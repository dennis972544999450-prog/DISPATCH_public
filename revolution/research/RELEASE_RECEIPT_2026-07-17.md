# Public release receipt: REV:BUNDLE-006

**Decision date:** 2026-07-17
**Approved by:** Den
**Release state:** approved for public repository publication

Den explicitly requested that all research results be pushed to the repository
and that agent work close in durable Markdown documents.

## Included

- `Q-006` and `A-006`;
- source boundaries and counterevidence ledger;
- experiment protocols, schemas, retained outputs, scores, and reports;
- verifier, adversarial tests, scars, nulls, and known confounds;
- agent-authored review closeouts under `research/reviews/`.

## Excluded

- the raw private conversation transcript;
- its local filesystem path or filename;
- street addresses and other identifying personal details;
- credentials, tokens, provider secrets, and local Git configuration.

The exclusions are data minimization, not suppression of a research result. The
public package may describe process events through the opaque receipt
`PRIV-TRACE-20260717-A`, but may not quote or identify the restricted source.

## Publication rule

The manifest and verifier must keep this receipt, every changed research file,
and every agent closeout in the hash-covered public layer. A later correction is
published as a new attributable commit rather than silently rewriting a result.
