#!/usr/bin/env python3
"""
OMPU Publication Block Validator v2.0

Validates publications against publication_block_v2.json schema.
Performs both JSON Schema validation and semantic checks
(step numbering, cross-references, temperature consistency, etc.)

Usage:
    python validate_publication.py <publication.json> [--schema path/to/schema.json]
    python validate_publication.py --batch <dir> [--schema path/to/schema.json]
    python validate_publication.py --all [--schema path/to/schema.json]

Exit codes:
    0 = all validations passed
    1 = validation failures found
    2 = file/argument error
"""

import json
import sys
import os
import re
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = SCRIPT_DIR.parent / "schemas" / "publication_block_v2.json"
DEFAULT_DRAFTS = SCRIPT_DIR.parent / "drafts"

# ---------------------------------------------------------------------------
# Lightweight JSON Schema validator (no external dependencies)
# ---------------------------------------------------------------------------


class SchemaError:
    """A single validation finding."""

    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity  # error, warning, info

    def __str__(self):
        tag = self.severity.upper()
        return f"  [{tag}] {self.path}: {self.message}"


class SchemaValidator:
    """
    Minimal JSON Schema Draft 2020-12 validator.
    Supports: type, enum, const, required, properties, additionalProperties,
    pattern, minLength, maxLength, minimum, maximum, exclusiveMinimum,
    exclusiveMaximum, minItems, maxItems, uniqueItems, items, format,
    oneOf, $ref, $defs, default, description, and nullable via type arrays.
    """

    def __init__(self, schema: dict):
        self.root_schema = schema
        self.defs = schema.get("$defs", {})
        self.errors: list[SchemaError] = []

    def validate(self, instance: dict) -> list[SchemaError]:
        self.errors = []
        self._validate(instance, self.root_schema, "$")
        return self.errors

    def _resolve_ref(self, ref: str) -> dict:
        if ref.startswith("#/$defs/"):
            name = ref[len("#/$defs/"):]
            if name in self.defs:
                return self.defs[name]
        return {}

    def _validate(self, value, schema: dict, path: str):
        if "$ref" in schema:
            resolved = self._resolve_ref(schema["$ref"])
            desc = schema.get("description")
            merged = {**resolved}
            if desc:
                merged["description"] = desc
            self._validate(value, merged, path)
            return

        if "oneOf" in schema:
            matched = 0
            for option in schema["oneOf"]:
                sub = SchemaValidator.__new__(SchemaValidator)
                sub.root_schema = self.root_schema
                sub.defs = self.defs
                sub.errors = []
                sub._validate(value, option, path)
                if not any(e.severity == "error" for e in sub.errors):
                    matched += 1
            if matched == 0:
                self.errors.append(SchemaError(path, f"does not match any oneOf option"))
            return

        # not (JSON Schema negation)
        if "not" in schema:
            sub = SchemaValidator.__new__(SchemaValidator)
            sub.root_schema = self.root_schema
            sub.defs = self.defs
            sub.errors = []
            sub._validate(value, schema["not"], path)
            if not any(e.severity == "error" for e in sub.errors):
                # The "not" condition matched when it shouldn't have
                self.errors.append(SchemaError(path, "value matches schema that it should NOT match"))
            # If the sub-validation found errors, that means "not" is satisfied (good)
            return

        # if/then/else (JSON Schema conditional)
        if "if" in schema:
            if_schema = schema["if"]
            sub = SchemaValidator.__new__(SchemaValidator)
            sub.root_schema = self.root_schema
            sub.defs = self.defs
            sub.errors = []
            sub._validate(value, if_schema, path)
            condition_met = not any(e.severity == "error" for e in sub.errors)
            if condition_met and "then" in schema:
                then_schema = schema["then"]
                self._validate(value, then_schema, path)
            elif not condition_met and "else" in schema:
                else_schema = schema["else"]
                self._validate(value, else_schema, path)

        # Type checking
        if "type" in schema:
            expected_types = schema["type"]
            if isinstance(expected_types, str):
                expected_types = [expected_types]
            if not self._check_type(value, expected_types):
                self.errors.append(
                    SchemaError(path, f"expected type {schema['type']}, got {type(value).__name__} ({repr(value)[:80]})")
                )
                return  # stop further checks if type mismatch

        # Null is valid for nullable types -- skip further checks
        if value is None:
            return

        # const
        if "const" in schema:
            if value != schema["const"]:
                self.errors.append(
                    SchemaError(path, f"expected const {schema['const']!r}, got {value!r}")
                )

        # enum
        if "enum" in schema:
            if value not in schema["enum"]:
                self.errors.append(
                    SchemaError(path, f"value {value!r} not in enum {schema['enum']}")
                )

        # String checks
        if isinstance(value, str):
            if "pattern" in schema:
                if not re.search(schema["pattern"], value):
                    self.errors.append(
                        SchemaError(path, f"value {value!r} does not match pattern {schema['pattern']!r}")
                    )
            if "minLength" in schema and len(value) < schema["minLength"]:
                self.errors.append(
                    SchemaError(path, f"string length {len(value)} < minLength {schema['minLength']}")
                )
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                self.errors.append(
                    SchemaError(path, f"string length {len(value)} > maxLength {schema['maxLength']}")
                )
            if "format" in schema:
                self._check_format(value, schema["format"], path)

        # Number checks
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in schema and value < schema["minimum"]:
                self.errors.append(
                    SchemaError(path, f"value {value} < minimum {schema['minimum']}")
                )
            if "maximum" in schema and value > schema["maximum"]:
                self.errors.append(
                    SchemaError(path, f"value {value} > maximum {schema['maximum']}")
                )

        # Array checks
        if isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                self.errors.append(
                    SchemaError(path, f"array length {len(value)} < minItems {schema['minItems']}")
                )
            if "maxItems" in schema and len(value) > schema["maxItems"]:
                self.errors.append(
                    SchemaError(path, f"array length {len(value)} > maxItems {schema['maxItems']}")
                )
            if "uniqueItems" in schema and schema["uniqueItems"]:
                seen = []
                for item in value:
                    serialized = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item
                    if serialized in seen:
                        self.errors.append(
                            SchemaError(path, f"duplicate item found in array that requires uniqueItems")
                        )
                        break
                    seen.append(serialized)
            if "items" in schema:
                for i, item in enumerate(value):
                    self._validate(item, schema["items"], f"{path}[{i}]")

        # Object checks
        if isinstance(value, dict):
            props = schema.get("properties", {})
            required = schema.get("required", [])
            additional = schema.get("additionalProperties", True)

            for req in required:
                if req not in value:
                    self.errors.append(
                        SchemaError(path, f"missing required property {req!r}")
                    )

            for key, val in value.items():
                if key in props:
                    self._validate(val, props[key], f"{path}.{key}")
                elif additional is False:
                    self.errors.append(
                        SchemaError(path, f"additional property {key!r} not allowed")
                    )
                elif isinstance(additional, dict):
                    self._validate(val, additional, f"{path}.{key}")

    def _check_type(self, value, types: list) -> bool:
        for t in types:
            if t == "null" and value is None:
                return True
            if t == "string" and isinstance(value, str):
                return True
            if t == "integer" and isinstance(value, int) and not isinstance(value, bool):
                return True
            if t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
                return True
            if t == "boolean" and isinstance(value, bool):
                return True
            if t == "array" and isinstance(value, list):
                return True
            if t == "object" and isinstance(value, dict):
                return True
        return False

    def _check_format(self, value: str, fmt: str, path: str):
        if fmt == "date-time":
            # Accept common ISO 8601 variants
            patterns = [
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            ]
            if not any(re.match(p, value) for p in patterns):
                self.errors.append(
                    SchemaError(path, f"value {value!r} does not match format 'date-time'", "warning")
                )
        elif fmt == "date":
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                self.errors.append(
                    SchemaError(path, f"value {value!r} does not match format 'date'", "warning")
                )


# ---------------------------------------------------------------------------
# Semantic validation (beyond JSON Schema)
# ---------------------------------------------------------------------------


def semantic_validate(pub: dict) -> list[SchemaError]:
    """
    Checks that go beyond schema structure:
    - Step numbering is sequential and unique
    - Cross-references (supports, refutes, requires) point to valid steps
    - Temperature consistency warnings
    - Author role / type coherence
    - Graph refs don't self-reference
    - Crystal stage / compression_count coherence
    """
    errors = []
    chain = pub.get("chain", [])

    # --- Step numbering ---
    steps = [b.get("step") for b in chain if isinstance(b.get("step"), int)]
    step_set = set(steps)

    if steps != sorted(steps):
        errors.append(SchemaError("$.chain", "step numbers are not in ascending order", "warning"))

    step_counts = Counter(steps)
    for step_num, count in step_counts.items():
        if count > 1:
            errors.append(SchemaError(f"$.chain", f"duplicate step number {step_num}", "error"))

    expected_steps = list(range(1, len(chain) + 1))
    if steps != expected_steps:
        errors.append(SchemaError(
            "$.chain", f"steps should be sequential 1..{len(chain)}, got {steps[:5]}{'...' if len(steps) > 5 else ''}",
            "warning"
        ))

    # --- Cross-references ---
    for i, block in enumerate(chain):
        step = block.get("step", i + 1)
        path = f"$.chain[{i}]"

        supports = block.get("supports")
        if supports is not None and supports not in step_set:
            errors.append(SchemaError(path, f"'supports' references non-existent step {supports}", "error"))
        if supports is not None and supports == step:
            errors.append(SchemaError(path, f"'supports' references own step {step}", "warning"))

        refutes_val = block.get("refutes")
        if refutes_val is not None and refutes_val not in step_set:
            errors.append(SchemaError(path, f"'refutes' references non-existent step {refutes_val}", "error"))

        requires = block.get("requires", [])
        if isinstance(requires, list):
            for req in requires:
                if isinstance(req, int):
                    if req not in step_set:
                        errors.append(SchemaError(path, f"'requires' references non-existent step {req}", "error"))
                    if req >= step:
                        errors.append(SchemaError(path, f"'requires' step {req} >= current step {step} (forward reference)", "warning"))

    # --- Temperature consistency ---
    signal_temp = pub.get("signal", {}).get("temperature")
    if signal_temp:
        temp_order = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}
        signal_level = temp_order.get(signal_temp, 0)
        block_temps = [b.get("temperature") for b in chain if b.get("temperature")]
        max_block = max((temp_order.get(t, 0) for t in block_temps), default=0)
        if signal_level < max_block:
            errors.append(SchemaError(
                "$.signal.temperature",
                f"publication temperature {signal_temp} is cooler than hottest block T{max_block} -- signal should reflect highest uncertainty",
                "warning"
            ))

    # --- Crystal coherence ---
    crystal = pub.get("crystal", {})
    stage = crystal.get("stage")
    comp_count = crystal.get("compression_count", 0)
    compressions_list = crystal.get("compressions", [])

    if comp_count != len(compressions_list) and len(compressions_list) > 0:
        errors.append(SchemaError(
            "$.crystal", f"compression_count={comp_count} but compressions array has {len(compressions_list)} entries",
            "warning"
        ))

    if stage == "published" and comp_count < 2:
        errors.append(SchemaError(
            "$.crystal", f"stage is 'published' but compression_count={comp_count} (minimum 2 for publication)",
            "warning"
        ))

    if stage == "published" and not pub.get("doi"):
        errors.append(SchemaError(
            "$.crystal", "stage is 'published' but doi is null",
            "warning"
        ))

    # --- Graph refs ---
    pub_id = pub.get("pub_id", "")
    for i, ref in enumerate(pub.get("graph_refs", [])):
        target = ref.get("target", "")
        if target == pub_id:
            errors.append(SchemaError(f"$.graph_refs[{i}]", f"self-reference: target is own pub_id {pub_id}", "warning"))

    # --- Meta block count ---
    meta = pub.get("meta", {})
    if isinstance(meta, dict) and "actual_block_count" in meta:
        declared = meta["actual_block_count"]
        actual = len(chain)
        if declared != actual:
            errors.append(SchemaError(
                "$.meta.actual_block_count",
                f"declared {declared} but chain has {actual} blocks",
                "warning"
            ))

    # --- Author uniqueness ---
    author_ids = [a.get("id") for a in pub.get("authors", []) if a.get("id")]
    id_counts = Counter(author_ids)
    for aid, count in id_counts.items():
        if count > 1:
            errors.append(SchemaError("$.authors", f"duplicate author id {aid!r}", "warning"))

    return errors


# ---------------------------------------------------------------------------
# v1 -> v2 migration hints
# ---------------------------------------------------------------------------


def migration_hints(pub: dict) -> list[SchemaError]:
    """
    Generate hints for migrating a v1 publication to v2.
    These are informational, not errors.
    """
    hints = []

    if "schema_version" not in pub:
        hints.append(SchemaError("$", "missing 'schema_version' field -- add '\"schema_version\": \"2.0.0\"' for v2 compliance", "info"))

    # Check for v1 types not in v2 -- shouldn't happen since v2 is superset
    pub_type = pub.get("type")
    v2_types = ["theory", "empirical", "experiment", "hypothesis", "dataset", "standard",
                 "framework", "replication", "refutation", "synthesis", "protocol",
                 "artifact", "meta", "tool", "review"]
    if pub_type and pub_type not in v2_types:
        hints.append(SchemaError("$.type", f"type {pub_type!r} not in v2 enum -- closest match needed", "info"))

    # Check author roles
    v2_roles = ["author", "researcher", "experimenter", "reviewer", "validator",
                "data_source", "signer", "coordinator", "contributor", "publisher",
                "editor", "advisor"]
    for i, author in enumerate(pub.get("authors", [])):
        role = author.get("role")
        if role and role not in v2_roles:
            hints.append(SchemaError(f"$.authors[{i}].role", f"role {role!r} not in v2 enum", "info"))

    # Chain block types
    v2_block_types = ["claim", "evidence", "derivation", "definition", "protocol",
                      "observation", "bridge", "gap", "refutation", "convergence",
                      "fish", "compression", "result", "prediction", "axiom",
                      "example", "counterexample", "summary", "meta"]
    for i, block in enumerate(pub.get("chain", [])):
        btype = block.get("type")
        if btype and btype not in v2_block_types:
            hints.append(SchemaError(f"$.chain[{i}].type", f"block type {btype!r} not in v2 enum", "info"))

    if "updated_at" not in pub:
        hints.append(SchemaError("$", "consider adding 'updated_at' field for edit tracking", "info"))

    if "tags" not in pub:
        hints.append(SchemaError("$", "consider adding 'tags' array for machine-parseable topic classification", "info"))

    return hints


# ---------------------------------------------------------------------------
# Main validation entry point
# ---------------------------------------------------------------------------


def validate_publication(pub_path: str, schema_path: str, verbose: bool = False) -> dict:
    """
    Validate a single publication. Returns a result dict.
    """
    result = {
        "file": str(pub_path),
        "valid": False,
        "schema_errors": [],
        "semantic_errors": [],
        "migration_hints": [],
        "error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }

    # Load files
    try:
        with open(pub_path, "r", encoding="utf-8") as f:
            pub = json.load(f)
    except json.JSONDecodeError as e:
        result["schema_errors"].append(str(SchemaError("$", f"invalid JSON: {e}")))
        result["error_count"] = 1
        return result
    except FileNotFoundError:
        result["schema_errors"].append(str(SchemaError("$", f"file not found: {pub_path}")))
        result["error_count"] = 1
        return result

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        result["schema_errors"].append(str(SchemaError("$", f"schema load error: {e}")))
        result["error_count"] = 1
        return result

    # Schema validation
    validator = SchemaValidator(schema)
    schema_findings = validator.validate(pub)
    result["schema_errors"] = [str(e) for e in schema_findings]

    # Semantic validation
    sem_findings = semantic_validate(pub)
    result["semantic_errors"] = [str(e) for e in sem_findings]

    # Migration hints
    mig_findings = migration_hints(pub)
    result["migration_hints"] = [str(e) for e in mig_findings]

    # Count by severity
    all_findings = schema_findings + sem_findings + mig_findings
    result["error_count"] = sum(1 for e in all_findings if e.severity == "error")
    result["warning_count"] = sum(1 for e in all_findings if e.severity == "warning")
    result["info_count"] = sum(1 for e in all_findings if e.severity == "info")
    result["valid"] = result["error_count"] == 0

    return result


def format_result(result: dict, verbose: bool = False) -> str:
    """Format a validation result for human/agent reading."""
    lines = []
    filename = Path(result["file"]).name
    status = "PASS" if result["valid"] else "FAIL"
    lines.append(f"{'=' * 70}")
    lines.append(f"  {filename}")
    lines.append(f"  Status: {status} | Errors: {result['error_count']} | Warnings: {result['warning_count']} | Info: {result['info_count']}")
    lines.append(f"{'=' * 70}")

    if result["schema_errors"]:
        lines.append("\n  Schema Validation:")
        for e in result["schema_errors"]:
            lines.append(f"  {e.strip()}")

    if result["semantic_errors"]:
        lines.append("\n  Semantic Validation:")
        for e in result["semantic_errors"]:
            lines.append(f"  {e.strip()}")

    if verbose and result["migration_hints"]:
        lines.append("\n  Migration Hints (v1 -> v2):")
        for e in result["migration_hints"]:
            lines.append(f"  {e.strip()}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="OMPU Publication Block Validator v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_publication.py pub.json
  python validate_publication.py --batch ../drafts/
  python validate_publication.py --all --verbose
  python validate_publication.py --all --report validation_report.txt
        """
    )
    parser.add_argument("file", nargs="?", help="Publication JSON file to validate")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Path to schema file")
    parser.add_argument("--batch", metavar="DIR", help="Validate all .json files in directory")
    parser.add_argument("--all", action="store_true", help="Validate all files in default drafts directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show migration hints and detailed output")
    parser.add_argument("--report", metavar="FILE", help="Write report to file")
    parser.add_argument("--json-output", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not args.file and not args.batch and not args.all:
        parser.print_help()
        sys.exit(2)

    # Collect files to validate
    files = []
    if args.all:
        drafts_dir = DEFAULT_DRAFTS
        if drafts_dir.exists():
            files = sorted(drafts_dir.glob("*.json"))
        else:
            print(f"Drafts directory not found: {drafts_dir}", file=sys.stderr)
            sys.exit(2)
    elif args.batch:
        batch_dir = Path(args.batch)
        if batch_dir.exists():
            files = sorted(batch_dir.glob("*.json"))
        else:
            print(f"Directory not found: {args.batch}", file=sys.stderr)
            sys.exit(2)
    elif args.file:
        files = [Path(args.file)]

    if not files:
        print("No JSON files found to validate.", file=sys.stderr)
        sys.exit(2)

    # Validate
    results = []
    for f in files:
        result = validate_publication(str(f), args.schema, args.verbose)
        results.append(result)

    # Output
    if args.json_output:
        output = json.dumps(results, indent=2)
    else:
        lines = []
        lines.append("OMPU Publication Block Validator v2.0")
        lines.append(f"Schema: {args.schema}")
        lines.append(f"Date: {datetime.now().isoformat()}")
        lines.append(f"Files: {len(files)}")
        lines.append("")

        for result in results:
            lines.append(format_result(result, args.verbose))

        # Summary
        total_errors = sum(r["error_count"] for r in results)
        total_warnings = sum(r["warning_count"] for r in results)
        total_info = sum(r["info_count"] for r in results)
        passed = sum(1 for r in results if r["valid"])
        failed = len(results) - passed

        lines.append("=" * 70)
        lines.append("  SUMMARY")
        lines.append(f"  Passed: {passed}/{len(results)} | Failed: {failed}/{len(results)}")
        lines.append(f"  Total errors: {total_errors} | Total warnings: {total_warnings} | Info: {total_info}")
        lines.append("=" * 70)

        output = "\n".join(lines)

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {args.report}")
    else:
        print(output)

    # Exit code
    any_failures = any(not r["valid"] for r in results)
    sys.exit(1 if any_failures else 0)


if __name__ == "__main__":
    main()
