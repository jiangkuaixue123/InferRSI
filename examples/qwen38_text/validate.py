"""Validate scoped text traces; missing evidence exits 2, numeric rejection 1.

Reference self-check is the default; native smoke requires distinct source and
implementation evidence. Neither scope establishes general quality/performance.
"""

import argparse
import copy
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

if __package__:
    from .profiles import (
        BF16_MODEL_ID,
        FP8_MODEL_ID,
        MODEL_IDS,
        check_precision,
        validate_config,
        validate_native_loading,
    )
else:
    from profiles import (
        BF16_MODEL_ID,
        FP8_MODEL_ID,
        MODEL_IDS,
        check_precision,
        validate_config,
        validate_native_loading,
    )


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def require_object(value):
    if not isinstance(value, dict):
        raise ValueError("evidence field must be a JSON object")
    return value


def require_string(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("evidence field must be a nonempty string")
    return value


def require_digest(value, pattern=r"[0-9a-f]{64}"):
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise ValueError("missing or malformed source digest")
    return value


def source_identity(value, *, available=False):
    value = require_object(value)
    # Git supports SHA-1 and SHA-256 object IDs; snapshot digests are SHA-256.
    require_digest(value.get("head"), r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
    require_digest(value.get("snapshot_hash"))
    if available and value.get("available") is not True:
        raise ValueError("source snapshot unavailable")
    return value


def local_file(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("artifact must use a relative path")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("artifact missing or escapes its trial")
    return path


def token_ids(value):
    return isinstance(value, list) and bool(value) and all(
        type(item) is int and item >= 0 for item in value
    )


REFERENCE_POLICY = {"hub_kernels": False, "full_attention": "eager",
                    "optional_modules": {"fla": False, "causal_conv1d": False}}
NATIVE_POLICY = {"implementation": "native_torch", "full_attention": "eager",
                 "deltanet": "torch", "cuda_graph": False, "tensor_parallel_size": 1}


def validate_sources(record, spec, locked, root, side, model_id=BF16_MODEL_ID):
    sources = require_object(record.get("source_provenance"))
    required = {"control"} if side == "baseline" else {"control", "engine"}
    if set(sources) != required:
        raise ValueError("missing or extra source provenance")
    for label in required:
        target = "baseline" if label == "control" else "candidate"
        identity = source_identity(locked.get(target), available=True)
        source = source_identity(sources[label])
        if any(
            source.get(key) != identity.get(key) for key in ("head", "snapshot_hash")
        ):
            raise ValueError("trial source identity differs from frozen checkout")
        source_root = Path(spec["repo"] if label == "control" else spec["candidate_repo"])
        imports = require_object(source.get("imports"))
        required_modules = {"inferrsi", "inferrsi.infra.targets.git"} if label == "control" else {
            "nanovllm", "nanovllm.qwen38.loader", "nanovllm.qwen38.runner", "nanovllm.qwen38.model",
        }
        if label == "engine" and model_id == FP8_MODEL_ID:
            required_modules |= {"nanovllm.qwen38.quant", "nanovllm.qwen38._triton_fp8"}
        if not required_modules <= set(imports):
            raise ValueError("required source import origins missing")
        prefix = "inferrsi" if label == "control" else "nanovllm"
        for name, imported in imports.items():
            require_string(name)
            imported = require_object(imported)
            require_digest(imported.get("sha256"))
            if name != prefix and not name.startswith(prefix + "."):
                raise ValueError("unexpected import provenance namespace")
            path = local_file(source_root, imported.get("path"))
            if digest(path) != imported["sha256"]:
                raise ValueError("imported source file changed or has wrong digest")
    if side == "candidate" and record.get("native_model_module") != "nanovllm.qwen38.model":
        raise ValueError("candidate model is not the native engine class")
    if side == "candidate":
        validate_native_loading(record.get("loading"), model_id)
        if model_id == FP8_MODEL_ID:
            execution = require_object(record.get("fp8_execution"))
            count = record["loading"]["fp8_linear_modules"]
            if (type(execution.get("modules")) is not int or execution["modules"] != count
                    or type(execution.get("total_calls")) is not int
                    or execution["total_calls"] < count):
                raise ValueError("Native FP8 execution evidence incomplete")
    source_check = read_json(root / "source.json")
    if source_check.get("side") != side:
        raise ValueError("trial source check has wrong role")
    for stage in ("before", "after"):
        checked = source_identity(source_check.get(stage), available=True)
        if any(
            checked[key] != locked[side][key]
            for key in ("head", "snapshot_hash")
        ):
            raise ValueError("trial source changed during execution")


def validate_reference_kernel(record, revision, snapshot):
    kernel = require_object(record.get("reference_kernel"))
    if (kernel.get("repo_id") != "kernels-community/finegrained-fp8"
            or kernel.get("repo_type") != "kernel"
            or kernel.get("revision") != revision or kernel.get("snapshot_sha256") != snapshot):
        raise ValueError("Reference kernel differs from frozen provenance")
    package_root = require_string(kernel.get("package_root"))
    if (kernel.get("build") != "torch-cuda" or not Path(package_root).is_absolute()
            or Path(package_root).name != "torch-cuda"):
        raise ValueError("Reference kernel build origin missing")
    files = kernel.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Reference kernel file coverage missing")
    names = set()
    for item in files:
        require_object(item)
        name = require_string(item.get("path"))
        if Path(name).is_absolute() or ".." in Path(name).parts or name in names:
            raise ValueError("Invalid reference kernel file identity")
        names.add(name)
        require_digest(item.get("sha256"))
    observed = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    if observed != snapshot:
        raise ValueError("Reference kernel fingerprint mismatch")
    loading = require_object(record.get("fp8_loading"))
    expected = {"execution": "transformers_fp8", "dequantized": False,
                "backend": "finegrained_fp8", "weight_dtype": "float8_e4m3fn",
                "activation_dtype": "bfloat16", "scale_dtype": "float32",
                "scale_normalization": "lossless_float32"}
    if (loading.get("dequantized") is not False
            or any(loading.get(key) != value for key, value in expected.items())
            or type(loading.get("fp8_linear_modules")) is not int
            or loading["fp8_linear_modules"] <= 0
            or type(loading.get("bf16_scale_upcasts")) is not int
            or not 0 <= loading["bf16_scale_upcasts"] <= loading["fp8_linear_modules"]):
        raise ValueError("Reference FP8 execution coverage missing or dequantized")
    return kernel


def authenticated_reference_metadata(model_path, manifest):
    """Independently derive identities from frozen-manifest-authenticated metadata."""
    if model_path is None:
        raise ValueError("FP8 validation requires checkpoint metadata")
    if __package__:
        from .trial import model_file
    else:
        from trial import model_file
    entries = {}
    for entry in manifest["files"]:
        if entry["path"] in entries:
            raise ValueError("Duplicate manifest identity")
        entries[entry["path"]] = entry
    metadata = {}
    for name in ("config.json", "model.safetensors.index.json"):
        path = model_file(Path(model_path), name)
        item = entries[name]
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != item["sha256"] or len(payload) != item["size"]:
            raise ValueError("Reference metadata differs from frozen manifest")
        metadata[name] = require_object(json.loads(payload))
    return metadata


def reference_adaptation_contract(model_path, manifest):
    metadata = authenticated_reference_metadata(model_path, manifest)
    config = metadata["config.json"]
    validate_config(config, FP8_MODEL_ID)
    weights = require_object(metadata["model.safetensors.index.json"]["weight_map"])
    if any(not isinstance(key, str) or not isinstance(value, str)
           for key, value in weights.items()):
        raise ValueError("Reference weight index is invalid")
    suffix = ".weight_scale_inv"
    names = sorted(name[:-len(suffix)] for name in weights
                   if name.startswith("model.language_model.layers.") and name.endswith(suffix))
    if not names or any(name + ".weight" not in weights for name in names):
        raise ValueError("Reference metadata lacks FP8 pairs")
    layers = config["text_config"]["num_hidden_layers"]
    if type(layers) is not int or layers <= 0:
        raise ValueError("Reference metadata layer count invalid")
    aliases = [f"model.language_model.layers.{layer}.mlp.gate" for layer in range(layers)]
    skip = config["quantization_config"]["modules_to_not_convert"]
    if (not isinstance(skip, list) or any(not isinstance(name, str) for name in skip)
            or any(skip.count(alias) != 1 or alias + "_proj" not in names for alias in aliases)):
        raise ValueError("Reference metadata gate alias mismatch")
    adapted = copy.deepcopy(config)
    adapted["quantization_config"]["modules_to_not_convert"] = [
        name for name in skip if name not in aliases]
    def identity(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                         allow_nan=False).encode()).hexdigest()
    return {"policy": "remove_nonexistent_dense_gate_aliases", "version": 1,
            "original_config_sha256": identity(config), "adapted_config_sha256": identity(adapted),
            "config_identity_encoding": "sorted_compact_json_utf8",
            "removed_exclusions": aliases, "expected_fp8_modules": names}


def validate_adaptation_record(loading, contract):
    if (loading.get("config_adaptation") != contract
            or loading.get("fp8_module_names") != contract["expected_fp8_modules"]
            or loading.get("fp8_linear_modules") != len(contract["expected_fp8_modules"])):
        raise ValueError("Reference adaptation/module identity differs from authenticated metadata")


def normalization_contract(config, source_sha256, modeling_sha256):
    """Validator-side derivation; never use adapter output as the module oracle."""
    require_digest(source_sha256)
    require_digest(modeling_sha256)
    adapter = Path(__file__).with_name("reference_rmsnorm.py")
    if hashlib.sha256(adapter.read_bytes()).hexdigest() != source_sha256:
        raise ValueError("Frozen reference normalization source mismatch")
    text = require_object(config.get("text_config"))
    layers = text.get("num_hidden_layers")
    width, head = text.get("hidden_size"), text.get("head_dim")
    heads, kv_heads = text.get("num_attention_heads"), text.get("num_key_value_heads")
    eps, kinds = text.get("rms_norm_eps"), text.get("layer_types")
    if (config.get("model_type") != "qwen3_5"
            or any(type(n) is not int or n <= 0 for n in (layers, width, head, heads, kv_heads))
            or type(eps) not in (int, float) or not math.isfinite(eps) or eps <= 0
            or not isinstance(kinds, list) or len(kinds) != layers
            or any(kind not in ("linear_attention", "full_attention") for kind in kinds)):
        raise ValueError("Invalid normalization metadata")
    expected = {"model.language_model.norm": (width, None)}
    for index, kind in enumerate(kinds):
        prefix = f"model.language_model.layers.{index}"
        expected[prefix + ".input_layernorm"] = (width, None)
        expected[prefix + ".post_attention_layernorm"] = (width, None)
        if kind == "full_attention":
            expected[prefix + ".self_attn.q_norm"] = (head, heads)
            expected[prefix + ".self_attn.k_norm"] = (head, kv_heads)
    identity = hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":"),
                                         allow_nan=False).encode()).hexdigest()
    return {"identity": {"policy": "fixed-pairwise-fp32-v1", "version": 1,
                         "scope": "all_text_plain_rmsnorm",
                         "label": "transformers_fp8_with_fixed_pairwise_fp32_rmsnorm",
                         "source_sha256": source_sha256, "modeling_source_sha256": modeling_sha256,
                         "adapter_import": {"path": "examples/qwen38_text/reference_rmsnorm.py",
                                            "sha256": source_sha256},
                         "config_sha256": identity,
                         "reduction": "last_dim_fixed_pairwise_elementwise_add_fp32",
                         "materialization": "original_bfloat16_after_zero_centered_weight"},
            "modules": expected, "eps": eps}


def validate_normalization_record(record, contract, implementation_label=None):
    if contract is None:
        if "reference_normalization" in record or "reference_implementation" in record:
            raise ValueError("Undeclared reference normalization policy")
        return
    policy = require_object(record.get("reference_normalization"))
    if (type(policy.get("version")) is not int
            or any(policy.get(key) != value for key, value in contract["identity"].items())
            or record.get("reference_implementation") != (
                implementation_label or contract["identity"]["label"])
            or policy.get("parameters_preserved") is not True
            or policy.get("state_keys_preserved") is not True):
        raise ValueError("Reference normalization policy identity mismatch")
    modules = policy.get("modules")
    if not isinstance(modules, list) or len(modules) != len(contract["modules"]):
        raise ValueError("Reference normalization module coverage missing")
    seen = set()
    for module in modules:
        require_object(module)
        name = require_string(module.get("name"))
        if name in seen or name not in contract["modules"]:
            raise ValueError("Reference normalization module set mismatch")
        seen.add(name)
        width, heads = contract["modules"][name]
        if (type(module.get("width")) is not int or module["width"] != width
                or type(module.get("eps")) not in (int, float) or module["eps"] != contract["eps"]
                or module.get("weight_dtype") != "bfloat16"
                or type(module.get("calls")) is not int or module["calls"] <= 0):
            raise ValueError("Reference normalization module execution mismatch")
        require_digest(module.get("weight_sha256_fp32"))
        shapes = module.get("input_shapes")
        if not isinstance(shapes, list) or not shapes:
            raise ValueError("Reference normalization input shape evidence missing")
        for shape in shapes:
            if (not isinstance(shape, list) or any(type(n) is not int or n <= 0 for n in shape)
                    or len(shape) != (3 if heads is None else 4)
                    or shape[0] != 1 or shape[-1] != width
                    or heads is not None and shape[-2] != heads):
                raise ValueError("Reference normalization input shape mismatch")


def delta_contract(config, source_sha256, modeling_sha256):
    """Derive complete linear module identities independently from authenticated config."""
    require_digest(source_sha256)
    require_digest(modeling_sha256)
    if digest(Path(__file__).with_name("reference_delta.py")) != source_sha256:
        raise ValueError("Frozen reference Delta source mismatch")
    text = require_object(config.get("text_config"))
    count, kinds = text.get("num_hidden_layers"), text.get("layer_types")
    fields = {"hidden_size": "hidden_size", "num_k_heads": "linear_num_key_heads",
              "num_v_heads": "linear_num_value_heads", "head_k_dim": "linear_key_head_dim",
              "head_v_dim": "linear_value_head_dim", "conv_kernel_size": "linear_conv_kernel_dim"}
    dimensions = {name: text.get(key) for name, key in fields.items()}
    if (config.get("model_type") != "qwen3_5" or type(count) is not int or count <= 0
            or not isinstance(kinds, list) or len(kinds) != count
            or any(kind not in ("linear_attention", "full_attention") for kind in kinds)
            or any(type(x) is not int or x <= 0 for x in dimensions.values())):
        raise ValueError("Invalid reference Delta metadata")
    modules = {f"model.language_model.layers.{i}.linear_attn": {"layer_idx": i, **dimensions}
               for i, kind in enumerate(kinds) if kind == "linear_attention"}
    if not modules:
        raise ValueError("Missing reference Delta coverage")
    return {
        "modules": modules,
        "identity": {
            "policy": "canonical-recurrent-fp32-v1",
            "version": 1,
            "scope": "all_text_linear_attention",
            "label": ("transformers_fp8_with_fixed_pairwise_fp32_rmsnorm"
                      "_and_canonical_recurrent_delta"),
            "source_sha256": source_sha256,
            "modeling_source_sha256": modeling_sha256,
            "adapter_import": {
                "path": "examples/qwen38_text/reference_delta.py",
                "sha256": source_sha256,
            },
            "config_sha256": hashlib.sha256(
                json.dumps(config, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
            ).hexdigest(),
            "execution": "original_recurrent_for_chunk_and_incremental_calls",
            "original_recurrent_unchanged": True,
        },
    }


def validate_delta_record(record, contract, cases):
    if contract is None:
        if "reference_delta" in record:
            raise ValueError("Undeclared reference Delta policy")
        return
    policy = require_object(record.get("reference_delta"))
    if (
        type(policy.get("version")) is not int
        or any(policy.get(k) != v for k, v in contract["identity"].items())
        or record.get("reference_implementation") != contract["identity"]["label"]
        or policy.get("original_recurrent_unchanged") is not True
        or policy.get("parameters_preserved") is not True
        or policy.get("state_keys_preserved") is not True
    ):
        raise ValueError("Reference Delta identity mismatch")
    modules = policy.get("modules")
    if not isinstance(modules, list) or len(modules) != len(contract["modules"]):
        raise ValueError("Reference Delta module coverage missing")
    count = sum(case["max_steps"] for case in cases)
    redirected = count if record.get("implementation") == "transformers_full" else len(cases)
    seen = set()
    for module in modules:
        require_object(module)
        name = require_string(module.get("name"))
        if name in seen or name not in contract["modules"]:
            raise ValueError("Reference Delta complete module set mismatch")
        seen.add(name)
        if any(
            type(module.get(k)) is not int or module[k] != v
            for k, v in contract["modules"][name].items()
        ) or any(
            type(module.get(k)) is not int or module[k] != v
            for k, v in {
                "calls": count,
                "redirected_chunk_calls": redirected,
                "direct_recurrent_calls": count - redirected,
            }.items()
        ):
            raise ValueError("Reference Delta execution coverage mismatch")
        shapes = module.get("input_shapes")
        if not isinstance(shapes, list) or not shapes:
            raise ValueError("Reference Delta input evidence missing")
        for shape in shapes:
            if (not isinstance(shape, list) or len(shape) != 3
                    or any(type(n) is not int or n <= 0 for n in shape)
                    or shape[0] != 1 or shape[-1] != contract["modules"][name]["hidden_size"]):
                raise ValueError("Reference Delta input shape mismatch")


def validate(
    run_dir,
    workload_path,
    manifest_path,
    max_nrmse,
    min_top1,
    rms_floor,
    qualification_scope="reference_self_check",
    model_id=BF16_MODEL_ID,
    fp8_kernel_revision=None,
    fp8_kernel_sha256=None,
    model_path=None,
    reference_rmsnorm_policy="stock",
    reference_rmsnorm_sha256=None,
    reference_modeling_sha256=None,
    reference_delta_policy="stock",
    reference_delta_sha256=None,
):
    import numpy as np

    for number in (max_nrmse, min_top1, rms_floor):
        if not math.isfinite(number):
            raise ValueError("gates must be finite")
    if max_nrmse < 0 or not 0 <= min_top1 <= 1 or rms_floor <= 0:
        raise ValueError("invalid numerical gates")
    run_dir = Path(run_dir)
    workload = read_json(workload_path)
    manifest = read_json(manifest_path)
    spec = read_json(run_dir / "run.lock.json")
    environment_record = read_json(run_dir / "environment.json")
    if qualification_scope not in {"reference_self_check", "native_text_smoke"}:
        raise ValueError("unknown qualification scope")
    native = qualification_scope == "native_text_smoke"
    fp8 = model_id == FP8_MODEL_ID
    for document in (manifest, workload):
        check_precision(document, model_id)
    if fp8:
        require_digest(fp8_kernel_revision, r"[0-9a-f]{40}")
        require_digest(fp8_kernel_sha256)
    adaptation_contract = reference_adaptation_contract(model_path, manifest) if fp8 else None
    norm_contract = None
    if reference_rmsnorm_policy == "fixed-pairwise-fp32-v1":
        if not fp8:
            raise ValueError("Fixed reference normalization requires FP8")
        metadata = authenticated_reference_metadata(model_path, manifest)
        norm_contract = normalization_contract(metadata["config.json"], reference_rmsnorm_sha256,
                                               reference_modeling_sha256)
    elif (reference_rmsnorm_policy != "stock" or reference_rmsnorm_sha256 is not None
          or reference_modeling_sha256 is not None):
        raise ValueError("Unexpected reference normalization identity")
    recurrent_contract = None
    if reference_delta_policy == "canonical-recurrent-fp32-v1":
        if norm_contract is None:
            raise ValueError("Canonical Delta requires the fixed FP8 normalization policy")
        recurrent_contract = delta_contract(
            metadata["config.json"], reference_delta_sha256, reference_modeling_sha256
        )
    elif reference_delta_policy != "stock" or reference_delta_sha256 is not None:
        raise ValueError("Unexpected reference Delta identity")
    if spec.get("model", None if fp8 else model_id) != model_id:
        raise ValueError("RunSpec model identity differs from requested profile")
    if native:
        if spec.get("comparison_scope") != qualification_scope or not spec.get("candidate_repo"):
            raise ValueError("native smoke requires an explicit native RunSpec and engine checkout")
        for key in ("repo", "candidate_repo"):
            require_string(spec.get(key))
        if Path(spec["candidate_repo"]).resolve() == Path(spec["repo"]).resolve():
            raise ValueError("control and native engine checkouts must be distinct")
        locked = read_json(run_dir / "repositories.lock.json")
        for side in ("baseline", "candidate"):
            source_identity(locked.get(side), available=True)
    elif spec.get("comparison_scope") == "native_text_smoke":
        raise ValueError("native evidence cannot be relabelled as a reference self-check")
    if spec.get("objective") != "correctness":
        raise ValueError("reference self-check requires correctness objective")
    count = spec.get("repetitions")
    if type(count) is not int or count < 1:
        raise ValueError("invalid repetition count")
    cases = workload["cases"]
    expected = {case["id"]: case for case in cases}
    if not expected or len(expected) != len(cases):
        raise ValueError("workload case IDs must be unique and nonempty")
    for case in cases:
        if type(case["max_steps"]) is not int or case["max_steps"] < 1:
            raise ValueError("invalid workload steps")
    identities = {
        "schema_version": 1,
        "qualification_scope": qualification_scope,
        "model_id": model_id,
        "model_revision": manifest["revision"],
        "manifest_sha256": digest(manifest_path),
        "workload_sha256": digest(workload_path),
        "dtype": "fp8" if fp8 else "bfloat16",
        "device_type": "cuda",
        "device_count": 1,
        "tokenization": "raw_text_no_special_tokens",
    }
    if manifest.get("model_id") != identities["model_id"]:
        raise ValueError("wrong model manifest")
    if workload.get("model_id") != identities["model_id"]:
        raise ValueError("wrong model workload")
    if spec.get("model_revision") != manifest["revision"]:
        raise ValueError("RunSpec model revision differs from manifest")
    if spec.get("workload_id") != identities["workload_sha256"]:
        raise ValueError("RunSpec workload hash differs from workload")
    traces = {}
    environment = None
    reference_kernel = None
    norm_weights = None
    candidate_role = "nanovllm_qwen38" if native else "transformers_cached"
    for side, implementation in (("baseline", "transformers_full"), ("candidate", candidate_role)):
        wanted = {f"trial-{index:03d}" for index in range(1, count + 1)}
        found = {path.name for path in (run_dir / side).glob("trial-*")}
        if found != wanted:
            raise ValueError("missing or extra trial coverage")
        traces[side] = []
        for trial_name in sorted(wanted):
            root = run_dir / side / trial_name
            record = read_json(root / "result.json")
            execution = read_json(root / "execution.json")
            if execution.get("status") != "completed" or execution.get("returncode") != 0:
                raise ValueError("trial execution did not complete")
            if any(record.get(key) != value for key, value in identities.items()):
                raise ValueError("trace identity, precision or scope mismatch")
            if record.get("implementation") != implementation:
                raise ValueError("incorrect reference implementation role")
            check_precision(record, model_id)
            role_norm_contract = None if native and side == "candidate" else norm_contract
            role_delta_contract = None if native and side == "candidate" else recurrent_contract
            label = (
                role_delta_contract["identity"]["label"]
                if role_delta_contract is not None
                else None
            )
            validate_normalization_record(record, role_norm_contract, label)
            validate_delta_record(record, role_delta_contract, cases)
            if role_norm_contract is not None:
                observed_weights = {item["name"]: item["weight_sha256_fp32"]
                                    for item in record["reference_normalization"]["modules"]}
                if norm_weights is None:
                    norm_weights = observed_weights
                elif observed_weights != norm_weights:
                    raise ValueError("Reference normalization weights changed across trials")
            policy = NATIVE_POLICY if native and side == "candidate" else REFERENCE_POLICY
            if fp8:
                policy = ({**policy, "fp8_linear": "triton_block_fp8"}
                          if native and side == "candidate" else
                          {**policy, "fp8_linear": "finegrained_fp8", "deepgemm": False})
                if not (native and side == "candidate"):
                    kernel = validate_reference_kernel(
                        record, fp8_kernel_revision, fp8_kernel_sha256,
                    )
                    validate_adaptation_record(record["fp8_loading"], adaptation_contract)
                    if reference_kernel is None:
                        reference_kernel = kernel
                    elif reference_kernel != kernel:
                        raise ValueError("Reference FP8 kernel changed across trials")
            if record.get("kernel_policy") != policy:
                raise ValueError("incorrect implementation kernel policy")
            if native:
                expected_repo = spec["repo"] if side == "baseline" else spec["candidate_repo"]
                require_string(execution.get("cwd"))
                if Path(execution["cwd"]).resolve() != Path(expected_repo).resolve():
                    raise ValueError("trial did not execute in its snapshotted checkout")
                validate_sources(record, spec, locked, root, side, model_id)
            vocab = record.get("vocab_size")
            if type(vocab) is not int or vocab < 1:
                raise ValueError("missing vocabulary size")
            current = {key: record.get(key) for key in ("device_model", "versions", "vocab_size")}
            if not current["device_model"] or not isinstance(current["versions"], dict):
                raise ValueError("missing environment qualification")
            if current["device_model"] != environment_record.get("requested_device_model"):
                raise ValueError("actual GPU differs from requested qualification target")
            version_keys = ("torch", "transformers", "kernels", "triton") if fp8 else (
                "torch", "transformers")
            if not all(current["versions"].get(key) for key in version_keys):
                raise ValueError("missing runtime versions")
            if environment is None:
                environment = current
            elif current != environment:
                raise ValueError("environment changed across trials")
            outputs = record["cases"]
            by_id = {case["id"]: case for case in outputs}
            if len(by_id) != len(outputs) or set(by_id) != set(expected):
                raise ValueError("missing, duplicate or unexpected case")
            loaded = {}
            for case_id, case in by_id.items():
                steps = expected[case_id]["max_steps"]
                if not token_ids(case.get("input_ids")) or not token_ids(
                    case.get("continuation_ids")
                ) or len(case["continuation_ids"]) != steps:
                    raise ValueError("invalid token coverage")
                if any(token >= vocab for token in case["input_ids"] + case["continuation_ids"]):
                    raise ValueError("recorded token ID exceeds vocabulary")
                artifact = local_file(root, case["logits_file"])
                if digest(artifact) != case["logits_sha256"]:
                    raise ValueError("logit artifact hash mismatch")
                with np.load(artifact, allow_pickle=False) as data:
                    if data["logits"].dtype != np.float32:
                        raise ValueError("logit observations must be float32")
                    logits = data["logits"].astype(np.float64)
                if logits.shape != (steps, vocab) or not np.isfinite(logits).all():
                    raise ValueError("incomplete or nonfinite logit array")
                if case.get("greedy_ids") != logits.argmax(axis=1).tolist():
                    raise ValueError("greedy observations disagree with logits")
                loaded[case_id] = (case, logits)
            traces[side].append(loaded)
    measurements, failed = [], []
    for index in range(count):
        for case_id in expected:
            a, reference = traces["baseline"][index][case_id]
            b, candidate = traces["candidate"][index][case_id]
            if any(a[key] != b[key] for key in ("input_ids", "continuation_ids")):
                raise ValueError("paired trials used different tokens")
            rms = float(np.sqrt(np.mean(reference * reference)))
            nrmse = float(np.sqrt(np.mean((candidate - reference) ** 2))) / max(rms, rms_floor)
            top1 = float(np.mean(reference.argmax(axis=1) == candidate.argmax(axis=1)))
            measurements.append({"trial": index + 1, "case": case_id,
                                 "nrmse": nrmse, "top1_agreement": top1})
            if nrmse > max_nrmse or top1 < min_top1:
                failed.append(f"trial {index + 1}, case {case_id}: numerical gate rejected")
    # Explicit replay_of pairs detect state contamination within each trial.
    for side, trials in traces.items():
        for index, trial in enumerate(trials):
            for case_id, requested in expected.items():
                if "replay_of" not in requested:
                    continue
                original = requested["replay_of"]
                if original not in trial:
                    raise ValueError("replay source case missing")
                a, logits_a = trial[original]
                b, logits_b = trial[case_id]
                if any(a[key] != b[key] for key in ("input_ids", "continuation_ids")):
                    raise ValueError("replay cases did not use identical tokens")
                if not np.array_equal(logits_a, logits_b):
                    failed.append(f"{side} trial {index + 1}: reset/replay differs")
    return {"verdict": "FAIL" if failed else "PASS", "reasons": failed,
            "qualification_scope": qualification_scope, "measurements": measurements,
            "gates": {"max_nrmse": max_nrmse, "min_top1": min_top1, "rms_floor": rms_floor},
            "limitations": [
                "No whole-engine acceptance" if native else "No dedicated engine validated",
                "No performance claim",
                "Bounded raw-text teacher-forcing smoke, not broad task quality"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", choices=MODEL_IDS, default=BF16_MODEL_ID)
    parser.add_argument("--fp8-kernel-revision")
    parser.add_argument("--fp8-kernel-sha256")
    parser.add_argument("--reference-rmsnorm-policy",
                        choices=("stock", "fixed-pairwise-fp32-v1"), default="stock")
    parser.add_argument("--reference-rmsnorm-sha256")
    parser.add_argument(
        "--reference-delta-policy",
        choices=("stock", "canonical-recurrent-fp32-v1"),
        default="stock",
    )
    parser.add_argument("--reference-delta-sha256")
    parser.add_argument("--reference-modeling-sha256")
    parser.add_argument("--model-path", type=Path)
    for name in ("run-dir", "workload", "manifest", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    for name in ("max-nrmse", "min-top1", "rms-floor"):
        parser.add_argument("--" + name, required=True, type=float)
    parser.add_argument("--qualification-scope", default="reference_self_check",
                        choices=("reference_self_check", "native_text_smoke"))
    args = parser.parse_args()
    try:
        result = validate(args.run_dir, args.workload, args.manifest,
                          args.max_nrmse, args.min_top1, args.rms_floor, args.qualification_scope,
                          args.model_id, args.fp8_kernel_revision, args.fp8_kernel_sha256,
                          args.model_path, args.reference_rmsnorm_policy,
                          args.reference_rmsnorm_sha256, args.reference_modeling_sha256,
                          args.reference_delta_policy, args.reference_delta_sha256)
    except (OSError, ValueError, KeyError, TypeError, ImportError, zipfile.BadZipFile) as exc:
        # Do not echo exception strings, which may contain private runtime paths.
        result = {"verdict": "INCONCLUSIVE", "qualification_scope": args.qualification_scope,
                  "reasons": [f"Invalid or missing validation evidence ({type(exc).__name__})"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result))
    return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
