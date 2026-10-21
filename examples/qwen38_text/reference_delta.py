"""Explicit reference-only canonical recurrence policy; no Transformers edits."""

import inspect
import re
from pathlib import Path

if __package__:
    from .reference_rmsnorm import config_identity, digest
else:
    from reference_rmsnorm import config_identity, digest

POLICY = "canonical-recurrent-fp32-v1"
LABEL = "transformers_fp8_with_fixed_pairwise_fp32_rmsnorm_and_canonical_recurrent_delta"


def canonical_chunk_call(
    original_recurrent,
    query,
    key,
    value,
    g,
    beta,
    chunk_size=64,
    initial_state=None,
    output_final_state=False,
    use_qk_l2norm_in_kernel=False,
    **kwargs,
):
    """Forward original chunk semantics to the unchanged pinned recurrence body."""
    if type(chunk_size) is not int or chunk_size != 64:
        raise ValueError("Unsupported reference Delta chunk size")
    return original_recurrent(
        query,
        key,
        value,
        g=g,
        beta=beta,
        initial_state=initial_state,
        output_final_state=output_final_state,
        use_qk_l2norm_in_kernel=use_qk_l2norm_in_kernel,
        **kwargs,
    )


def expected_modules(config):
    text = config["text_config"]
    fields = {
        "hidden_size": "hidden_size",
        "num_k_heads": "linear_num_key_heads",
        "num_v_heads": "linear_num_value_heads",
        "head_k_dim": "linear_key_head_dim",
        "head_v_dim": "linear_value_head_dim",
        "conv_kernel_size": "linear_conv_kernel_dim",
    }
    dimensions = {name: text[key] for name, key in fields.items()}
    kinds, count = text["layer_types"], text["num_hidden_layers"]
    if (
        config.get("model_type") != "qwen3_5"
        or type(count) is not int
        or count <= 0
        or not isinstance(kinds, list)
        or len(kinds) != count
        or any(kind not in ("linear_attention", "full_attention") for kind in kinds)
        or any(type(value) is not int or value <= 0 for value in dimensions.values())
    ):
        raise ValueError("Invalid reference Delta configuration")
    return {
        f"model.language_model.layers.{i}.linear_attn": {"layer_idx": i, **dimensions}
        for i, kind in enumerate(kinds)
        if kind == "linear_attention"
    }


def install(model, config, source_sha256, modeling_sha256):
    if (
        any(
            not isinstance(x, str) or not re.fullmatch(r"[0-9a-f]{64}", x)
            for x in (source_sha256, modeling_sha256)
        )
        or digest(__file__) != source_sha256
    ):
        raise ValueError("Reference Delta requires its frozen adapter identity")
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    if digest(modeling.__file__) != modeling_sha256:
        raise ValueError("Reference Delta modeling source mismatch")
    forward = inspect.unwrap(modeling.Qwen3_5GatedDeltaNet.forward)
    if (
        forward.__name__ != "forward"
        or forward.__qualname__ != "Qwen3_5GatedDeltaNet.forward"
        or Path(forward.__code__.co_filename).resolve() != Path(modeling.__file__).resolve()
    ):
        raise ValueError("Unexpected reference Delta class forward replacement")
    for name in ("torch_chunk_gated_delta_rule", "torch_recurrent_gated_delta_rule", "l2norm"):
        function = inspect.unwrap(getattr(modeling, name))
        if (
            function.__name__ != name
            or Path(function.__code__.co_filename).resolve() != Path(modeling.__file__).resolve()
        ):
            raise ValueError("Unexpected reference Delta function replacement")
    expected = expected_modules(config)
    found = {
        name: module
        for name, module in model.named_modules()
        if name.startswith("model.language_model.")
        and isinstance(module, modeling.Qwen3_5GatedDeltaNet)
    }
    if not expected or set(found) != set(expected):
        raise ValueError("Reference Delta module coverage mismatch")
    for name, module in found.items():
        if (
            type(module) is not modeling.Qwen3_5GatedDeltaNet
            or "forward" in vars(module)
            or hasattr(module, "_hf_hook")
            or module._forward_hooks
            or module._forward_pre_hooks
            or any(getattr(module, key) != value for key, value in expected[name].items())
        ):
            raise ValueError("Unexpected reference Delta module, dimensions or hooks")
    session = PolicySession(
        model, config, expected, found, source_sha256, modeling_sha256, modeling
    )
    try:
        session.bind()
        session.check(require_calls=False)
    except BaseException:
        session.close()
        raise
    return session


class PolicySession:
    def __init__(self, model, config, expected, modules, source, modeling_hash, modeling):
        self.model, self.expected, self.modules, self.modeling = model, expected, modules, modeling
        self.chunk = modeling.torch_chunk_gated_delta_rule
        self.recurrent = modeling.torch_recurrent_gated_delta_rule
        self.l2norm = modeling.l2norm
        self.forward = modeling.Qwen3_5GatedDeltaNet.forward
        self.parameters = dict(model.named_parameters())
        self.parameter_contract = {
            name: (tuple(p.shape), p.dtype, p.device) for name, p in self.parameters.items()
        }
        self.state_keys = sorted(model.state_dict())
        self.records = {
            name: {
                "calls": 0,
                "redirected_chunk_calls": 0,
                "direct_recurrent_calls": 0,
                "input_shapes": set(),
            }
            for name in modules
        }
        self.active, self.failed, self.closed = None, False, False
        self.handles, self.hooks = [], {}
        self.identity = {
            "policy": POLICY,
            "version": 1,
            "scope": "all_text_linear_attention",
            "label": LABEL,
            "source_sha256": source,
            "adapter_import": {"path": "examples/qwen38_text/reference_delta.py", "sha256": source},
            "modeling_source_sha256": modeling_hash,
            "config_sha256": config_identity(config),
            "execution": "original_recurrent_for_chunk_and_incremental_calls",
            "original_recurrent_unchanged": True,
        }

    def bind(self):
        def dispatch(*args, **kwargs):
            if self.active is None or not self.active["redirect"] or self.active["seen"]:
                raise ValueError("Unowned or repeated reference chunk call")
            self.active["seen"] = True
            return canonical_chunk_call(self.recurrent, *args, **kwargs)

        self.dispatch = dispatch
        for name, module in self.modules.items():

            def before(mod, args, kwargs, name=name):
                if self.closed or self.active is not None:
                    raise ValueError("Concurrent or nested reference Delta call")
                hidden = args[0] if args else kwargs.get("hidden_states")
                if (
                    hidden is None
                    or hidden.ndim != 3
                    or hidden.shape[0] != 1
                    or hidden.shape[1] <= 0
                ):
                    raise ValueError("Reference Delta requires one nonempty text request")
                cache = kwargs.get("cache_params", args[1] if len(args) > 1 else None)
                previous = cache is not None and cache.has_previous_state(
                    mod.layer_idx, state_idx=0
                )
                self.active = {
                    "name": name,
                    "redirect": not (previous and hidden.shape[1] == 1),
                    "seen": False,
                }
                self.records[name]["input_shapes"].add(tuple(hidden.shape))

            def after(mod, args, kwargs, output, name=name):
                active, self.active = self.active, None
                if output is None:
                    self.failed = True
                    return
                if active is None or active["name"] != name or active["seen"] != active["redirect"]:
                    self.failed = True
                    raise ValueError("Reference Delta execution branch mismatch")
                record = self.records[name]
                record["calls"] += 1
                record[
                    "redirected_chunk_calls" if active["redirect"] else "direct_recurrent_calls"
                ] += 1

            pre = module.register_forward_pre_hook(before, with_kwargs=True)
            post = module.register_forward_hook(after, with_kwargs=True, always_call=True)
            self.handles.extend((pre, post))
            self.hooks[name] = (pre.id, before, post.id, after)
        self.modeling.torch_chunk_gated_delta_rule = self.dispatch

    def check(self, require_calls=True):
        if (
            self.closed
            or self.failed
            or self.active is not None
            or digest(__file__) != self.identity["source_sha256"]
            or digest(self.modeling.__file__) != self.identity["modeling_source_sha256"]
            or self.modeling.torch_chunk_gated_delta_rule is not self.dispatch
            or self.modeling.torch_recurrent_gated_delta_rule is not self.recurrent
            or self.modeling.l2norm is not self.l2norm
        ):
            raise ValueError("Reference Delta policy identity or execution changed")
        params = dict(self.model.named_parameters())
        if (
            set(params) != set(self.parameters)
            or sorted(self.model.state_dict()) != self.state_keys
            or any(
                params[name] is not p
                or (tuple(p.shape), p.dtype, p.device) != self.parameter_contract[name]
                for name, p in self.parameters.items()
            )
        ):
            raise ValueError("Reference Delta changed checkpoint parameter/state identity")
        records = []
        found = {
            name for name, module in self.model.named_modules()
            if name.startswith("model.language_model.")
            and isinstance(module, self.modeling.Qwen3_5GatedDeltaNet)
        }
        if found != set(self.expected):
            raise ValueError("Reference Delta complete module coverage changed")
        for name, module in self.modules.items():
            pre_id, before, post_id, after = self.hooks[name]
            record = self.records[name]
            if (
                self.model.get_submodule(name) is not module
                or type(module) is not self.modeling.Qwen3_5GatedDeltaNet
                or module.forward.__func__ is not self.forward
                or "forward" in vars(module)
                or hasattr(module, "_hf_hook")
                or dict(module._forward_pre_hooks) != {pre_id: before}
                or dict(module._forward_hooks) != {post_id: after}
                or any(getattr(module, key) != value for key, value in self.expected[name].items())
                or require_calls
                and record["calls"] <= 0
            ):
                raise ValueError("Reference Delta module or execution coverage changed")
            records.append(
                {
                    "name": name,
                    **self.expected[name],
                    **record,
                    "input_shapes": [list(s) for s in sorted(record["input_shapes"])],
                }
            )
        return {
            **self.identity,
            "parameters_preserved": True,
            "state_keys_preserved": True,
            "modules": records,
        }

    def close(self):
        if self.closed:
            return
        if getattr(self, "dispatch", None) is self.modeling.torch_chunk_gated_delta_rule:
            self.modeling.torch_chunk_gated_delta_rule = self.chunk
        for handle in self.handles:
            handle.remove()
        self.handles.clear()
        self.closed = True
