"""Reference Delta contract tests; Torch cases are CPU-only, never campaign PASS."""

import copy

import pytest

from examples.qwen38_text import reference_delta as policy
from examples.qwen38_text.validate import delta_contract, validate_delta_record


def config(layers=64):
    return {
        "model_type": "qwen3_5",
        "text_config": {
            "num_hidden_layers": layers,
            "hidden_size": 8,
            "linear_num_key_heads": 1,
            "linear_num_value_heads": 3,
            "linear_key_head_dim": 4,
            "linear_value_head_dim": 4,
            "linear_conv_kernel_dim": 4,
            "layer_types": [
                "full_attention" if i % 4 == 3 else "linear_attention" for i in range(layers)
            ],
        },
    }


def test_complete_module_set_independently_derived():
    expected = policy.expected_modules(config())
    contract = delta_contract(config(), policy.digest(policy.__file__), "a" * 64)
    assert len(expected) == 48 and expected == contract["modules"]


@pytest.mark.parametrize("initial", [False, True])
@pytest.mark.parametrize("final", [False, True])
@pytest.mark.parametrize("normalize", [False, True])
def test_thin_call_preserves_every_argument_and_original_return(initial, final, normalize):
    values = [object() for _ in range(5)]
    state = object() if initial else None
    marker, result = object(), object()
    seen = []

    def original(*args, **kwargs):
        seen.append((args, kwargs))
        return result

    assert (
        policy.canonical_chunk_call(
            original,
            *values,
            initial_state=state,
            output_final_state=final,
            use_qk_l2norm_in_kernel=normalize,
            cu_seqlens=marker,
        )
        is result
    )
    assert seen == [
        (
            tuple(values[:3]),
            {
                "g": values[3],
                "beta": values[4],
                "initial_state": state,
                "output_final_state": final,
                "use_qk_l2norm_in_kernel": normalize,
                "cu_seqlens": marker,
            },
        )
    ]
    with pytest.raises(ValueError, match="chunk size"):
        policy.canonical_chunk_call(original, *values, chunk_size=32)


def synthetic_record(mode="transformers_full"):
    contract = delta_contract(config(4), policy.digest(policy.__file__), "a" * 64)
    redirected = 3 if mode == "transformers_full" else 1
    record = {
        "implementation": mode,
        "reference_implementation": policy.LABEL,
        "reference_delta": {
            **contract["identity"],
            "parameters_preserved": True,
            "state_keys_preserved": True,
            "modules": [
                {
                    "name": name,
                    **dimensions,
                    "calls": 3,
                    "redirected_chunk_calls": redirected,
                    "direct_recurrent_calls": 3 - redirected,
                    "input_shapes": [[1, 2, 8]],
                }
                for name, dimensions in contract["modules"].items()
            ],
        },
    }
    return record, contract


@pytest.mark.parametrize("mode", ["transformers_full", "transformers_cached"])
def test_reference_role_and_exact_calls(mode):
    record, contract = synthetic_record(mode)
    validate_delta_record(record, contract, [{"max_steps": 3}])
    with pytest.raises(ValueError, match="Undeclared"):
        validate_delta_record(record, None, [{"max_steps": 3}])


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.pop("reference_delta"),
        lambda r: r.update(reference_implementation="stock"),
        lambda r: r["reference_delta"].update(policy="stock"),
        lambda r: r["reference_delta"].update(original_recurrent_unchanged=False),
        lambda r: r["reference_delta"].update(source_sha256="0" * 64),
        lambda r: r["reference_delta"].update(parameters_preserved=False),
        lambda r: r["reference_delta"]["modules"].pop(),
        lambda r: r["reference_delta"]["modules"][0].update(name="same_count_wrong_name"),
        lambda r: r["reference_delta"]["modules"][0].update(calls=2),
        lambda r: r["reference_delta"]["modules"][0].update(redirected_chunk_calls=0),
        lambda r: r["reference_delta"]["modules"][0].update(head_k_dim=8),
        lambda r: r["reference_delta"]["modules"][0].update(input_shapes=[]),
    ],
)
def test_forged_or_missing_policy_rejected(mutate):
    record, contract = synthetic_record()
    mutate(record)
    with pytest.raises((ValueError, TypeError)):
        validate_delta_record(record, contract, [{"max_steps": 3}])


@pytest.mark.parametrize(
    "initial,final,normalize",
    [(a, b, c) for a in (False, True) for b in (False, True) for c in (False, True)],
)
def test_real_original_recurrent_cpu_semantics(initial, final, normalize):
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    generator = torch.Generator().manual_seed(71)
    q, k, v = [torch.randn(1, 3, 3, 4, generator=generator).to(torch.bfloat16) for _ in range(3)]
    g = -torch.rand(1, 3, 3, generator=generator)
    beta = torch.rand(1, 3, 3, generator=generator)
    state = torch.randn(1, 3, 4, 4, generator=generator) if initial else None
    originals = [x.clone() for x in (q, k, v, g, beta)]
    saved = None if state is None else state.clone()
    kwargs = {
        "g": g,
        "beta": beta,
        "initial_state": state,
        "output_final_state": final,
        "use_qk_l2norm_in_kernel": normalize,
    }
    expected = modeling.torch_recurrent_gated_delta_rule(q, k, v, **kwargs)
    actual = policy.canonical_chunk_call(
        modeling.torch_recurrent_gated_delta_rule, q, k, v, **kwargs
    )
    assert torch.equal(expected[0], actual[0])
    assert (actual[1] is None) == (not final)
    if final:
        assert torch.equal(expected[1], actual[1])
    assert all(torch.equal(x, y) for x, y in zip((q, k, v, g, beta), originals))
    assert state is None or torch.equal(state, saved)


def make_tree(torch, modeling, document, device):
    text = copy.deepcopy(document["text_config"])
    text.update(hidden_act="silu", rms_norm_eps=1e-6)
    from types import SimpleNamespace

    root = torch.nn.Module()
    for name, spec in policy.expected_modules(document).items():
        parent = root
        for part in name.split(".")[:-1]:
            if not hasattr(parent, part):
                parent.add_module(part, torch.nn.Module())
            parent = getattr(parent, part)
        with torch.device(device):
            module = modeling.Qwen3_5GatedDeltaNet(SimpleNamespace(**text), spec["layer_idx"])
        parent.add_module(name.rsplit(".", 1)[1], module.to(dtype=torch.bfloat16))
    return root


def test_meta_full_set_bind_restore_and_no_false_execution_claim():
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    root = make_tree(torch, modeling, config(), "meta")
    chunk, recurrent = (
        modeling.torch_chunk_gated_delta_rule,
        modeling.torch_recurrent_gated_delta_rule,
    )
    session = policy.install(
        root, config(), policy.digest(policy.__file__), policy.digest(modeling.__file__)
    )
    try:
        assert len(session.check(require_calls=False)["modules"]) == 48
        assert modeling.torch_recurrent_gated_delta_rule is recurrent
        with pytest.raises(ValueError, match="coverage"):
            session.check()
    finally:
        session.close()
    session.close()
    assert modeling.torch_chunk_gated_delta_rule is chunk
    assert all(not m._forward_hooks and not m._forward_pre_hooks for m in session.modules.values())


def test_preexisting_class_forward_replacement_rejected(monkeypatch):
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    root = make_tree(torch, modeling, config(1), "meta")
    chunk = modeling.torch_chunk_gated_delta_rule
    monkeypatch.setattr(modeling.Qwen3_5GatedDeltaNet, "forward", lambda self, hidden: hidden)
    with pytest.raises(ValueError, match="class forward"):
        policy.install(
            root, config(1), policy.digest(policy.__file__), policy.digest(modeling.__file__)
        )
    assert modeling.torch_chunk_gated_delta_rule is chunk


def test_real_module_cpu_branch_counts_and_parameter_guard():
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    root = make_tree(torch, modeling, config(1), "cpu")
    session = policy.install(
        root, config(1), policy.digest(policy.__file__), policy.digest(modeling.__file__)
    )
    try:
        module = root.get_submodule(next(iter(policy.expected_modules(config(1)))))
        module(torch.zeros(1, 2, 8, dtype=torch.bfloat16))
        from transformers.models.qwen3_5.configuration_qwen3_5 import Qwen3_5TextConfig

        cache = modeling.DynamicCache(config=Qwen3_5TextConfig(**config(1)["text_config"]))
        module(torch.zeros(1, 2, 8, dtype=torch.bfloat16), cache_params=cache)
        module(torch.zeros(1, 1, 8, dtype=torch.bfloat16), cache_params=cache)
        record = session.check()["modules"][0]
        assert (
            record["calls"],
            record["redirected_chunk_calls"],
            record["direct_recurrent_calls"],
        ) == (3, 2, 1)
        module.dt_bias = torch.nn.Parameter(module.dt_bias.clone())
        with pytest.raises(ValueError, match="parameter"):
            session.check()
    finally:
        session.close()
