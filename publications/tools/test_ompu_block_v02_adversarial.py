#!/usr/bin/env python3
"""Run the independent ompu-block v0.2 adversarial fixture corpus."""

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "publications/tools/validate_ompu_block_v02.py"
SCHEMA_PATH = REPO_ROOT / "publications/schemas/ompu_block_v0.2.json"
FIXTURE_ROOT = REPO_ROOT / "publications/schemas/fixtures/adversarial"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("ompu_block_v02_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def result_paths(entries):
    return {entry["path"] for entry in entries}


def describe_actual(result):
    schema_paths = sorted(result_paths(result.schema_errors))
    semantic_paths = sorted(result_paths(result.semantic_errors))
    warning_paths = sorted(result_paths(result.semantic_warnings))
    return (
        f"schema={schema_paths or ['pass']} "
        f"semantic={semantic_paths or ['pass']} "
        f"warnings={warning_paths or ['none']}"
    )


def main():
    validator = load_validator_module()
    if not validator.HAVE_JSONSCHEMA:
        print("ERROR: real Draft 2020-12 oracle unavailable; fallback is not accepted")
        return 2

    schema, schema_error = validator.load_schema(str(SCHEMA_PATH))
    if schema_error:
        print(f"ERROR: {schema_error}")
        return 2
    validator.Draft202012Validator.check_schema(schema)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures = []

    golden_passed = 0
    for relative_path in manifest["golden_valid"]:
        path = (FIXTURE_ROOT / relative_path).resolve()
        result = validator.validate_file(str(path), schema=schema)
        if result.valid:
            golden_passed += 1
            print(f"PASS GOLDEN_VALID {path.name}")
        else:
            failures.append(f"GOLDEN_VALID:{path.name}")
            print(f"FAIL GOLDEN_VALID {path.name}: {describe_actual(result)}")

    adversarial_passed = 0
    for case in manifest["fixtures"]:
        path = FIXTURE_ROOT / case["file"]
        result = validator.validate_file(str(path), schema=schema)
        expected_layer = case["expected_layer"]
        expected_pointer = case["expected_pointer"]
        code = case["expected_error_code"]

        if expected_layer == "schema":
            actual_paths = result_paths(result.schema_errors)
            passed = result.schema_ok is False and expected_pointer in actual_paths
        elif expected_layer == "semantic":
            actual_paths = result_paths(result.semantic_errors)
            passed = (
                result.schema_ok is True
                and not result.schema_errors
                and expected_pointer in actual_paths
            )
        else:
            raise ValueError(f"Unknown expected layer: {expected_layer}")

        if passed:
            adversarial_passed += 1
            print(f"PASS {code} {case['file']} -> {expected_layer}:{expected_pointer}")
        else:
            failures.append(code)
            print(
                f"FAIL {code} {case['file']} expected "
                f"{expected_layer}:{expected_pointer}; {describe_actual(result)}"
            )

    golden_total = len(manifest["golden_valid"])
    adversarial_total = len(manifest["fixtures"])

    warning_passed = 0
    for case in manifest.get("corpus_warning_cases", []):
        path = REPO_ROOT / case["file"]
        result = validator.validate_file(str(path), schema=schema)
        warning_entries = [
            entry
            for entry in result.semantic_warnings
            if entry["path"] == case["expected_pointer"]
        ]
        passed = (
            result.valid
            and len(warning_entries) == 1
            and all(
                needle in warning_entries[0]["message"]
                for needle in case["message_contains"]
            )
        )
        if passed:
            warning_passed += 1
            print(
                f"PASS CORPUS_WARNING {path.name} -> "
                f"{case['expected_pointer']}"
            )
        else:
            failures.append(f"CORPUS_WARNING:{path.name}")
            print(
                f"FAIL CORPUS_WARNING {path.name}: "
                f"{describe_actual(result)}"
            )

    warning_total = len(manifest.get("corpus_warning_cases", []))
    print()
    print(f"GOLDEN {golden_passed}/{golden_total} valid")
    print(f"ADVERSARIAL {adversarial_passed}/{adversarial_total} rejected as expected")
    print(f"CORPUS_WARNING {warning_passed}/{warning_total} preserved as expected")
    print(f"RESULT {'PASS' if not failures else 'FAIL'}")

    if failures:
        print("MISSED " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
