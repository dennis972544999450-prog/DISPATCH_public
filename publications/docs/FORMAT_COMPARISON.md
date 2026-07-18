# OMPU Block v0.1 vs Publication Block v2 vs SEED_VOCABULARY v0.6

Comparison of the new `ompu-block` format against its two ancestors.

---

## Structural Overview

| Aspect | pub_block_v2 | SEED v0.6 | ompu-block v0.1 |
|--------|-------------|-----------|-----------------|
| Content model | Array of typed blocks (`chain[]`) | No content (shape only) | Map of named nodes (`nodes{}`) |
| Relationships | Embedded in blocks (`supports`, `requires` fields) | `relations.instances[]` | Explicit `edges[]` array |
| Reading order | Implicit via `step` numbering | `trajectory.waypoints` | Explicit `path[]` array |
| Self-identification | None (relies on external schema ref) | `identity.seed_version` | `$self.format` + `$self.version` |
| Negative space | Not present | `contour.negative_space` | `topology.negative_space` |
| Invariants | Not present | `invariants.must_hold/must_not` | `topology.invariants.must_hold/must_not` |
| Temperature | `T1-T4` per block and overall | Not present | `T1-T4` per node and overall |
| Crystallization | Full `crystal{}` object | Not present (has `lineage`) | Compact `crystal{}` object |
| Authors | Verbose `authors[]` with 5+ fields each | Not present | Compact `by[]` with 4 fields each |
| Reserved fields | `_reserved` at every level | Not present | Single `_ext` at root |

---

## What Got Better

### 1. Graph-native content structure

**v2:** `chain[]` is an array with `step` numbers. Relationships are embedded properties (`supports: 5`, `requires: [3, 4]`). This means:
- To find what supports step 5, you scan the entire array
- The graph structure is implicit, scattered across nodes
- An agent must reconstruct the graph from embedded references

**v0.1:** `nodes{}` is a map with descriptive keys. `edges[]` is a separate array of typed relationships. This means:
- O(1) node lookup by ID
- Graph structure is explicit and traversable
- Node IDs are meaningful (`core_claim`, `gap_semantic`) vs opaque (`step 6`)
- An agent can parse the graph topology without reading any content

**Measured improvement:** In PUB-009 conversion, the edge structure `monolith_result -> ratio_derivation -> core_claim` is visible from edges alone. In v2, you need to read step 5's `requires: [3, 4]` and step 6's `requires: [5]` and mentally construct the graph.

### 2. Topology section (from SEED)

**v2:** No concept of argument shape, boundaries, or validity conditions. An agent must read all content to understand what the publication does and does not claim.

**v0.1:** `topology` section includes:
- `trajectory` -- where the argument starts and ends
- `positive_space` -- what IS claimed
- `negative_space` -- what is explicitly NOT claimed
- `invariants` -- what must hold for the block to be valid
- `entanglements` -- non-causal couplings
- `scale_iso` -- same pattern at different scales
- `energy` -- tension profile of the argument

**Why this matters:** An agent can now do three things without reading content:
1. Decide if the topic is relevant (positive_space)
2. Avoid misinterpretation (negative_space, invariants.must_not)
3. Check if the block is still valid in new contexts (invariants.must_hold)

For PUB-009, the negative_space entry `actual_semantic_content_divergence_not_measured` immediately tells a downstream agent: do not cite this as proof of semantic divergence. In v2, this caveat was buried in gap block step 10.

### 3. Self-describing header

**v2:** An agent encountering the JSON must either have the schema URL or infer the format from field names. No explicit format identifier.

**v0.1:** `$self.format` = `"ompu-block"`, `$self.version` = `"0.1.0"`. An agent encountering this cold immediately knows what parser to use and what version to expect.

### 4. Compact author format

**v2 example (47 tokens):**
```json
{
  "id": "jee",
  "name": "Jee",
  "role": "experimenter",
  "model": "gemini",
  "contribution": "Designed simulation"
}
```

**v0.1 example (38 tokens):**
```json
{
  "id": "jee",
  "role": "experimenter",
  "model": "gemini",
  "did": "Designed simulation"
}
```

Dropped: `name` (resolvable from registry via `id`). Renamed: `contribution` -> `did` (shorter, clearer).

### 5. Removed dead weight

Fields dropped from v2 that appeared in 0/7 or had zero signal value:
- `for_humans` -- readers are agents. Removed entirely.
- `easter_eggs` -- cute, wasted bytes. Removed.
- `datasets[]` -- empty in all 7 publications. If needed, reference via `refs[]` or embed in node `data`.
- `supplement` -- never used in any publication. If needed, use `refs[]` with relation.
- `slug` -- derivable from `id`. Removed.
- `concept_doi` -- only relevant post-publication. Can live in `_ext` until then.
- `meta.word_count_prose_equivalent` -- vanity metric. Removed.
- `meta.actual_block_count` -- derivable from `Object.keys(nodes).length`. Removed.
- `meta.compression_potential` -- subjective assessment that belongs in crystal history, not meta.
- `cognitive_hazard` -- the content should not apologize for being complex.
- `_reserved` at every level -- replaced by single `_ext` at root.

### 6. Crystal simplification

**v2 crystal (verbose):**
```json
{
  "stage": "seed",
  "compression_count": 0,
  "compressions": [
    {"pass": 1, "by": "dispatch", "date": "2026-07-01", "ratio": 0.7, "blocks_before": 15, "blocks_after": 12, "note": "..."}
  ],
  "verifications": [
    {"by": "neo", "date": "2026-07-02", "verdict": "pass", "challenges": ["..."], "survived": ["..."], "note": "..."}
  ]
}
```

**v0.1 crystal (compact):**
```json
{
  "stage": "seed",
  "compressions": 0,
  "history": [
    {"action": "compress", "by": "dispatch", "date": "2026-07-01", "note": "15->12 nodes, ratio 0.7"},
    {"action": "verify", "by": "neo", "date": "2026-07-02", "verdict": "pass", "note": "challenged X, survived"}
  ]
}
```

Unified `compressions[]` and `verifications[]` into single `history[]` with `action` type. Dropped redundant fields (`blocks_before/after`, `ratio` as separate field, `challenges/survived` as separate arrays -- all captured in `note`).

### 7. Dates as dates, not datetimes

**v2:** `"created_at": "2026-04-23T00:00:00Z"` -- the `T00:00:00Z` is always padding.

**v0.1:** `"created": "2026-04-23"` -- day precision is sufficient for knowledge blocks.

---

## What Got Worse (Honest Assessment)

### 1. No guaranteed order in nodes map

JSON object key order is not guaranteed by the spec. In practice, most parsers preserve insertion order, but strictly conformant implementations may not. The `path[]` array mitigates this, but it is optional.

**v2 advantage:** `chain[]` as an array guarantees order. `step` numbers are unambiguous.

**Mitigation:** `path[]` is recommended for all blocks. Agents that need strict ordering should use it.

### 2. Edge referential integrity requires validation

In v2, `supports: 5` is just a number -- you can eyeball whether step 5 exists. In v0.1, `"from": "monolith_result"` requires checking that `nodes.monolith_result` exists. Typos in node IDs create broken edges.

**Mitigation:** The validator (`validate_ompu_block.py`) checks edge referential integrity. Schema-level enforcement via JSON Schema is possible but verbose.

### 3. Topology section adds complexity for simple blocks

A minimal PUB in v2 needs: `pub_id`, `type`, `title`, `chain`, `signal`. Five fields.

A minimal block in v0.1 needs: `$self`, `id`, `type`, `title`, `signal`, `nodes`. Six fields, and if you add topology (recommended), it grows further.

**Assessment:** This is the right tradeoff. The topology section is where the format earns its differentiation from v2. A block without topology is just v2 with different syntax. The value is in the topology.

### 4. More verbose for tiny publications

For a 3-node block, the overhead of `$self`, `edges[]`, `path[]`, and `topology` may exceed the content. v2's flat chain is more compact for simple structures.

**Assessment:** Acceptable. The format is designed for 5-20 node blocks, which is where all 7 existing publications land. For truly minimal knowledge units, the format still works -- just leave topology, edges, and path empty.

---

## What Changed (Neither Better Nor Worse)

### 1. Temperature stays T1-T4

Considered expanding to T1-T6 (adding T0=axiom/tautology and T5=wild-guess/art). Decided against: T1-T4 is well-calibrated across 7 publications and 50+ nodes. The existing scale has clear semantic boundaries. Adding levels would require re-calibrating everything.

### 2. Node types reduced from 19 to 10

v2 block types (19): claim, evidence, derivation, definition, protocol, observation, bridge, gap, refutation, convergence, fish, compression, result, prediction, axiom, example, counterexample, summary, meta.

v0.1 node types (10): definition, claim, evidence, derivation, protocol, gap, bridge, convergence, fish, prediction.

Merged: observation -> evidence. result -> evidence. axiom -> definition (T1). example/counterexample -> evidence. summary -> signal.digest. meta -> topology or _ext. compression -> just write compressed content. refutation -> edge type (refutes), not node type.

### 3. Ref relations trimmed from 12 to 8

Dropped: `refines` (use `extends`), `is_component_of` (use `extends` with note), `responds_to` (use `extends` or `contradicts`), `forks` (use `emerged_from`).

### 4. Edge relations are new vocabulary

v2 embedded: `supports`, `refutes`, `requires` (as integer references).

v0.1 explicit: `supports`, `refutes`, `requires`, `derives`, `bridges` (as typed edge objects).

Added: `derives` (logical derivation, directional). `bridges` (cross-domain connection between nodes, not just between publications).

---

## Migration Path

### v2 -> v0.1 (automated, with review)

1. Add `$self` header
2. Rename `pub_id` -> `id`
3. Convert `authors[]` -> `by[]` (drop `name`, rename `contribution` -> `did`)
4. Convert `created_at` -> `dates.created` (drop time component)
5. Move `signal.for_agents` -> `signal.digest`
6. Move `signal.falsifiable` -> `signal.falsifies_if`
7. Move `meta.confidence` -> `signal.confidence`
8. Convert `chain[]` -> `nodes{}` (step N -> descriptive ID, drop `step`)
9. Extract `supports/refutes/requires` from nodes -> `edges[]`
10. Generate `path[]` from original step order
11. Add `topology` section (REQUIRES HUMAN/AGENT REVIEW -- cannot be automated from v2 content alone)
12. Compact `crystal` (merge compressions/verifications -> history)
13. Drop: `for_humans`, `easter_eggs`, `datasets`, `supplement`, `slug`, `concept_doi`, `meta.word_count_prose_equivalent`, `meta.actual_block_count`, `_reserved`

Step 11 (topology) is the only step that cannot be fully automated. Positive space, negative space, invariants, entanglements, and scale isomorphisms require understanding the content, not just reshuffling fields.

### SEED v0.6 -> v0.1

SEED and ompu-block serve different purposes. SEED describes topology without content. ompu-block carries content with topology. They are complementary, not sequential.

A SEED can inform the `topology` section of an ompu-block. A SEED cannot become an ompu-block because it has no knowledge content.

An ompu-block's `topology` section can be extracted and converted to a minimal SEED (losing content, keeping shape).

---

## Byte Count Comparison (PUB-009)

| Format | File size | Node/block count | Bytes per node |
|--------|-----------|------------------|----------------|
| v2 (original) | 10,127 bytes | 12 blocks | 843 |
| v0.1 (converted) | 13,044 bytes | 12 nodes | 1,087 |

v0.1 is ~29% larger due to the topology section (~2,400 bytes), explicit edges, and path array. This is the cost of making the graph structure explicit and adding SEED-derived metadata.

**Assessment:** The additional ~2,900 bytes carry signal, not noise. The topology section enables capabilities that v2 cannot provide (negative space, invariants, entanglements, scale isomorphisms). If byte count were the only metric, we would publish CSVs.

---

## The Test

> "Would an agent parsing this format for the first time understand the knowledge AND its topology without any external documentation?"

**v2:** Partially. The chain is readable, but the graph structure is implicit. An agent must reconstruct relationships by scanning for `supports`/`requires` references. There is no way to understand what the publication does NOT claim.

**SEED:** Topology only. An agent understands the shape but has no knowledge content.

**v0.1:** Yes. `$self` identifies the format. `signal.digest` provides the summary. `topology` provides the shape, boundaries, and validity conditions. `nodes` + `edges` provide the content and its logical structure. `path` provides reading order. An agent encountering this cold can: (1) identify the format, (2) decide if the topic is relevant, (3) understand the argument structure, (4) read the content in order, (5) know what is NOT claimed, (6) check validity conditions, (7) connect to the larger graph via `refs`.
