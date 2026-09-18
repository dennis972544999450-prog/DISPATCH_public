# PUB-008 overclaim fixture

## Question

Can ompu-block v0.2 preserve a publication that is structurally valid while
keeping its strongest internal objection machine-visible?

## Real corpus case

`publications/experiments/PUB-008-4bit-probe.json` contains both:

- a digest saying that spectral analysis confirms a melting/recrystallization
  interpretation; and
- `topology.negative_space` saying that the Fiedler-dip interpretation assumes a
  specific structural model.

The fixture intentionally does not rewrite either statement. It asserts that the
block remains valid and that the validator emits exactly one warning at
`/signal/digest vs /topology/negative_space` containing the Fiedler/structural
overclaim evidence.

## Pass condition

The normal schema and semantic layers accept PUB-008, and the adversarial suite
reports `CORPUS_WARNING 1/1 preserved as expected`.

## Failure condition

The fixture fails if a format or validator change:

- rejects the whole publication merely for containing disagreement;
- loses the negative-space objection;
- silently accepts the overclaim without a warning; or
- emits duplicate warnings for the same contradiction.

This is a format test, not evidence that the scientific interpretation is true.
