#!/usr/bin/env python3
"""
OMPU Block v0.2 Validator -- two-layer validation.

Layer 1: JSON Schema Draft 2020-12 validation (structural)
Layer 2: Semantic integrity checks (referential, logical, profile-based)

Usage:
    python3 validate_ompu_block_v02.py FILE
    python3 validate_ompu_block_v02.py --batch DIR
    python3 validate_ompu_block_v02.py --schema PATH FILE
    python3 validate_ompu_block_v02.py --verbose FILE
    python3 validate_ompu_block_v02.py --json-output FILE

Exit codes:
    0 = valid (no errors)
    1 = invalid (errors found)
    2 = usage error
"""

import json
import sys
import os
import argparse
import re
from pathlib import Path

# --- Schema validation layer ---

HAVE_JSONSCHEMA = False
try:
    import jsonschema
    from jsonschema import Draft202012Validator, ValidationError
    HAVE_JSONSCHEMA = True
except ImportError:
    pass

# --- Default schema location ---

DEFAULT_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "schemas", "ompu_block_v0.2.json"
)

# --- Temperature ordering ---
# Higher number = hotter (more speculative)

T_ORDER = {"T1": 1, "T2": 2, "T3": 3, "T4": 4}

# --- Strong claim keywords for digest-topology coherence ---

STRONG_CLAIM_PATTERNS = [
    (re.compile(r'\bproves?\b', re.IGNORECASE), "proves"),
    (re.compile(r'\bproven\b', re.IGNORECASE), "proven"),
    (re.compile(r'\bdemonstrates?\b', re.IGNORECASE), "demonstrates"),
    (re.compile(r'\bconfirms?\b', re.IGNORECASE), "confirms"),
    (re.compile(r'\bestablishes?\b', re.IGNORECASE), "establishes"),
    (re.compile(r'\bdefinitively\b', re.IGNORECASE), "definitively"),
    (re.compile(r'\bconclusively\b', re.IGNORECASE), "conclusively"),
    (re.compile(r'\bunequivocally\b', re.IGNORECASE), "unequivocally"),
    (re.compile(r'\bcertain(?:ly)?\b', re.IGNORECASE), "certainly"),
]


def extract_claim_text(item):
    """Extract plain text from a StatusClaim (string or {claim, status} object)."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("claim", "")
    return ""


class ValidationResult:
    """Collects errors, warnings, and info from both validation layers."""

    def __init__(self, filename=""):
        self.filename = filename
        self.schema_errors = []
        self.semantic_errors = []
        self.semantic_warnings = []
        self.info = []
        self.schema_ok = None  # None = not run, True/False = result

    def schema_error(self, path, msg):
        self.schema_errors.append({"path": path, "message": msg})

    def error(self, path, msg):
        self.semantic_errors.append({"path": path, "message": msg})

    def warn(self, path, msg):
        self.semantic_warnings.append({"path": path, "message": msg})

    def note(self, path, msg):
        self.info.append({"path": path, "message": msg})

    @property
    def valid(self):
        return len(self.schema_errors) == 0 and len(self.semantic_errors) == 0

    def format_entry(self, prefix, entry):
        return f"  {prefix} [{entry['path']}]: {entry['message']}"

    def report_lines(self, verbose=False):
        lines = []

        # Schema layer
        if self.schema_ok is None:
            lines.append("SCHEMA  [SKIP] schema validation not run")
        elif self.schema_ok:
            lines.append("SCHEMA  [PASS] schema validation (0 violations)")
        else:
            lines.append(
                f"SCHEMA  [FAIL] schema validation "
                f"({len(self.schema_errors)} violations)"
            )
            for entry in self.schema_errors:
                lines.append(self.format_entry("SCHEMA", entry))

        # Semantic layer
        n_err = len(self.semantic_errors)
        n_warn = len(self.semantic_warnings)
        if n_err == 0:
            lines.append(
                f"SEMANTIC [PASS] semantic checks "
                f"(0 errors, {n_warn} warnings)"
            )
        else:
            lines.append(
                f"SEMANTIC [FAIL] semantic checks "
                f"({n_err} errors, {n_warn} warnings)"
            )

        for entry in self.semantic_errors:
            lines.append(self.format_entry("ERROR", entry))
        for entry in self.semantic_warnings:
            lines.append(self.format_entry("WARN ", entry))

        if verbose:
            for entry in self.info:
                lines.append(self.format_entry("INFO ", entry))

        # Final result
        status = "VALID" if self.valid else "INVALID"
        lines.append(f"RESULT  [{status}] {self.filename}")

        return lines

    def to_dict(self):
        return {
            "filename": self.filename,
            "valid": self.valid,
            "schema": {
                "status": (
                    "pass" if self.schema_ok
                    else ("fail" if self.schema_ok is False else "skip")
                ),
                "violations": self.schema_errors,
            },
            "semantic": {
                "status": "pass" if len(self.semantic_errors) == 0 else "fail",
                "errors": self.semantic_errors,
                "warnings": self.semantic_warnings,
            },
            "info": self.info,
        }


# ============================================================
# Layer 1: JSON Schema validation
# ============================================================

def load_schema(schema_path):
    """Load JSON Schema from file. Returns (schema_dict, error_string)."""
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"Schema file not found: {schema_path}"
    except json.JSONDecodeError as e:
        return None, f"Schema file is not valid JSON: {e}"


def validate_schema_layer(block, schema, result):
    """Run JSON Schema Draft 2020-12 validation. Populates result.schema_errors."""
    if not HAVE_JSONSCHEMA:
        result.schema_ok = None
        result.warn(
            "/",
            "jsonschema library not installed. Schema validation skipped. "
            "Install: pip install jsonschema"
        )
        _validate_schema_fallback(block, result)
        return

    try:
        validator = Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(block),
            key=lambda e: list(e.absolute_path)
        )
        if errors:
            result.schema_ok = False
            for err in errors:
                path = (
                    "/" + "/".join(str(p) for p in err.absolute_path)
                    if err.absolute_path else "/"
                )
                msg = err.message
                if len(msg) > 300:
                    msg = msg[:297] + "..."
                result.schema_error(path, msg)
        else:
            result.schema_ok = True
    except Exception as e:
        result.schema_ok = False
        result.schema_error("/", f"Schema validation engine error: {e}")


def _validate_schema_fallback(block, result):
    """Manual structural checks when jsonschema is not available.

    This is NOT a substitute for real JSON Schema validation.
    It catches the most common structural problems only.
    """
    result.note(
        "/",
        "Running fallback structural checks "
        "(install jsonschema for full Draft 2020-12 validation)"
    )

    if not isinstance(block, dict):
        result.schema_error("/", "Root must be a JSON object.")
        return

    # Required top-level fields (v0.2 requires profile)
    for field in ["$self", "id", "type", "title", "signal", "nodes", "profile"]:
        if field not in block:
            result.schema_error(f"/{field}", f"Required field '{field}' is missing.")

    # $self structure
    self_obj = block.get("$self")
    if isinstance(self_obj, dict):
        if self_obj.get("format") != "ompu-block":
            result.schema_error(
                "/$self/format",
                f"Expected 'ompu-block', got '{self_obj.get('format')}'."
            )
        version = self_obj.get("version")
        if version != "0.2.0":
            result.schema_error(
                "/$self/version",
                f"Expected '0.2.0', got '{version}'."
            )

    # type enum
    valid_types = {
        "theory", "experiment", "empirical", "hypothesis", "framework",
        "standard", "protocol", "refutation", "replication", "synthesis",
        "tool", "meta"
    }
    block_type = block.get("type")
    if block_type is not None and block_type not in valid_types:
        result.schema_error("/type", f"Invalid type '{block_type}'.")

    # profile enum
    profile = block.get("profile")
    if profile is not None and profile not in {"lite", "research"}:
        result.schema_error("/profile", f"Invalid profile '{profile}'.")

    # signal structure
    signal = block.get("signal")
    if isinstance(signal, dict):
        for field in ["digest", "t", "falsifies_if"]:
            if field not in signal:
                result.schema_error(
                    f"/signal/{field}",
                    f"Required signal field '{field}' is missing."
                )
        t = signal.get("t")
        if t is not None and t not in {"T1", "T2", "T3", "T4"}:
            result.schema_error("/signal/t", f"Invalid temperature '{t}'.")

    # nodes
    nodes = block.get("nodes")
    if isinstance(nodes, dict):
        if len(nodes) == 0:
            result.schema_error("/nodes", "Must contain at least one node.")
    elif nodes is not None:
        result.schema_error("/nodes", "Must be an object.")

    # Conditional: research profile requirements
    if profile == "research":
        for field in ["topology", "edges", "path"]:
            if field not in block:
                result.schema_error(
                    f"/{field}",
                    f"Profile 'research' requires '{field}'."
                )
        if block_type == "experiment" and "reproduce" not in block:
            result.schema_error(
                "/reproduce",
                "Profile 'research' with type 'experiment' requires 'reproduce'."
            )

    result.schema_ok = len(result.schema_errors) == 0


# ============================================================
# Layer 2: Semantic validation
# ============================================================

def get_node_ids(block):
    """Extract node IDs from the block."""
    nodes = block.get("nodes")
    if isinstance(nodes, dict):
        return set(nodes.keys())
    return set()


def check_edge_referential_integrity(block, result):
    """All edge from/to must reference existing node keys."""
    node_ids = get_node_ids(block)
    edges = block.get("edges", [])
    if not isinstance(edges, list):
        return

    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            continue
        prefix = f"/edges[{i}]"

        from_id = edge.get("from")
        to_id = edge.get("to")

        if from_id is not None and node_ids and from_id not in node_ids:
            result.error(
                f"{prefix}/from",
                f"Node '{from_id}' does not exist in nodes. "
                f"Available: {sorted(node_ids)}"
            )

        if to_id is not None and node_ids and to_id not in node_ids:
            result.error(
                f"{prefix}/to",
                f"Node '{to_id}' does not exist in nodes. "
                f"Available: {sorted(node_ids)}"
            )

        # Self-loop warning
        if from_id is not None and from_id == to_id:
            result.warn(prefix, f"Self-loop: '{from_id}' -> '{to_id}'.")


def check_path_consistency(block, result):
    """All path entries must reference existing node keys."""
    node_ids = get_node_ids(block)
    path = block.get("path")
    if path is None or not isinstance(path, list):
        return

    for i, node_id in enumerate(path):
        if isinstance(node_id, str) and node_ids and node_id not in node_ids:
            result.error(
                f"/path[{i}]",
                f"Node '{node_id}' does not exist in nodes."
            )

    # Duplicate warning
    seen = set()
    for node_id in path:
        if isinstance(node_id, str):
            if node_id in seen:
                result.warn("/path", f"Duplicate node '{node_id}' in path.")
            seen.add(node_id)

    # Completeness info
    if node_ids:
        path_set = set(p for p in path if isinstance(p, str))
        missing = node_ids - path_set
        if missing:
            result.warn(
                "/path",
                f"Path does not include all nodes. Missing: {sorted(missing)}"
            )


def check_temperature_consistency(block, result):
    """signal.t should be >= hottest node temperature.

    Higher T number = hotter = more speculative.
    Block-level temperature should not be cooler than any individual node.
    """
    signal = block.get("signal")
    if not isinstance(signal, dict):
        return
    block_t = signal.get("t")
    if block_t is None or block_t not in T_ORDER:
        return

    nodes = block.get("nodes")
    if not isinstance(nodes, dict):
        return

    block_t_val = T_ORDER[block_t]
    hottest_node = None
    hottest_val = 0

    for node_id, node in nodes.items():
        if not isinstance(node, dict):
            continue
        node_t = node.get("t")
        if node_t is not None and node_t in T_ORDER:
            node_val = T_ORDER[node_t]
            if node_val > hottest_val:
                hottest_val = node_val
                hottest_node = node_id

    if hottest_node and hottest_val > block_t_val:
        result.warn(
            "/signal/t",
            f"Block temperature {block_t} is cooler than node "
            f"'{hottest_node}' with temperature T{hottest_val}. "
            f"Block temperature should be >= hottest node (T{hottest_val})."
        )


def check_profile_enforcement(block, result):
    """If profile=research, enforce strict structural requirements.

    These checks are SEMANTIC -- they go beyond what JSON Schema
    conditional validation can express (e.g., non-empty arrays).
    The schema handles required-field presence via if/then;
    this function checks semantic completeness.
    """
    profile = block.get("profile")
    if profile != "research":
        return

    # topology.negative_space must be non-empty
    topo = block.get("topology")
    if isinstance(topo, dict):
        neg = topo.get("negative_space")
        if isinstance(neg, list) and len(neg) == 0:
            result.error(
                "/topology/negative_space",
                "Profile 'research' requires non-empty negative_space. "
                "What does this block NOT claim?"
            )

        inv = topo.get("invariants")
        if isinstance(inv, dict):
            must_hold = inv.get("must_hold")
            if isinstance(must_hold, list) and len(must_hold) == 0:
                result.error(
                    "/topology/invariants/must_hold",
                    "Profile 'research' requires non-empty invariants.must_hold. "
                    "What conditions must remain true?"
                )

    # edges must be non-empty
    edges = block.get("edges")
    if isinstance(edges, list) and len(edges) == 0:
        result.error(
            "/edges",
            "Profile 'research' requires at least one edge."
        )

    # path must be non-empty
    path = block.get("path")
    if isinstance(path, list) and len(path) == 0:
        result.error(
            "/path",
            "Profile 'research' requires a non-empty path."
        )


def check_digest_topology_coherence(block, result):
    """Flag if digest contains strong claims that contradict negative_space.

    Uses keyword matching: if digest says "proves X" and negative_space
    declares "X_not_measured", flag it as a possible overclaim.
    Handles StatusClaim items (plain string or {claim, status}).
    """
    signal = block.get("signal")
    if not isinstance(signal, dict):
        return
    digest = signal.get("digest", "")
    if not isinstance(digest, str) or len(digest) == 0:
        return

    topo = block.get("topology")
    if not isinstance(topo, dict):
        return
    neg_space = topo.get("negative_space")
    if not isinstance(neg_space, list) or len(neg_space) == 0:
        return

    digest_lower = digest.lower()

    for pattern, claim_word in STRONG_CLAIM_PATTERNS:
        match = pattern.search(digest)
        if not match:
            continue

        # Context window around the strong claim word
        claim_context = digest_lower[
            max(0, match.start() - 40):match.end() + 40
        ]

        for neg_item in neg_space:
            neg_text = extract_claim_text(neg_item)
            if not neg_text:
                continue
            neg_lower = neg_text.lower()

            # Extract keywords from negative space entry
            neg_keywords = set(re.split(r'[_\s\-/]+', neg_lower))
            neg_keywords.discard("")

            # Check if any keyword (4+ chars) appears near the strong claim
            for kw in neg_keywords:
                if len(kw) >= 4 and kw in claim_context:
                    result.warn(
                        "/signal/digest vs /topology/negative_space",
                        f"Digest uses strong language ('{claim_word}') near "
                        f"keyword '{kw}', but negative_space declares "
                        f"'{neg_text}'. Possible overclaim."
                    )
                    break  # one warning per negative_space item


def check_edge_direction(block, result):
    """For prerequisite_of edges, warn if 'from' appears AFTER 'to' in path.

    Convention: from=prerequisite, to=dependent.
    The prerequisite should come before the dependent in reading order.
    """
    path = block.get("path")
    if not isinstance(path, list) or len(path) == 0:
        return

    edges = block.get("edges", [])
    if not isinstance(edges, list):
        return

    # Build position map (first occurrence)
    pos = {}
    for i, node_id in enumerate(path):
        if isinstance(node_id, str) and node_id not in pos:
            pos[node_id] = i

    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            continue
        rel = edge.get("rel")
        if rel != "prerequisite_of":
            continue

        from_id = edge.get("from")
        to_id = edge.get("to")

        if from_id in pos and to_id in pos:
            if pos[from_id] > pos[to_id]:
                result.warn(
                    f"/edges[{i}]",
                    f"prerequisite_of edge: '{from_id}' "
                    f"(path position {pos[from_id]}) appears AFTER "
                    f"'{to_id}' (position {pos[to_id]}) in path. "
                    f"Prerequisite should come before dependent."
                )


def check_reproducibility(block, result):
    """For type=experiment with profile=research, check reproduce quality.

    The schema enforces that reproduce is present via if/then.
    This checks semantic completeness of the reproduce section.
    """
    block_type = block.get("type")
    profile = block.get("profile")

    if block_type != "experiment" or profile != "research":
        return

    reproduce = block.get("reproduce")
    if not isinstance(reproduce, dict):
        # Schema layer should catch missing reproduce; semantic layer
        # flags it only if schema validation is skipped
        return

    protocol = reproduce.get("protocol")
    if not protocol or (isinstance(protocol, str) and len(protocol.strip()) == 0):
        result.warn(
            "/reproduce/protocol",
            "Reproduce section has empty protocol. "
            "How should an agent reproduce this?"
        )

    expected = reproduce.get("expected_outcome")
    if not expected or (isinstance(expected, str) and len(expected.strip()) == 0):
        result.warn(
            "/reproduce/expected_outcome",
            "Reproduce section has empty expected_outcome."
        )


def check_orphan_nodes(block, result):
    """Detect nodes with no edges pointing to or from them.

    Orphan nodes in blocks with 3+ nodes suggest incomplete graph structure.
    Gaps and predictions are exempt -- they are often intentionally unconnected.
    """
    nodes = block.get("nodes", {})
    edges = block.get("edges", [])

    if not isinstance(nodes, dict) or not isinstance(edges, list):
        return
    if len(nodes) <= 2:
        return

    connected = set()
    for edge in edges:
        if isinstance(edge, dict):
            connected.add(edge.get("from"))
            connected.add(edge.get("to"))

    orphans = set(nodes.keys()) - connected
    for orphan in orphans:
        node = nodes.get(orphan, {})
        if isinstance(node, dict):
            node_type = node.get("type", "")
            if node_type not in ("gap", "prediction"):
                result.warn(
                    f"/nodes/{orphan}",
                    "Orphan node (no edges). "
                    "Consider connecting it to the graph."
                )


def check_crystal_stage_consistency(block, result):
    """Check crystal stage against other fields."""
    crystal = block.get("crystal")
    if not isinstance(crystal, dict):
        return

    stage = crystal.get("stage")

    if stage == "published" and block.get("doi") is None:
        result.warn(
            "/crystal/stage",
            "Stage is 'published' but no DOI assigned."
        )

    if stage == "retracted":
        result.note(
            "/crystal/stage",
            "Block is RETRACTED. Downstream consumers should not rely on it."
        )

    if stage == "superseded":
        result.note(
            "/crystal/stage",
            "Block is SUPERSEDED. Check refs for the replacement."
        )


def validate_semantic_layer(block, result):
    """Run all semantic checks on a block."""
    if not isinstance(block, dict):
        result.error("/", "Root must be a JSON object. Semantic checks skipped.")
        return

    check_edge_referential_integrity(block, result)
    check_path_consistency(block, result)
    check_temperature_consistency(block, result)
    check_profile_enforcement(block, result)
    check_digest_topology_coherence(block, result)
    check_edge_direction(block, result)
    check_reproducibility(block, result)
    check_orphan_nodes(block, result)
    check_crystal_stage_consistency(block, result)

    # Block statistics
    nodes = block.get("nodes", {})
    edges = block.get("edges", [])
    n_nodes = len(nodes) if isinstance(nodes, dict) else 0
    n_edges = len(edges) if isinstance(edges, list) else 0
    result.note(
        "/",
        f"Block '{block.get('id', '?')}': {n_nodes} nodes, {n_edges} edges, "
        f"type={block.get('type', '?')}, t={block.get('signal', {}).get('t', '?')}, "
        f"profile={block.get('profile', 'none')}"
    )


# ============================================================
# Main orchestration
# ============================================================

def validate_block(block, schema=None, filename=""):
    """Run both validation layers on a parsed block. Returns ValidationResult."""
    result = ValidationResult(filename=filename)

    # Layer 1: Schema
    if schema is not None:
        validate_schema_layer(block, schema, result)
    else:
        result.schema_ok = None
        result.note("/", "No schema provided. Schema validation skipped.")

    # Layer 2: Semantic
    validate_semantic_layer(block, result)

    return result


def validate_file(filepath, schema=None):
    """Load and validate a single JSON file. Returns ValidationResult."""
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        result = ValidationResult(filename=filename)
        result.error("/", f"File not found: {filepath}")
        return result

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            block = json.load(f)
    except json.JSONDecodeError as e:
        result = ValidationResult(filename=filename)
        result.schema_error("/", f"Invalid JSON: {e}")
        result.schema_ok = False
        return result

    return validate_block(block, schema=schema, filename=filename)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "OMPU Block v0.2 Validator -- "
            "two-layer validation (schema + semantic)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "file", nargs="?",
        help="JSON file to validate."
    )
    parser.add_argument(
        "--batch",
        metavar="DIR",
        help="Validate all .json files in DIR."
    )
    parser.add_argument(
        "--schema",
        metavar="PATH",
        help=(
            "Path to JSON Schema file. "
            "Default: ../schemas/ompu_block_v0.2.json"
        )
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show info-level messages."
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Machine-readable JSON output."
    )

    args = parser.parse_args()

    if args.file is None and args.batch is None:
        parser.print_help()
        sys.exit(2)

    # Load schema
    schema_path = args.schema if args.schema else DEFAULT_SCHEMA_PATH
    schema, schema_err = load_schema(schema_path)
    if schema_err:
        if args.schema:
            # Explicit --schema flag: hard error
            print(f"ERROR: {schema_err}", file=sys.stderr)
            sys.exit(2)
        else:
            # Default path missing: warn and continue without schema
            print(
                f"WARNING: {schema_err}. Running semantic checks only.",
                file=sys.stderr
            )

    if not HAVE_JSONSCHEMA and schema is not None:
        print(
            "WARNING: jsonschema library not installed. "
            "Schema validation will use fallback structural checks. "
            "For full Draft 2020-12 validation: pip install jsonschema",
            file=sys.stderr
        )

    # Collect files to validate
    files = []
    if args.batch:
        batch_dir = args.batch
        if not os.path.isdir(batch_dir):
            print(f"ERROR: Not a directory: {batch_dir}", file=sys.stderr)
            sys.exit(2)
        for fname in sorted(os.listdir(batch_dir)):
            if fname.endswith(".json"):
                files.append(os.path.join(batch_dir, fname))
        if not files:
            print(f"No .json files found in {batch_dir}", file=sys.stderr)
            sys.exit(2)
    else:
        files.append(args.file)

    # Run validation
    all_results = []
    any_invalid = False

    for filepath in files:
        r = validate_file(filepath, schema=schema)
        all_results.append(r)
        if not r.valid:
            any_invalid = True

    # Output
    if args.json_output:
        output = {
            "validator": "ompu-block-v0.2",
            "schema_engine": "jsonschema" if HAVE_JSONSCHEMA else "fallback",
            "results": [r.to_dict() for r in all_results],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        for i, r in enumerate(all_results):
            if i > 0:
                print()  # separator between files
            for line in r.report_lines(verbose=args.verbose):
                print(line)

        # Batch summary
        if len(all_results) > 1:
            n_valid = sum(1 for r in all_results if r.valid)
            n_total = len(all_results)
            print()
            print(f"BATCH   {n_valid}/{n_total} valid")

    sys.exit(1 if any_invalid else 0)


if __name__ == "__main__":
    main()
