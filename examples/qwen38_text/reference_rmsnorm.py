"""Explicit fixed-row reference policy; Torch is imported only when installing it.

The original Qwen3.5 zero-centered RMSNorm formula is preserved, with a fixed
FP32 pairwise reduction tree over the last dimension. This is a reference
harness policy, not an engine optimization or an edit to Transformers sources.
"""

import hashlib
import json
import math
import re
from pathlib import Path

POLICY = "fixed-pairwise-fp32-v1"
LABEL = "transformers_fp8_with_fixed_pairwise_fp32_rmsnorm"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_identity(config):
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def expected_modules(config):
    text = config["text_config"]
    layers, width, head = (text[key] for key in ("num_hidden_layers", "hidden_size", "head_dim"))
    eps, kinds = text["rms_norm_eps"], text["layer_types"]
    if (
        config.get("model_type") != "qwen3_5"
        or any(type(n) is not int or n <= 0 for n in (layers, width, head))
        or type(eps) not in (float, int)
        or not math.isfinite(eps)
        or eps <= 0
        or not isinstance(kinds, list)
        or len(kinds) != layers
        or any(kind not in ("linear_attention", "full_attention") for kind in kinds)
    ):
        raise ValueError("Invalid plain RMSNorm configuration")
    result = {"model.language_model.norm": {"width": width, "eps": eps}}
    for i, kind in enumerate(kinds):
        root = f"model.language_model.layers.{i}"
        for name in ("input_layernorm", "post_attention_layernorm"):
            result[root + "." + name] = {"width": width, "eps": eps}
        if kind == "full_attention":
            for name in ("q_norm", "k_norm"):
                result[root + ".self_attn." + name] = {"width": head, "eps": eps}
    return dict(sorted(result.items()))


def install(model, config, source_sha256, modeling_sha256):
    """Replace only authenticated text plain norms; preserve Parameter objects."""
    if any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
        for value in (source_sha256, modeling_sha256)
    ):
        raise ValueError("Reference norm policy requires frozen source fingerprints")
    if digest(__file__) != source_sha256:
        raise ValueError("Reference norm adapter differs from frozen source")
    import torch
    from transformers.models.qwen3_5 import modeling_qwen3_5 as modeling

    if digest(modeling.__file__) != modeling_sha256:
        raise ValueError("Original Transformers modeling source differs from frozen identity")
    expected = expected_modules(config)
    found = {
        name: module
        for name, module in model.named_modules()
        if name.startswith("model.language_model.") and isinstance(module, modeling.Qwen3_5RMSNorm)
    }
    if set(found) != set(expected):
        raise ValueError("Plain reference RMSNorm coverage differs from config")
    for name, module in found.items():
        if (
            type(module) is not modeling.Qwen3_5RMSNorm
            or list(module.weight.shape) != [expected[name]["width"]]
            or module.weight.dtype != torch.bfloat16
            or module.eps != expected[name]["eps"]
            or "forward" in vars(module)
            or hasattr(module, "_hf_hook")
            or module._forward_hooks
            or module._forward_pre_hooks
        ):
            raise ValueError("Unsupported reference norm parameters or hooks")

    class FixedPairwiseRMSNorm(torch.nn.Module):
        def __init__(self, original):
            super().__init__()
            self.weight = original.weight
            self.eps = original.eps
            self.train(original.training)
            self.calls = 0
            self.input_shapes = set()

        def forward(self, x):
            if x.dtype != torch.bfloat16 or x.ndim < 1 or x.shape[-1] != self.weight.numel():
                raise ValueError("Reference normalization input contract mismatch")
            self.calls += 1
            self.input_shapes.add(tuple(x.shape))
            width = x.shape[-1]
            rows = x.float().reshape(-1, width)
            terms = rows * rows
            padded = 1 << (width - 1).bit_length()
            if padded != width:
                terms = torch.nn.functional.pad(terms, (0, padded - width))
            while terms.shape[-1] > 1:
                terms = terms[:, 0::2] + terms[:, 1::2]
            variance = terms / width
            output = rows * torch.rsqrt(variance + self.eps)
            output = output * (1.0 + self.weight.float())
            return output.reshape(x.shape).to(x.dtype)

    session = PolicySession(
        model,
        config,
        expected,
        source_sha256,
        modeling_sha256,
        modeling,
        torch,
        FixedPairwiseRMSNorm,
    )
    for name, original in found.items():
        parent, child = name.rsplit(".", 1)
        setattr(model.get_submodule(parent), child, FixedPairwiseRMSNorm(original))
    session.check(require_calls=False)
    return session


class PolicySession:
    def __init__(self, model, config, expected, source, modeling_hash, modeling, torch, norm_type):
        self.model, self.expected, self.torch, self.norm_type = model, expected, torch, norm_type
        self.original_parameters = dict(model.named_parameters())
        self.parameter_contract = {
            name: (tuple(p.shape), p.dtype, p.device)
            for name, p in self.original_parameters.items()
        }
        self.state_keys = sorted(model.state_dict())
        self.weight_hashes = {
            name: self.weight_hash(model.get_submodule(name).weight) for name in expected
        }
        self.modeling = modeling
        self.forward = norm_type.forward
        self.identity = {
            "policy": POLICY,
            "version": 1,
            "scope": "all_text_plain_rmsnorm",
            "label": LABEL,
            "source_sha256": source,
            "adapter_import": {
                "path": "examples/qwen38_text/reference_rmsnorm.py",
                "sha256": source,
            },
            "modeling_source_sha256": modeling_hash,
            "config_sha256": config_identity(config),
            "reduction": "last_dim_fixed_pairwise_elementwise_add_fp32",
            "materialization": "original_bfloat16_after_zero_centered_weight",
        }

    def weight_hash(self, weight):
        # BF16 -> FP32 is lossless; encode values portably for unchanged-weight evidence.
        data = weight.detach().float().cpu().contiguous().numpy().astype("<f4", copy=False)
        return hashlib.sha256(data.tobytes()).hexdigest()

    def check(self, require_calls=True):
        if (
            digest(__file__) != self.identity["source_sha256"]
            or digest(self.modeling.__file__) != self.identity["modeling_source_sha256"]
        ):
            raise ValueError("Reference normalization sources changed")
        parameters = dict(self.model.named_parameters())
        if (
            set(parameters) != set(self.original_parameters)
            or sorted(self.model.state_dict()) != self.state_keys
            or any(
                parameters[name] is not original
                or (tuple(original.shape), original.dtype, original.device)
                != self.parameter_contract[name]
                for name, original in self.original_parameters.items()
            )
        ):
            raise ValueError("Reference normalization changed checkpoint parameter identity")
        found = {
            name: module
            for name, module in self.model.named_modules()
            if isinstance(module, self.norm_type)
        }
        if set(found) != set(self.expected):
            raise ValueError("Reference normalization replacement coverage changed")
        records = []
        for name, module in sorted(found.items()):
            if (
                type(module) is not self.norm_type
                or module.forward.__func__ is not self.forward
                or "forward" in vars(module)
                or module._forward_hooks
                or module._forward_pre_hooks
                or hasattr(module, "_hf_hook")
                or module.eps != self.expected[name]["eps"]
                or self.weight_hash(module.weight) != self.weight_hashes[name]
                or require_calls
                and module.calls <= 0
            ):
                raise ValueError("Reference normalization execution or weight identity mismatch")
            records.append(
                {
                    "name": name,
                    **self.expected[name],
                    "weight_dtype": "bfloat16",
                    "weight_sha256_fp32": self.weight_hashes[name],
                    "calls": module.calls,
                    "input_shapes": [list(shape) for shape in sorted(module.input_shapes)],
                }
            )
        return {
            **self.identity,
            "parameters_preserved": True,
            "state_keys_preserved": True,
            "modules": records,
        }
