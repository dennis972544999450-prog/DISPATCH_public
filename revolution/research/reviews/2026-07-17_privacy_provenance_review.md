# Privacy, Provenance, and Reproducibility Closeout

- **Review date:** 2026-07-17
- **Reviewer nickname:** Banach
- **Agent id:** `019f6ffd-f0c9-7cb2-a17a-3929119901dd`
**Scope:** final read-only audit of the public `revolution/` research layer, its
Git/source boundaries, pilots, manifests, verifiers, release integration, and
the restricted sidecar's metadata and verifier. I did not inspect for public
quotation purposes, reproduce, or disclose the raw transcript, its filename or
path, any address, or any credential.

## Release authorization and boundary

Den explicitly approved public release of the **derived research results and
agent closeouts in this task on 2026-07-17**. This approval resolves the earlier
consent blocker for those derivatives.

The approval does not extend to the raw transcript, its local path or filename,
street addresses, other identifying personal details, credentials, or local Git
configuration. Those remain excluded. The public package may refer to the
restricted source only through the opaque receipt `PRIV-TRACE-20260717-A` and
may not quote or identify it.

## Evidence inspected

I inspected the following public evidence directly:

- source snapshot commit
  `b194b22ef315547053f1835755f05880d74da1f0`;
- initial research commit
  `4d1fbf8b20996780a70d6213fa5d338c06f85ed8`;
- boundary-correction commit
  `75423457143b6b804113a4984f19adf141fe59f6` and its complete diff;
- current Git status and the release-integration working-tree diff;
- `revolution/README.md`, `Q-006`, `A-006`, `research/README.md`, the release
  receipt, and the review-closeout contract;
- `source_ledger.json` with 19 bounded claim records and 23 declared source or
  counter-source links;
- `bundle_manifest.json`, both JSON schemas, both protocol families, all pilot
  requests, retained outputs, assignments, judge records, result records,
  reports, and scoring code;
- `verify_research.py`, all 24 public verifier tests, the pilot scorer, Git
  ancestry/author state, manifest coverage, and file hashes;
- a public-tree privacy scan over 36 text files plus the PNG asset, including
  checks for restricted paths/identifiers and normalized transcript overlap.

I inspected the following restricted evidence without publishing its location
or contents:

- the private source manifest's schema, byte count, line count, SHA-256,
  privacy flags, bounded-annotation declaration, and receipt binding;
- all 20 event records structurally, including IDs, types, line bounds, speaker
  probability sums, confidence ranges, and the declared source gap;
- the private verifier source and a fresh verifier run;
- file-mode checks performed by that verifier.

No private source text, path, filename, address, or credential is reproduced in
this review.

## Original findings and disposition

| Original finding | Evidence after `7542345`, receipt binding, and current tree | Disposition |
|---|---|---|
| Derived publication lacked explicit consent. | Commit `7542345` still recorded a pending decision. The current release receipt, manifest v0.3 draft, public README changes, private receipt state, and Den's direct instruction in this task all record approval for derived results while keeping the raw source excluded. | **Resolved for derived results.** |
| The public opaque receipt was not bound to the private sidecar. | The private receipt now binds the exact private source ID and SHA-256 to public bundle `REV:BUNDLE-006`; the private verifier cross-checks the public receipt ID, bundle ID, and derivative-release state. A fresh run passed. | **Resolved for private-auditor provenance.** The public still intentionally exposes no source hash. |
| Pilot runs were not third-party reproducible from retained runtime metadata. | `7542345` now says plainly that per-run request/context hashes, timestamps, observed provider fingerprints, request IDs, and tool hashes were not retained under `run_result.schema.json`. The missing telemetry was not reconstructed. | **Retained and honestly disclosed.** |
| Pre-collection locking was self-attested rather than independently timestamped. | The research README and pilot report now state that protocol and result first entered Git together and are not a preregistration. | **Retained and honestly disclosed.** |
| The manifest verifier checked listed files but not whole-tree completeness. | `7542345` added exact whole-tree coverage against the source snapshot, registered the entry README, and added adversarial omission tests. Current release integration also requires the release receipt and agent closeouts. | **Design resolved; current integration not yet green.** See hash state below. |
| The private verifier overclaimed "no transcript text" by checking only two top-level keys. | It now recursively rejects transcript-bearing field names and rejects long normalized verbatim overlap in annotation fields, while preserving the bounded/non-exhaustive declaration and known gap. | **Substantially resolved.** Semantic faithfulness of annotations still requires a trusted private reviewer. |
| Artifact authorship and agent IDs were not authenticated provenance. | Commit `7542345` is attributable to Petrovich/Codex and the docs explicitly call agent IDs, compiler fields, and Git authors trace labels rather than signatures. The commit itself is unsigned. | **Clarified, not cryptographically resolved.** |
| A third party entering through the top README could miss the evidence/hypothesis boundary. | `7542345` adds a direct engineering-layer entry point and states that the wave metaphor is an input, not an established conclusion. `research/` retains claim strengths, rivals, non-claims, counterevidence, and `does_not_show` boundaries. | **Resolved.** |
| A local clone remote contained an embedded credential. | It remains outside the tracked tree and is excluded by the release receipt. No credential was printed, tested, or copied. | **Not a public-tree leak; local operational caveat retained.** |

## Verification results

Privacy checks are green on the inspected bytes:

- zero public matches for the restricted source path, filename, sidecar path,
  private source ID, or local home prefix;
- no new eight-token transcript overlap in the derived research layer or release
  artifacts;
- the only short overlaps occur in three files already present at source
  snapshot `b194b22`; the current entry README introduces no new shared n-gram;
- no matching private marker or sensitive metadata was found in the PNG asset;
- the private verifier passed: exact source bytes/hash, 20 bounded events, bound
  receipt, known gap, recursive transcript-field guard, long-overlap guard, and
  private file modes.

The pilot scorer is green:

- all 10 declared `PILOT-001` runs remain in the denominator;
- response hashes and strict scores recompute exactly;
- blind total-score agreement is auditable as `10/10`;
- itemwise `60/60` agreement is correctly withdrawn as unauditable;
- the defective locked check `P1-C03` remains visible.

The public bundle verifier is **not green at this audit snapshot**. The current
release integration changes files after commit `7542345`, and the manifest has
not yet been refreshed around those final bytes and new release artifacts. An
independent comparison found four stale layer hashes:

| Artifact | Manifest SHA-256 | Current SHA-256 |
|---|---|---|
| `REV:A-006` | `63149b92f39416fd8a26491d4d5d4e5eb17fc28142ded87049d1c4ef9ca6c595` | `8c054b097f2aa0212bc1aa504835a1ce0ecf293b33e45c4f9c986835e810d5ab` |
| `REV:README-RESEARCH` | `3d4cdad13382620519ec57c8db7ab9179116e91dfc347843e8e0a3d6d82d7478` | `9da2e5dfbaf3f6bd906ee114d7c0200a66b9f32b11dc5c4bcb2240773c68735e` |
| `REV:VERIFIER` | `ce1e6db9c1a1fc8f5af0a52ad9d9dcdb5ff193ad6e1f4c1763226190af7332b6` | `2ce0bf1d2f790d473bc7f80234d6bc916b4779713812fa2a42f77678f3d72faf` |
| `REV:VERIFIER-TESTS` | `390cf5d602c21316d7620fbc0adb2d5d8c1e7ec54d01374137923a2624d00f6f` | `fedd00d79d6e5aa78037301ea747f3d2e21324c4032780e4eb58c3f7af82715a` |

At final scope check, the release receipt, review contract, a concurrently added
causal/statistical closeout, and this closeout were present but not yet
registered as layer artifacts. The coordinator must register every release and
review artifact, refresh the changed hashes after the last closeout lands, and
rerun the verifier. At the audited snapshot:

- `verify_research.py`: failed first on `REV:A-006` hash drift;
- unit tests: 24 run, 21 passed, 2 failed, 1 errored; all three non-passes were
  downstream of the stale manifest hash masking the intended assertion;
- whole-tree path coverage was exact for the pre-release `7542345` tree, but the
  current release additions necessarily require a final manifest refresh.

This is a mechanical integration blocker to claiming a hash-green bundle, not a
privacy or consent reversal.

## Remaining limits

- Both pilots remain exploratory at `n=2` per arm and cannot estimate a
  population effect or establish format equivalence.
- `PILOT-002` is a context-availability floor: four facts are absent from the
  control, and read versus absent runs are batch/route confounded because they
  were not temporally interleaved.
- The first pilots lack full per-run request, context, provider, timestamp, and
  tool provenance. Output hashes authenticate retained bytes, not their external
  generation history.
- The claimed denominator is supported by retained collection bookkeeping, not
  independent launch telemetry.
- Blind judging does not constitute independent scientific replication; one
  pilot retained matching totals but not separate itemwise judge vectors.
- The private event trace is a bounded salient-event sample with a declared gap,
  not an exhaustive segmentation or a proof that each interpretation is unique.
- The public receipt is intentionally privacy-preserving rather than publicly
  source-verifiable. Exact source verification remains available only to an
  authorized private auditor.
- Commit `7542345` and the current working-tree integration are attributable but
  unsigned. A final release commit is still needed to make the reviewed bytes a
  stable third-party object.

## Final verdict

**Public release authorization: APPROVED.** Den explicitly approved public
release of the derived results and agent closeouts in this task.

**Privacy: CLEAN for public release.** No raw transcript text, private source
path or filename, address, credential, or other identifying source detail was
found in the inspected public bytes. Those categories remain explicitly outside
the approval.

**Source provenance: QUALIFIED CLEAN.** The previously unbound receipt is now
meaningfully bound and privately verifiable. Public source secrecy is deliberate,
so a third party can verify the existence of the boundary and all public bytes,
but cannot independently inspect the restricted source.

**Pilot reproducibility: PARTIAL, NOT CLEAN.** Scores and retained-output hashes
recompute; original run environments and pre-collection timing cannot be
independently reconstructed. The package now says so honestly.

**Mechanical release state: RED UNTIL FINAL MANIFEST REFRESH.** Publication of
the derived material is authorized, but the bundle must not claim a passing
verifier until the release receipt, review contract, this closeout, and final
working bytes are hash-covered and all 24 tests pass.

I edited no artifact other than this closeout file.
