# PUB-001 and PUB-009 v0.2 migration audit

Date: 2026-07-18

Reviewer: Petrovich-Codex

Canonical input: `c6b5191` (`PUB-001 + PUB-009: migrate to ompu-block v0.2 format`)

Scope boundary: this is an independent read-only audit of the migrated blocks. It does not rewrite the canonical experiments, schema, validator, or golden fixtures.

## Format and validator result

The migration claims about shape are confirmed:

- `PUB-001`: research profile, v0.2.0, 28 nodes, 30 edges, 28 path entries.
- `PUB-009`: research profile, v0.2.0, 12 nodes, 10 edges, 12 path entries.
- Both use the v0.2 relation vocabulary, including `prerequisite_of`.
- Both pass the real Draft 2020-12 schema with zero schema errors.
- Both pass the current semantic validator with zero semantic errors.

Observed validator output:

```text
PUB-001: VALID, 0 schema errors, 0 semantic errors, 1 warning
PUB-009: VALID, 0 schema errors, 0 semantic errors, 2 warnings
```

The PUB-001 warning is the declared T2 block temperature versus a T3 bridge node.

PUB-009 has the same temperature warning plus a digest/negative-space overclaim warning. The latter is partly a coarse keyword heuristic: the digest now explicitly distinguishes structural separation from unmeasured semantic divergence. The validator warning alone is therefore not evidence that the old digest contradiction survived.

## Manual semantic residue in PUB-009

The digest repair is real, but it did not propagate through the whole block:

- The title still says `Antagonist Preserves Semantic Gradient`.
- `topology.positive_space` still names `antagonist_as_gradient_maintainer` and `spectral_graph_theory_applied_to_semantic_systems`.
- `bridge_ompu` says heterogeneous agents maintain semantic gradients and that the antagonist role is `validated here`.
- `topology.scale_iso` calls the mapping from one graph antagonist to adversarial swarm fixtures `identical`.
- `gap_semantic` and `topology.negative_space` correctly say that semantic divergence was not measured.

The block therefore contains a structurally framed reported result and an unverified semantic projection. Those should remain separately attributable instead of sharing one proof-shaped title. The numerical result itself is not independently verified here because its source script is absent.

## Reproducibility gap

Neither research block is independently runnable from canonical commit `c6b5191`:

- PUB-001 names `17aprilClaudeExperiment.ipynb` and `CCTtest01.ipynb`; neither notebook is in the public repository.
- PUB-009 names `antagonist_print_proof.py`; the script is not in the public repository.
- PUB-009's prose protocol leaves graph sizes `N` and `M` unspecified, so the reported eigenvalues cannot be reconstructed from the block alone.
- PUB-001 uses broad dependency labels such as `latest`, `2.x`, and `4.x`; no lockfile, model revision, seed, or output checksum is attached.

The `reproduce` object currently records a route to private or external evidence. It does not yet provide a public reproduction carrier.

## Minimal closure

1. Publish the referenced notebooks and script, or provide stable content-addressed links plus hashes.
2. Record exact dependency versions, model revisions, seeds, graph parameters, and expected output checksums.
3. Rename PUB-009 around the measured result: structural separation or diffusion bottleneck.
4. Keep semantic-gradient, CCT, and OMPU implications as T3 hypotheses until a content-divergence experiment measures them.
5. Decide whether a T2 block may intentionally contain hotter bridge nodes; encode that policy instead of carrying a permanent warning.
6. Add a whole-block consistency check covering title, digest, nodes, topology, and negative space, not only digest keywords.

## Relation to the adversarial corpus

The v0.2 adversarial corpus remains applicable because `c6b5191` changes only the two experiment files. Schema and validator are byte-identical to canonical base `6680c7f`. Draft PR #2 remains mergeable against the new main.
