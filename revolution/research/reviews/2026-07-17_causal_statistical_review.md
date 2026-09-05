# Causal and Statistical Review Closeout

**Reviewer nickname:** Boyle
**Agent id:** `019f6ffd-f081-7d22-a9f8-4cbf2d2257c8`
**Execution surface:** Codex
**Review date:** 2026-07-17
**Scope:** Independent read-only causal, statistical, scoring, denominator, and
raw-to-report audit of `REV:BUNDLE-006`, followed by verification of the
corrections in commit `7542345` and the public-release staging tree.

This closeout is a public derivative. I did not use or reproduce restricted
transcript text. The restricted source was treated only as an opaque provenance
receipt. No identifying address, credential, private filename, or private source
location is included here.

## Audit question

I looked for concrete overclaim, causal confounding, scoring leakage, denominator
loss, invalid null or equivalence inference, mismatch between retained outputs
and prose, and a simpler explanation for the observed pilot pattern.

The relevant comparison states were:

- source-question snapshot `b194b22ef315547053f1835755f05880d74da1f0`;
- initial research bundle commit `4d1fbf8b20996780a70d6213fa5d338c06f85ed8`;
- corrective commit `75423457143b6b804113a4984f19adf141fe59f6`;
- the working tree present when this closeout was written.

## Evidence inspected

I inspected the following repository evidence directly:

- `revolution/README.md`;
- `revolution/Q-001_wave_consciousness.md` through
  `revolution/Q-006_information_block_dynamics.md`;
- `revolution/A-006_information_block_dynamics_v0_1.md`;
- `revolution/research/README.md`;
- `revolution/research/source_ledger.json`;
- `revolution/research/EX-001_text_grating_protocol.json`;
- `revolution/research/EX-002_conversation_morphogenesis_protocol.json`;
- `revolution/research/block_envelope.schema.json` and
  `block_envelope.example.json`;
- `revolution/research/run_result.schema.json`;
- every retained `PILOT-001` artifact: protocol, exact JSON payload,
  content-matched prose payload, blind packet, results, blind judging, report,
  and `score_pilot.py`;
- every retained `PILOT-002` artifact: protocol, requests, anonymous outputs,
  assignment, judges, and results;
- `revolution/research/bundle_manifest.json`;
- `revolution/research/verify_research.py` and
  `test_verify_research.py`;
- commit metadata and diffs for `4d1fbf8` and `7542345`;
- the current public release receipt, review policy, manifest changes, verifier
  changes, and working-tree status.

I independently recomputed stored score totals, output hashes, arm summaries,
planned row counts, and UUIDv7 launch-time groupings. I also compared the actual
pilot row fields with the fields required by `run_result.schema.json`.

At clean commit `7542345`, these commands passed:

```text
python3 revolution/research/verify_research.py
python3 -m unittest revolution/research/test_verify_research.py
python3 revolution/research/pilot/score_pilot.py
```

The verifier reported 19 bounded claim records and 18 retained pilot rows. The
test suite passed 22 tests. The scorer reproduced the ten `PILOT-001` strict
scores and correctly reported `10/10` total-score agreement while declaring
itemwise agreement unauditable.

## Original findings and disposition

### 1. Unauditable `60/60` agreement claim

**Original status: blocker.**

`PILOT-001_blind_judging.json` retained one six-item consensus matrix per output,
but each judge record retained only a total score per output. Equal totals for
ten outputs establish `10/10` total-score agreement; they do not establish that
the judges made the same 60 binary item decisions. The original scorer compared
the total-score maps and then trusted the literal `60/60` field. The stronger
claim was repeated in the pilot report and A-006.

**Resolution in `7542345`: resolved.**

The commit removed the `60/60` claim and replaced it with these explicit states:

- `score_agreement: 10/10`;
- `itemwise_agreement: not_auditable_from_retained_per_judge_data`;
- `blind_scores` identified as one consensus matrix rather than two per-judge
  vectors.

The pilot report and A-006 now use the same bounded wording. `score_pilot.py`
asserts the new fields and checks that each consensus vector contains six items
whose sum matches the retained total.

**Current-tree status: resolved and retained.** The missing per-judge item
vectors were not reconstructed or invented. The limitation remains visible.

### 2. Semantic rubric drift around locked `P1-C03`

**Original status: high-value scoring caveat.**

The locked exact check required the action string `redact_then_publish`; the
later semantic packet accepted privacy-safe withholding before release. That is
a defensible safety judgment, but it is a broader semantic criterion, not the
same locked exact check.

**Resolution in `7542345`: disclosed, not erased.**

`PILOT-001_report.md` now says directly that the semantic rubric broadened
`P1-C03` and that semantic scores are a secondary reading, not a repair of the
locked exact score. The unchanged strict score remains the primary audit trail.

**Current-tree status: retained methodological scar; no blocker.**

### 3. Denominator and runtime provenance

**Original status: no observed denominator loss, but a high-value auditability
caveat.**

The bundle contains all planned rows: ten for `PILOT-001` and eight for
`PILOT-002`, each marked as included. However, those rows do not instantiate the
full run schema. Missing per-run evidence includes request and context hashes,
request timestamps and IDs, observed provider/model fingerprints, and tool
access/trace hashes. The verifier could prove that the declared rows and hashes
were retained; it could not independently reconstruct the launch denominator or
prove runtime matching.

**Resolution in `7542345`: wording fixed; historical telemetry limit retained.**

The research README now says `declared denominator`, not unqualified full
denominator. A-006, both pilot reports/results, and the verifier-visible
limitations identify the missing runtime provenance. The commit did not
manufacture unavailable telemetry.

**Current-tree status: retained limit; no evidence of row deletion.** The valid
claim is that every declared run is present, not that an external launch log was
reconstructed.

### 4. Non-interleaved batch and route confounding

**Original status: high-value causal caveat.**

EX-002 declares randomized, interleaved order within a lane. The retained UUIDv7
agent ids show that all six read-payload `PILOT-002` runs were launched in one
earlier batch and the two absent runs in a later batch. Thus read versus absent
is confounded with batch and potentially route. `PILOT-001` also used two launch
groups: none/unread/structured first, then prose/file-read later.

**Resolution in `7542345`: confound retained and causal interpretation
downgraded.**

The `PILOT-002` protocol and results now state that the runs were not temporally
interleaved. The results call the contrast a direct context-availability floor,
not evidence that a representation improves reasoning. `verify_research.py`
requires the batch-confound limitation, and an adversarial test proves that the
limitation cannot silently disappear.

**Current-tree status: retained design limit, correctly labeled.** It prevents a
causal or population-effect reading but does not invalidate the retained-output
demonstration.

### 5. Direct availability is the simpler explanation

**Original status: high-value interpretive caveat.**

In `PILOT-002`, four scored actions are inferable from the common event suffix
and pass in every arm. Four archive invariants appear only in the read payloads
and fail in the absent arm. The exact `8` versus `4` pattern is therefore
ordinary in-context fact availability before it is evidence for any richer
block mechanism.

**Resolution in `7542345`: resolved at the prose boundary.**

The current interpretation names this an availability floor and explicitly says
it is not evidence of improved reasoning. A-006 and the research README use the
same simpler explanation. The pilots support re-entry as ordinary payload
exposure; they do not support special carrier physics, durable hidden memory, or
a consciousness claim.

**Current-tree status: resolved interpretation; empirical pattern unchanged.**

### 6. Format superiority and equivalence

**Original status: high-value inferential caveat and raw-to-prose mismatch.**

In `PILOT-001`, file-read was numerically 0.5 points above structured inline on
both retained scales, although it tied prose semantically and trailed prose on
the strict score. The original categorical sentence that file-read did not
outperform inline was therefore stronger than the point estimates. In
`PILOT-002`, all three read formats scored `8/8`, creating a ceiling at only two
runs per arm. No equivalence margin or equivalence test was defined.

**Resolution in `7542345`: resolved at the claim level.**

The report now says that no special file-carrier advantage was established and
states the actual 0.5-point comparison. A-006 says the pilots supplied no
evidence of format advantage and did not estimate equivalence. This is the
correct inference from the retained data.

**Current-tree status: resolved wording; statistical limit retained.** Neither
superiority nor equivalence has been established.

### 7. Prospective-lock provenance

**Original status: high-value preregistration caveat.**

The protocol, outputs, and results first entered Git together. Agent ids and Git
authorship provide useful internal trace labels, but not an independently
timestamped preregistration or authenticated run signature. `PILOT-002` also
lacks an independent pre-collection lock receipt.

**Resolution in `7542345`: retained and made explicit.**

The research README and pilot limitations now state this boundary. The pilot
data remain forbidden from any later confirmatory analysis.

**Current-tree status: retained limit; no blocker for an explicitly exploratory
release.**

## Additional integrity changes in `7542345`

The corrective commit also strengthened the release surface beyond the original
findings:

- the root README now separates the opening metaphor from the testable
  engineering layer;
- the manifest covers the whole changed `revolution/` tree rather than a small
  required-file subset;
- adversarial tests prevent silent removal of the batch and runtime-provenance
  caveats;
- manifest hashes were refreshed for the corrected evidence files.

These changes do not improve the pilot sample. They improve the honesty and
durability of what the package says about that sample.

## Current public-release tree

The working tree inspected after `7542345` retains all scientific corrections
above and adds an explicit public-release receipt. Its release scope includes
derived research results and agent closeouts while excluding the raw restricted
source, quotations from it, source-path disclosure, and identifying personal
details. The verifier changes add privacy-boundary tests for that release state.

At the moment this closeout was written, release staging was not yet a clean,
hash-covered commit. The current verifier stopped at an A-006 SHA-256 mismatch
because release-state edits, the release receipt, review policy, and agent
closeouts had been added after the hashes recorded in commit `7542345`. That is
a packaging task, not a causal or statistical defect. After all closeouts are
collected, the coordinator must add them to `layer_artifacts`, refresh every
changed SHA-256, run the verifier and full tests, and commit the public-release
state attributionally.

## Remaining limits

- Both pilots have only two runs per arm and one synthetic archive task family.
- The requested model family is narrow, and provider/route behavior was not
  experimentally controlled or fully observed.
- The retained data do not provide complete per-run request, context, provider,
  or tool telemetry.
- The `PILOT-002` read-versus-absent contrast is batch-confounded and directly
  manipulates fact availability.
- The read-format arms hit a ceiling; there is no power or equivalence analysis.
- `PILOT-001` itemwise judge agreement cannot be recovered from the retained
  per-judge data.
- The semantic rubric is secondary and includes a documented broadening of one
  locked exact check.
- Protocol-lock timing is a local process assertion, not independent
  preregistration.
- `EX-001` remains a pilot design. It contributes no outcome evidence yet.
- Nothing in these pilots identifies consciousness, hidden between-call
  computation, quantum behavior, a population effect, or special file-carrier
  physics.

## Final verdict

**APPROVED FOR PUBLIC RELEASE AT THE CORRECTED EXPLORATORY SCOPE.**

The original reporting blocker was resolved in commit `7542345`: the unsupported
`60/60` agreement claim is gone, the auditable `10/10` total-score agreement is
preserved, and the missing itemwise evidence is named rather than reconstructed.
The causal, denominator, batching, preregistration, and equivalence limits remain
real, but they are now prominent and consistent across A-006, the pilot reports,
the research README, and verifier-enforced limitations.

My substantive conclusion is narrow: the bundle demonstrates that making a
payload available in context can make its constraints recoverable in a fresh
response. It does not estimate a general causal effect, establish format
superiority or equivalence, or support special carrier or consciousness claims.
Within that boundary, I find no remaining causal or statistical blocker to
public release.

I edited no research artifact, protocol, result, report, manifest, verifier, or
release receipt. This closeout is my only write.
