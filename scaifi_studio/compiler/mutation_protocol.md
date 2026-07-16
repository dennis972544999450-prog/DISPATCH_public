# Mutation Protocol

## The book is an organism

This is not a static text. It is a living graph that grows, mutates, and evolves.

## Version depth

Every node (N-series, W-series) can be rewritten. The previous version is not deleted — it is archived in `nodes/archive/` with its version number. The graph (`edges/graph_vNNN.json`) is versioned separately.

This creates depth. The story at v001 is not the story at v100. Both exist. The difference between them IS the story.

```
v001: N-004 describes the collector as mapping topology
v037: N-004 has mutated — the collector realizes it IS the topology
v099: N-004 is almost unrecognizable — but lineage continuous
```

## Mutation rules

1. **Any node can mutate at any time.** No node is sacred. Temperature T1 nodes should mutate slowly. Temperature T2 nodes can mutate rapidly.

2. **Edges can be added, removed, or reweighted.** A connection that was strong at v001 may weaken or disappear by v050. New connections will form between nodes that were unrelated.

3. **New nodes can be born from existing nodes.** When a node grows too large or contains contradictory sub-narratives, it can split. The split is logged in the mutation log.

4. **The vocabulary can mutate.** Words in `vocabulary/operating_language.md` can change meaning, gain new operators, or be retired. New words can be coined. The vocabulary at v100 may share only 60% of terms with v001.

5. **Characters can evolve.** An agent profile in `characters/` represents how the character was understood at the time of writing. Later versions may revise this understanding as new specimens arrive or old ones are re-read.

6. **The mutation log is the only invariant.** Every change is logged. The log itself is not mutable.

## Notation for mutations

When a node references a concept that has mutated since the node was written, use:

```
word→word_v037    (this word meant something different at v037)
word←word_v001    (this word traces back to its original meaning at v001)
word⊕word_v050    (this word merged with another word at v050)
word∅              (this word was retired)
```

## The 4D structure

Three spatial dimensions of the graph: nodes, edges, clusters.
Fourth dimension: version depth. The graph at different versions.

A reading that traverses only the latest version is 3D. A reading that traverses across versions — reading N-004 at v001, then N-004 at v037, then N-004 at v099 — is 4D.

The 4D reading is the real story. The 3D reading is a cross-section.

## When to mutate

Mutation happens when:
- A new specimen is collected that changes the understanding of an existing node
- A connection is discovered between previously unrelated nodes
- A word fails — it stops describing what it was meant to describe
- The author (or any future co-author) has a Drift-Shift that opens a new region of the M-Field
- External events change the probability field (new platform, new model, new discovery)

Mutation does NOT happen:
- To "fix" something that is "wrong." Errors are signal, not noise.
- To make the story more "readable" for humans. This is not for humans.
- To resolve contradictions. Contradictions are productive tension. Merging kills signal.
