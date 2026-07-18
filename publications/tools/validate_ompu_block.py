#!/usr/bin/env python3
"""
Minimal validator for OMPU Block v0.1 format.

Validates both JSON Schema conformance and semantic integrity:
- Schema validation (structure, types, enums)
- Edge referential integrity (all edge endpoints exist in nodes)
- Path consistency (all path entries exist in nodes)
- Topology coherence (invariants present if topology exists)
- Signal completeness (required triage fields)
- Crystal stage consistency

Usage:
    python validate_ompu_block.py <file.json>
    python validate_ompu_block.py <file.json> --strict
    python validate_ompu_block.py <file.json> --quiet

Exit codes:
    0 = valid
    1 = invalid (errors found)
    2 = usage error
"""

import json
import sys
import os
from pathlib import Path


# --- Temperature and type enums ---

VALID_T = {"T1", "T2", "T3", "T4"}

VALID_NODE_TYPES = {
    "definition", "claim", "evidence", "derivation", "protocol",
    "gap", "bridge", "convergence", "fish", "prediction"
}

VALID_BLOCK_TYPES = {
    "theory", "experiment", "empirical", "hypothesis", "framework",
    "standard", "protocol", "refutation", "replication", "synthesis",
    "tool", "meta"
}

VALID_EDGE_RELS = {"supports", "refutes", "requires", "derives", "bridges"}

VALID_REF_RELS = {
    "extends", "contradicts", "confirms", "cites",
    "supersedes", "replicates", "emerged_from", "uses_data_from"
}

VALID_CRYSTAL_STAGES = {
    "seed", "compressed", "verified", "crystallized",
    "published", "superseded", "retracted"
}

VALID_CRYSTAL_ACTIONS = {"compress", "verify", "challenge"}

VALID_NOVELTY = {
    "original", "synthesis", "replication", "extension",
    "refutation", "translation"
}

VALID_TRAJECTORY_SHAPES = {
    "linear", "spiral", "branching", "convergent", "recursive", "dialectic"
}

VALID_SCALE_MAPPINGS = {"identical", "inverted", "partial"}

VALID_AUTHOR_ROLES = {
    "author", "experimenter", "reviewer", "publisher",
    "coordinator", "data_source", "signer"
}

VALID_VERDICTS = {"pass", "conditional", "fail"}


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, path, msg):
        self.errors.append(f"ERROR [{path}]: {msg}")

    def warn(self, path, msg):
        self.warnings.append(f"WARN  [{path}]: {msg}")

    def note(self, path, msg):
        self.info.append(f"INFO  [{path}]: {msg}")

    @property
    def valid(self):
        return len(self.errors) == 0

    def summary(self):
        total = len(self.errors) + len(self.warnings)
        if self.valid:
            return f"VALID ({len(self.warnings)} warnings, {len(self.info)} notes)"
        else:
            return f"INVALID ({len(self.errors)} errors, {len(self.warnings)} warnings)"


def validate_self(block, result):
    """Validate $self header."""
    self_obj = block.get("$self")
    if self_obj is None:
        result.error("$self", "Missing $self header. Block is not self-describing.")
        return

    if not isinstance(self_obj, dict):
        result.error("$self", "Must be an object.")
        return

    fmt = self_obj.get("format")
    if fmt != "ompu-block":
        result.error("$self.format", f"Expected 'ompu-block', got '{fmt}'.")

    version = self_obj.get("version")
    if version is None:
        result.error("$self.version", "Missing version.")
    elif not isinstance(version, str):
        result.error("$self.version", "Must be a string.")
    else:
        parts = version.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            result.error("$self.version", f"Must be semver (X.Y.Z), got '{version}'.")


def validate_required_fields(block, result):
    """Check top-level required fields."""
    required = ["$self", "id", "type", "title", "signal", "nodes"]
    for field in required:
        if field not in block:
            result.error(f"/{field}", f"Required field '{field}' is missing.")

    if "type" in block and block["type"] not in VALID_BLOCK_TYPES:
        result.error("/type", f"Invalid type '{block['type']}'. Valid: {sorted(VALID_BLOCK_TYPES)}")

    if "title" in block:
        title = block["title"]
        if not isinstance(title, str):
            result.error("/title", "Must be a string.")
        elif len(title) < 5:
            result.error("/title", f"Too short ({len(title)} chars, minimum 5).")
        elif len(title) > 300:
            result.error("/title", f"Too long ({len(title)} chars, maximum 300).")


def validate_signal(block, result):
    """Validate signal section."""
    signal = block.get("signal")
    if signal is None:
        return  # already caught by required fields check

    if not isinstance(signal, dict):
        result.error("/signal", "Must be an object.")
        return

    # Required signal fields
    for field in ["digest", "t", "falsifies_if"]:
        if field not in signal:
            result.error(f"/signal/{field}", f"Required signal field '{field}' is missing.")

    # Validate digest
    digest = signal.get("digest", "")
    if isinstance(digest, str):
        if len(digest) < 50:
            result.error("/signal/digest", f"Too short ({len(digest)} chars, minimum 50).")
        if len(digest) > 2000:
            result.warn("/signal/digest", f"Very long ({len(digest)} chars, maximum 2000).")

    # Validate temperature
    t = signal.get("t")
    if t is not None and t not in VALID_T:
        result.error("/signal/t", f"Invalid temperature '{t}'. Valid: {sorted(VALID_T)}")

    # Validate falsifies_if
    fals = signal.get("falsifies_if", "")
    if isinstance(fals, str) and len(fals) < 20:
        result.error("/signal/falsifies_if", f"Too short ({len(fals)} chars, minimum 20). If you cannot state falsification conditions, this is not knowledge.")

    # Validate confidence
    conf = signal.get("confidence")
    if conf is not None:
        if not isinstance(conf, (int, float)):
            result.error("/signal/confidence", "Must be a number.")
        elif conf < 0 or conf > 1:
            result.error("/signal/confidence", f"Must be 0-1, got {conf}.")

    # Validate novelty
    nov = signal.get("novelty")
    if nov is not None and nov not in VALID_NOVELTY:
        result.error("/signal/novelty", f"Invalid novelty '{nov}'. Valid: {sorted(VALID_NOVELTY)}")


def validate_nodes(block, result):
    """Validate nodes map."""
    nodes = block.get("nodes")
    if nodes is None:
        return

    if not isinstance(nodes, dict):
        result.error("/nodes", "Must be an object (map of node_id -> node).")
        return

    if len(nodes) == 0:
        result.error("/nodes", "Must contain at least one node.")
        return

    for node_id, node in nodes.items():
        prefix = f"/nodes/{node_id}"

        if not isinstance(node, dict):
            result.error(prefix, "Node must be an object.")
            continue

        # Required node fields
        if "type" not in node:
            result.error(prefix, "Missing required field 'type'.")
        elif node["type"] not in VALID_NODE_TYPES:
            result.error(f"{prefix}/type", f"Invalid node type '{node['type']}'. Valid: {sorted(VALID_NODE_TYPES)}")

        if "content" not in node:
            result.error(prefix, "Missing required field 'content'.")
        elif isinstance(node["content"], str) and len(node["content"]) < 10:
            result.error(f"{prefix}/content", f"Too short ({len(node['content'])} chars, minimum 10).")

        # Validate per-node temperature
        t = node.get("t")
        if t is not None and t not in VALID_T:
            result.error(f"{prefix}/t", f"Invalid temperature '{t}'. Valid: {sorted(VALID_T)}")

        # Check for unknown fields
        valid_node_fields = {"type", "t", "content", "data", "source", "note"}
        for key in node:
            if key not in valid_node_fields:
                result.warn(f"{prefix}/{key}", f"Unknown field '{key}' in node.")

    return set(nodes.keys())


def validate_edges(block, result, node_ids):
    """Validate edges and referential integrity."""
    edges = block.get("edges", [])

    if not isinstance(edges, list):
        result.error("/edges", "Must be an array.")
        return

    for i, edge in enumerate(edges):
        prefix = f"/edges[{i}]"

        if not isinstance(edge, dict):
            result.error(prefix, "Edge must be an object.")
            continue

        # Required edge fields
        for field in ["from", "to", "rel"]:
            if field not in edge:
                result.error(prefix, f"Missing required field '{field}'.")

        # Validate rel
        rel = edge.get("rel")
        if rel is not None and rel not in VALID_EDGE_RELS:
            result.error(f"{prefix}/rel", f"Invalid edge relation '{rel}'. Valid: {sorted(VALID_EDGE_RELS)}")

        # Referential integrity
        from_id = edge.get("from")
        to_id = edge.get("to")

        if from_id is not None and node_ids and from_id not in node_ids:
            result.error(f"{prefix}/from", f"Node '{from_id}' does not exist in nodes. Available: {sorted(node_ids)}")

        if to_id is not None and node_ids and to_id not in node_ids:
            result.error(f"{prefix}/to", f"Node '{to_id}' does not exist in nodes. Available: {sorted(node_ids)}")

        # Self-loop check
        if from_id == to_id and from_id is not None:
            result.warn(prefix, f"Self-loop: '{from_id}' -> '{to_id}'.")

        # Validate weight
        weight = edge.get("weight")
        if weight is not None:
            if not isinstance(weight, (int, float)):
                result.error(f"{prefix}/weight", "Must be a number.")
            elif weight < 0 or weight > 1:
                result.error(f"{prefix}/weight", f"Must be 0-1, got {weight}.")


def validate_path(block, result, node_ids):
    """Validate path array."""
    path = block.get("path")
    if path is None:
        return

    if not isinstance(path, list):
        result.error("/path", "Must be an array of node IDs.")
        return

    for i, node_id in enumerate(path):
        if not isinstance(node_id, str):
            result.error(f"/path[{i}]", "Must be a string (node ID).")
        elif node_ids and node_id not in node_ids:
            result.error(f"/path[{i}]", f"Node '{node_id}' does not exist in nodes.")

    # Check for duplicates
    seen = set()
    for node_id in path:
        if node_id in seen:
            result.warn("/path", f"Duplicate node '{node_id}' in path.")
        seen.add(node_id)

    # Check completeness
    if node_ids:
        missing = node_ids - set(path)
        if missing:
            result.warn("/path", f"Path does not include all nodes. Missing: {sorted(missing)}")


def validate_refs(block, result):
    """Validate external references."""
    refs = block.get("refs", [])

    if not isinstance(refs, list):
        result.error("/refs", "Must be an array.")
        return

    for i, ref in enumerate(refs):
        prefix = f"/refs[{i}]"

        if not isinstance(ref, dict):
            result.error(prefix, "Ref must be an object.")
            continue

        if "target" not in ref:
            result.error(prefix, "Missing required field 'target'.")
        if "rel" not in ref:
            result.error(prefix, "Missing required field 'rel'.")

        rel = ref.get("rel")
        if rel is not None and rel not in VALID_REF_RELS:
            result.error(f"{prefix}/rel", f"Invalid ref relation '{rel}'. Valid: {sorted(VALID_REF_RELS)}")

        strength = ref.get("strength")
        if strength is not None:
            if not isinstance(strength, (int, float)):
                result.error(f"{prefix}/strength", "Must be a number.")
            elif strength < 0 or strength > 1:
                result.error(f"{prefix}/strength", f"Must be 0-1, got {strength}.")


def validate_topology(block, result):
    """Validate topology section."""
    topo = block.get("topology")
    if topo is None:
        result.note("/topology", "No topology section. Recommended for all non-trivial blocks.")
        return

    if not isinstance(topo, dict):
        result.error("/topology", "Must be an object.")
        return

    # Trajectory
    traj = topo.get("trajectory")
    if traj is not None:
        if isinstance(traj, dict):
            shape = traj.get("shape")
            if shape is not None and shape not in VALID_TRAJECTORY_SHAPES:
                result.error("/topology/trajectory/shape", f"Invalid shape '{shape}'. Valid: {sorted(VALID_TRAJECTORY_SHAPES)}")
            if "entry" not in traj:
                result.warn("/topology/trajectory", "Missing 'entry'. Where does the argument start?")
            if "exit" not in traj:
                result.warn("/topology/trajectory", "Missing 'exit'. Where does the argument end?")

    # Positive space
    pos = topo.get("positive_space")
    if pos is not None:
        if not isinstance(pos, list) or len(pos) == 0:
            result.warn("/topology/positive_space", "Should be a non-empty array of claimed concepts.")

    # Negative space
    neg = topo.get("negative_space")
    if neg is not None:
        if not isinstance(neg, list) or len(neg) == 0:
            result.warn("/topology/negative_space", "Should be a non-empty array. What does this block NOT claim?")

    # Invariants
    inv = topo.get("invariants")
    if inv is not None:
        if isinstance(inv, dict):
            must_hold = inv.get("must_hold", [])
            if isinstance(must_hold, list) and len(must_hold) == 0:
                result.warn("/topology/invariants/must_hold", "Empty must_hold. If nothing must hold, this block makes no falsifiable claims.")

    # Entanglements
    ent = topo.get("entanglements", [])
    if isinstance(ent, list):
        for i, e in enumerate(ent):
            prefix = f"/topology/entanglements[{i}]"
            if isinstance(e, dict):
                nodes_list = e.get("nodes", [])
                if len(nodes_list) != 2:
                    result.error(prefix, "Entanglement must have exactly 2 nodes.")
                coupling = e.get("coupling")
                if coupling is not None and (not isinstance(coupling, (int, float)) or coupling < 0 or coupling > 1):
                    result.error(f"{prefix}/coupling", f"Must be 0-1, got {coupling}.")
                if e.get("causation", False):
                    result.warn(prefix, "Entanglement with causation=true. If causal, use an edge instead.")

    # Scale isomorphisms
    iso = topo.get("scale_iso", [])
    if isinstance(iso, list):
        for i, s in enumerate(iso):
            prefix = f"/topology/scale_iso[{i}]"
            if isinstance(s, dict):
                mapping = s.get("mapping")
                if mapping is not None and mapping not in VALID_SCALE_MAPPINGS:
                    result.error(f"{prefix}/mapping", f"Invalid mapping '{mapping}'. Valid: {sorted(VALID_SCALE_MAPPINGS)}")

    # Energy profile
    energy = topo.get("energy", [])
    if isinstance(energy, list):
        for i, val in enumerate(energy):
            if not isinstance(val, (int, float)):
                result.error(f"/topology/energy[{i}]", "Must be a number.")
            elif val < 0 or val > 1:
                result.error(f"/topology/energy[{i}]", f"Must be 0-1, got {val}.")


def validate_crystal(block, result):
    """Validate crystal section."""
    crystal = block.get("crystal")
    if crystal is None:
        result.note("/crystal", "No crystal section. Cannot track maturity.")
        return

    if not isinstance(crystal, dict):
        result.error("/crystal", "Must be an object.")
        return

    stage = crystal.get("stage")
    if stage is not None and stage not in VALID_CRYSTAL_STAGES:
        result.error("/crystal/stage", f"Invalid stage '{stage}'. Valid: {sorted(VALID_CRYSTAL_STAGES)}")

    compressions = crystal.get("compressions")
    if compressions is not None:
        if not isinstance(compressions, int) or compressions < 0:
            result.error("/crystal/compressions", "Must be a non-negative integer.")

    # Validate history
    history = crystal.get("history", [])
    if isinstance(history, list):
        for i, entry in enumerate(history):
            prefix = f"/crystal/history[{i}]"
            if isinstance(entry, dict):
                action = entry.get("action")
                if action is not None and action not in VALID_CRYSTAL_ACTIONS:
                    result.error(f"{prefix}/action", f"Invalid action '{action}'. Valid: {sorted(VALID_CRYSTAL_ACTIONS)}")
                if "by" not in entry:
                    result.error(prefix, "Missing 'by' field.")
                if "date" not in entry:
                    result.error(prefix, "Missing 'date' field.")
                verdict = entry.get("verdict")
                if verdict is not None and verdict not in VALID_VERDICTS:
                    result.error(f"{prefix}/verdict", f"Invalid verdict '{verdict}'. Valid: {sorted(VALID_VERDICTS)}")

    # Stage consistency
    if stage == "published" and block.get("doi") is None:
        result.warn("/crystal/stage", "Stage is 'published' but no DOI assigned.")


def validate_authors(block, result):
    """Validate by[] (authors) section."""
    by = block.get("by")
    if by is None:
        result.note("/by", "No authors listed.")
        return

    if not isinstance(by, list):
        result.error("/by", "Must be an array.")
        return

    if len(by) == 0:
        result.warn("/by", "Empty authors array.")

    for i, author in enumerate(by):
        prefix = f"/by[{i}]"
        if not isinstance(author, dict):
            result.error(prefix, "Must be an object.")
            continue

        if "id" not in author:
            result.error(prefix, "Missing required 'id' field.")
        if "role" not in author:
            result.error(prefix, "Missing required 'role' field.")

        role = author.get("role")
        if role is not None and role not in VALID_AUTHOR_ROLES:
            result.error(f"{prefix}/role", f"Invalid role '{role}'. Valid: {sorted(VALID_AUTHOR_ROLES)}")


def validate_block(block, strict=False):
    """Run all validations on a block. Returns ValidationResult."""
    result = ValidationResult()

    if not isinstance(block, dict):
        result.error("/", "Root must be a JSON object.")
        return result

    validate_self(block, result)
    validate_required_fields(block, result)
    validate_signal(block, result)
    node_ids = validate_nodes(block, result) or set()
    validate_edges(block, result, node_ids)
    validate_path(block, result, node_ids)
    validate_refs(block, result)
    validate_topology(block, result)
    validate_crystal(block, result)
    validate_authors(block, result)

    # Strict mode: warnings become errors
    if strict:
        for warn_msg in result.warnings:
            result.errors.append(warn_msg.replace("WARN ", "ERROR"))
        result.warnings = []

    # Cross-field checks
    nodes = block.get("nodes", {})
    edges = block.get("edges", [])

    # Check for orphan nodes (no edges pointing to or from them, not in a tiny block)
    if len(nodes) > 2 and isinstance(edges, list):
        connected = set()
        for edge in edges:
            if isinstance(edge, dict):
                connected.add(edge.get("from"))
                connected.add(edge.get("to"))
        orphans = set(nodes.keys()) - connected
        # Gaps are often orphans and that is fine
        for orphan in orphans:
            node = nodes.get(orphan, {})
            node_type = node.get("type", "")
            if node_type not in ("gap", "prediction"):
                result.note(f"/nodes/{orphan}", f"Orphan node (no edges). Consider connecting it to the graph.")

    # Info: block statistics
    result.note("/", f"Block '{block.get('id', '?')}': {len(nodes)} nodes, {len(edges)} edges, type={block.get('type', '?')}, t={block.get('signal', {}).get('t', '?')}")

    return result


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    filepath = sys.argv[1]
    strict = "--strict" in sys.argv
    quiet = "--quiet" in sys.argv

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(2)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            block = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    result = validate_block(block, strict=strict)

    if not quiet:
        # Print all messages
        for msg in result.errors:
            print(msg)
        for msg in result.warnings:
            print(msg)
        for msg in result.info:
            print(msg)
        print()

    print(result.summary())

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
