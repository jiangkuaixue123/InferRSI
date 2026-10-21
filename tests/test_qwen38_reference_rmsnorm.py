"""Reference-policy contracts; optional real Torch CPU arithmetic, never GPU."""

import pytest

from examples.qwen38_text import reference_rmsnorm as policy
from examples.qwen38_text.validate import normalization_contract, validate_normalization_record


def config(layers=4):
    return {
        "model_type": "qwen3_5",
        "text_config": {
            "num_hidden_layers": layers,
            "hidden_size": 5120,
            "head_dim": 256,
            "num_attention_heads": 24,
            "num_key_value_heads": 4,
            "rms_norm_eps": 1e-6,
            "layer_types": [
                "full_attention" if i % 4 == 3 else "linear_attention" for i in range(layers)
            ],
        },
    }


def test_production_name_set_and_independent_validator_derivation():
    expected = policy.expected_modules(config(64))
    contract = normalization_contract(config(64), policy.digest(policy.__file__), "a" * 64)
    assert len(expected) == 161
    assert set(expected) == set(contract["modules"])
    assert expected["model.language_model.layers.3.self_attn.q_norm"]["width"] == 256
    assert "model.language_model.layers.0.linear_attn.norm" not in expected


@pytest.mark.parametrize(
    "change",
    [
        {"num_hidden_layers": True},
        {"layer_types": []},
        {"head_dim": 0},
        {"rms_norm_eps": float("nan")},
        {"rms_norm_eps": True},
    ],
)
def test_invalid_norm_configuration_rejected(change):
    document = config()
    document["text_config"].update(change)
    with pytest.raises(ValueError):
        policy.expected_modules(document)
    with pytest.raises(ValueError):
        normalization_contract(document, policy.digest(policy.__file__), "a" * 64)


def synthetic_record():
    contract = normalization_contract(config(), policy.digest(policy.__file__), "a" * 64)
    modules = [
        {
            "name": name,
            "width": width,
            "eps": contract["eps"],
            "weight_dtype": "bfloat16",
            "weight_sha256_fp32": "b" * 64,
            "calls": 2,
            "input_shapes": [[1, 7, width] if heads is None else [1, 7, heads, width]],
        }
        for name, (width, heads) in sorted(contract["modules"].items())
    ]
    record = {
        "reference_implementation": policy.LABEL,
        "reference_normalization": {
            **contract["identity"],
            "parameters_preserved": True,
            "state_keys_preserved": True,
            "modules": modules,
        },
    }
    return record, contract


@pytest.mark.parametrize(
    "change",
    [
        lambda r: r.pop("reference_normalization"),
        lambda r: r["reference_normalization"].update(policy="stock"),
        lambda r: r["reference_normalization"].update(version=2),
        lambda r: r["reference_normalization"].update(source_sha256="0" * 64),
        lambda r: r["reference_normalization"].update(modeling_source_sha256="0" * 64),
        lambda r: r["reference_normalization"].update(config_sha256="0" * 64),
        lambda r: r["reference_normalization"].update(parameters_preserved=False),
        lambda r: r["reference_normalization"]["modules"].pop(),
        lambda r: r["reference_normalization"]["modules"][0].update(name="wrong.same_count"),
        lambda r: r["reference_normalization"]["modules"][0].update(calls=0),
        lambda r: r["reference_normalization"]["modules"][0].update(input_shapes=[]),
        lambda r: r["reference_normalization"]["modules"][0].update(width=1),
        lambda r: r["reference_normalization"]["modules"][0].update(input_shapes=[[1, 7, 1]]),
    ],
)
def test_policy_evidence_missing_or_forged_rejected(change):
    record, contract = synthetic_record()
    validate_normalization_record(record, contract)
    change(record)
    with pytest.raises(ValueError):
        validate_normalization_record(record, contract)


def test_undeclared_policy_is_not_accepted_as_stock():
    record, _contract = synthetic_record()
    with pytest.raises(ValueError):
        validate_normalization_record(record, None)
    validate_normalization_record({}, None)


@pytest.fixture
def cpu_policy():
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    root = torch.nn.Module()
    for name, spec in policy.expected_modules(config()).items():
        parent = root
        for part in name.split(".")[:-1]:
            if not hasattr(parent, part):
                parent.add_module(part, torch.nn.Module())
            parent = getattr(parent, part)
        norm = modeling.Qwen3_5RMSNorm(spec["width"], spec["eps"]).to(torch.bfloat16)
        with torch.no_grad():
            norm.weight.copy_(torch.linspace(-0.25, 0.25, spec["width"], dtype=torch.bfloat16))
        parent.add_module(name.rsplit(".", 1)[1], norm)
    return torch, modeling, root


def test_replacement_retains_parameters_and_requires_all_modules_exercised(cpu_policy):
    torch, modeling, root = cpu_policy
    parameters, keys = dict(root.named_parameters()), set(root.state_dict())
    session = policy.install(
        root, config(), policy.digest(policy.__file__), policy.digest(modeling.__file__)
    )
    assert all(dict(root.named_parameters())[name] is value for name, value in parameters.items())
    assert set(root.state_dict()) == keys
    with pytest.raises(ValueError, match="execution"):
        session.check()
    for name, spec in policy.expected_modules(config()).items():
        root.get_submodule(name)(torch.zeros(1, 7, spec["width"], dtype=torch.bfloat16))
    record = session.check()
    assert len(record["modules"]) == len(policy.expected_modules(config()))
    first = next(iter(policy.expected_modules(config())))
    root.get_submodule(first).weight = torch.nn.Parameter(root.get_submodule(first).weight.clone())
    with pytest.raises(ValueError, match="parameter identity"):
        session.check()


@pytest.mark.parametrize("kind,heads", [("decoder", 1), ("q", 24), ("k", 4)])
def test_fixed_row_full_single_and_strided_chunk_shapes(cpu_policy, kind, heads):
    torch, modeling, root = cpu_policy
    policy.install(root, config(), policy.digest(policy.__file__), policy.digest(modeling.__file__))
    name = (
        "model.language_model.layers.0.input_layernorm"
        if kind == "decoder"
        else "model.language_model.layers.3.self_attn." + kind + "_norm"
    )
    module = root.get_submodule(name)
    width = module.weight.numel()
    generator = torch.Generator().manual_seed(71)
    shape = (1, 8, width) if kind == "decoder" else (1, 8, heads, 2 * width)
    raw = torch.randn(shape, generator=generator).to(torch.bfloat16)
    values = raw if kind == "decoder" else raw.chunk(2, dim=-1)[0]
    if kind != "decoder":
        assert not values.is_contiguous()  # Real Q projection chunk layout.
    values[:, 0] = 0
    values[:, 1] = torch.nextafter(torch.ones_like(values[:, 1]), torch.zeros_like(values[:, 1]))
    full = module(values)
    seven = module(values[:, :7])
    assert torch.equal(full[:, :7], seven)
    for position in range(8):
        assert torch.equal(
            full[:, position : position + 1], module(values[:, position : position + 1])
        )
    assert full.dtype == torch.bfloat16 and full.shape == values.shape
    assert torch.isfinite(full).all()
    # FP64 formula checks zero-centered weights on an exactly reduced input;
    # do not impose a campaign numeric error tolerance on general FP32 reductions.
    ones = torch.ones_like(values)
    golden = (
        ones.double()
        * torch.rsqrt(ones.double().square().mean(-1, keepdim=True) + module.eps)
        * (1.0 + module.weight.double())
    ).to(torch.bfloat16)
    assert torch.equal(module(ones), golden)


def test_normalized_values_stay_fp32_until_after_zero_centered_weight(cpu_policy):
    torch, modeling, root = cpu_policy
    policy.install(root, config(), policy.digest(policy.__file__), policy.digest(modeling.__file__))
    module = root.get_submodule("model.language_model.layers.0.input_layernorm")
    with torch.no_grad():
        module.weight.fill_(-0.4921875)  # Exactly representable in BF16.
    values = torch.tensor([1.0, 2.0], dtype=torch.bfloat16).repeat(2560).reshape(1, 1, 5120)
    normalized64 = values.double() * torch.rsqrt(
        values.double().square().mean(-1, keepdim=True) + module.eps
    )
    golden = (normalized64 * (1.0 + module.weight.double())).to(torch.bfloat16)
    premature = (
        normalized64.to(torch.bfloat16).float() * (1.0 + module.weight.float())
    ).to(torch.bfloat16)
    # This input straddles a BF16 rounding boundary only when the cast is early.
    assert golden[0, 0, 0].item() == 0.3203125
    assert premature[0, 0, 0].item() == 0.322265625
    assert not torch.equal(golden, premature)
    assert torch.equal(module(values), golden)


@pytest.mark.parametrize("mutation", ["forward", "hook", "wrong_type", "missing", "dtype"])
def test_install_rejects_unsupported_modules_without_partial_replacement(cpu_policy, mutation):
    torch, modeling, root = cpu_policy
    name = "model.language_model.layers.0.input_layernorm"
    module = root.get_submodule(name)
    if mutation == "forward":
        module.forward = lambda x: x
    elif mutation == "hook":
        module.register_forward_pre_hook(lambda m, a: None)
    elif mutation == "wrong_type":

        class Derived(modeling.Qwen3_5RMSNorm):
            pass

        root.get_submodule(name.rsplit(".", 1)[0]).input_layernorm = Derived(5120).to(
            torch.bfloat16
        )
    elif mutation == "missing":
        del root.get_submodule(name.rsplit(".", 1)[0]).input_layernorm
    else:
        module.float()
    before = dict(root.named_modules())
    with pytest.raises(ValueError):
        policy.install(
            root, config(), policy.digest(policy.__file__), policy.digest(modeling.__file__)
        )
    assert dict(root.named_modules()) == before
