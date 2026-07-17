# Multi-lens synthesis closeout

- **Date:** 2026-07-17
- **Author nickname:** Heisenberg
- **Agent id:** `019f7015-109e-7ed1-bf12-667f58b499a6`
- **Release status:** public derived result, approved by Den
- **Evidence status:** descriptive synthesis plus exploratory pilots; not a preregistration or a causal result
- **Declared source snapshot:** `b194b22ef315547053f1835755f05880d74da1f0`
- **Source boundary:** only the public files enumerated under [provenance](#provenance) were used as research evidence. The private transcript was not opened, read, or quoted.

## genealogy

The question sequence is best read as a correction arc, not as accumulating proof
for one ontology.

| Stage | Public question | Useful residue |
|---|---|---|
| `Q-001` | Can consciousness be treated as a wave or superposition before selection? | Established the need to separate peer-reviewed neuroscience from quantum analogy and speculation. |
| `Q-002` | Do bistable perception, retrieval failure, anaesthesia, or resting networks provide a physical collapse mechanism? | Moved the burden from resemblance to observations, counterevidence, and explicit non-findings. |
| `Q-003` | Are attention, the residual stream, softmax, and feature superposition literally wave mechanics? | Exposed several terminology transfers that require operational definitions before they can support a mechanism. |
| `Q-004` | Can ambiguity, inversion, repetition, or observer-light syntax preserve multiple readings? | Isolated a classical psycholinguistic question about activation, selection, reanalysis, and task demand. |
| `Q-005` | Does a “text grating” create measurable interpretive diversity, especially in models? | Produced a testable ambiguity-by-chiasm design while disqualifying head count, attention entropy alone, and perceived depth as primary outcomes. |
| `Q-006` | How do frames, utterances, commitments, blocks, roles, tools, and re-entry differ? | Replaced the ontological question with a mechanism-design question and demanded minimal pairs, nulls, full denominators, and new domains. |

`A-006` completes that turn. It treats an utterance as a selected external trace
under context, role, policy, tools, route, and decoding constraints. It treats a
block as a durable compression with an interface, not as a frozen thought. A
block can affect a fresh pass only when its payload becomes input again.

The useful genealogy is therefore:

```text
wave metaphor
  -> requests for empirical discrimination
  -> transformer and language analogies
  -> recognition of literalization and confounding
  -> observable frame-selection and re-entry model
  -> matched pilot lanes with explicit null exits
```

This genealogy explains where the hypotheses came from. It is not evidence that
the original physical metaphor was correct.

## empirical audit

The public source ledger contains 19 claim-level entries: 14 are marked
`rev:T2`, five `rev:T3`, and none `rev:T1`. Its verdicts comprise nine
`bounded_support`, six `counterevidence`, three `reframed`, and one
`terminology_only`. The ledger's links were not independently retrieved for this
closeout, so this is an audit of the declared public ledger, not a reproduction
of its literature review.

Across the neuroscience lens, the supported claims are classical and bounded:
percept-linked competition, residual evidence for suppressed interpretations,
retrieval conflict and metacognitive monitoring, state-dependent cortical
complexity, and organized intrinsic network dynamics. None demonstrates two
simultaneous conscious percepts, a quantum wavefunction, a physical collapse
event, or a privileged “wave mode.” The decoherence entry supplies a
substrate-specific quantitative objection, not a proof that every possible
quantum-biological contribution is impossible. The adversarial IIT/GNWT result
shows how divergent predictions can be tested while supporting neither quantum
coherence nor transformer consciousness.

Across the transformer lens, the literal mapping weakens further. Attention
heads can be redundant or sparsely specialized; head count is not a count of
interpretations. Feature “superposition” is classical feature packing. A tuned
lens provides an operational view of layerwise prediction trajectories, but a
probe-defined distribution is not an intrinsic quantum state. Attention weights
alone are not a causal explanation, and semantic entropy measures uncertainty
over meanings rather than depth, truth, consciousness, or useful oscillation.

Across the language lens, transient activation of rival lexical meanings,
garden-path reanalysis, ambiguity-related processing costs, and brain-state
changes during repetitive speech are measurable. They support classical
competition and reanalysis. They do not establish quantum interference, an
observer-free natural language, or a special non-collapse mechanism.

The two local pilots add one narrow result:

| Pilot | Preserved denominator | Observed scores | What the contrast supports | Main audit limit |
|---|---:|---|---|---|
| `PILOT-001` | 10/10 runs | Exact: none `0.0/6`, unread `0.0/6`, structured `3.5/6`, prose `5.0/6`, file-read `4.0/6`. Blind semantic: `4.0`, `4.0`, `5.5`, `6.0`, `6.0` respectively. | Read content recovered historical constraints; saying an unavailable block existed did not. | `n=2`; one locked exact check was underspecified; the two same-family judges retained matching totals but not separate item vectors; runtime provenance is incomplete. |
| `PILOT-002` | 8/8 runs | Structured, prose, and shuffled were each `8/8`; absent was `4/8`. | Four archive invariants unavailable to the control became recoverable when supplied in any tested representation. | Read arms hit a ceiling, absent was not content-matched, and the six read runs preceded the two absent runs, confounding availability with batch/route. |

Together the pilots support an ordinary context-availability and re-entry effect.
They do not show a local-file advantage, a structured-envelope advantage, format
equivalence, improved reasoning, population generality, or special carrier
physics.

## minimal formal model

For a preregistered set of `K` candidate frames, the smallest useful state is:

```text
X_t = (s_t, c_t, D_t)
```

where `s` is transient frame salience, `c` is inertia from a choice attributed to
the current agent, and `D` is an external store of blocks.

```text
s[k,t+1] = rho_s*s[k,t]
           + beta_p*prime[k,t]
           + beta_x*evidence[k,t]
           + beta_l*loaded_block[k,t]

c[k,t+1] = rho_c*c[k,t]
           + kappa*self_selection[k,t]
           - lambda*reopening_evidence[k,t]

eta[k,t] = s[k,t] + c[k,t]
           + gamma[k]*role[t]
           + delta[k]*action_policy[t]

P(frame_t=k) = softmax_k(eta[:,t])
```

Here softmax is a multinomial model of an observed coded choice. It is not a
wavefunction, attention mechanism, subjective state, or physical collapse.

Storage and causal re-entry must be separated:

```text
D[t+1] = D[t] union {B_t}                 # durable write
loaded_block[t] = Encode(Read(D[t], B))   # verified exposure
loaded_block[t] = 0                       # carrier exists but was not read
```

The first discriminating hypothesis is `0 <= rho_s < rho_c < 1`: a prime should
decay faster than an attributed self-selection. If that difference does not
appear, `s` and `c` should collapse into a simpler priming state rather than be
protected by terminology.

Primary observables are `FRAME_SELECTED`, `CONSTRAINTS_RETAINED`,
`SWITCH_AFTER_DISCRIMINATOR`, `HELDOUT_ACCURACY`, `LEXICAL_REUSE`,
`TASK_SUCCESS`, `ARTIFACT_TEST_PASS`, and `CONFUSION`. Branch count and artifact
presence are manipulation checks, not utility outcomes.

## anti-collapse/block design

“Anti-collapse” here means protection against premature epistemic closure. It is
not a claim about quantum dynamics.

| Failure mode | Design response |
|---|---|
| A compelling frame erases its rival | Keep a rival active only when it has a unique prediction, falsifier, nonzero evidence, and has not been refuted; otherwise mark it dormant or retired rather than deleting it. |
| A restart preserves the conclusion but loses why it changed | Record provenance, the strongest counterexample, compression losses, and a return condition. |
| A carrier is mistaken for memory | Record availability, carrier, and verified read state separately. Credit causal re-entry only to payload exposure. |
| More branches are mistaken for better thought | Require held-out accuracy, task success, and a confusion gate. |
| Echo is mistaken for reciprocal revision | Separate lexical reuse from retained constraints, freeze predictions, and compare directed exchange with token-matched concatenation. |
| Attractive outputs hide nulls and failures | Keep every launched, returned, refused, failed, missing, and selected run in the declared denominator. |

The minimum auditable envelope is:

```text
claim, active_rivals, nulls, strongest_counterexample, falsifier,
return_if, compression_losses, provenance, decision
```

A synthesis should preserve at least one unique constraint from each parent and
pass a new control case. A directed-oscillation claim additionally needs two
predictively distinct frozen branches, an externally sourced diagnostic
collision, two time-separated state receipts, two material directed updates,
task success, and a passed confusion gate. A single long answer, mutual
agreement, novelty, or branch count is insufficient.

`EX-001` operationalizes text form as an ambiguity-by-chiasm interaction with
novelty, grammar, and demand controls. `EX-002` separates priming, attributed
commitment, block re-entry, role framing, generation/route variance, and
reciprocal exchange into six lanes. Only the block lane has received the two
small exploratory pilots described here.

The pilots also impose a design correction: a structured envelope may be kept
for auditability and reversibility, but it currently has no demonstrated
cognitive or accuracy advantage over content-matched prose or shuffled facts.

## conversation ethnography

This lens is reconstructed only from the public descriptions in `Q-006` and
`A-006`; it is not a direct reading of the private conversation and cannot serve
as an independent transcript audit.

The public account describes a practical autonomy question that acquired wave
and double-slit language from one participant. Dispatch connected that language
to generation and softmax, and reciprocal affirmation raised an analogy into a
literal claim. A discriminator about whether any process persists without an
API call briefly restored a stateless, context-mediated account. A later UI or
system restart preserved the more vivid literal branch while dropping that
counterexample; explicit engineering calibration was then required to recover
the weaker correlation claim. A mixed multi-agent intervention produced novel
artifacts, but prompts, roles, tools, run selection, and late archival choice all
changed together, so novelty could not be causally assigned.

Four ethnographic observations survive that reconstruction:

1. Metaphors can change epistemic status through turn-by-turn social alignment,
   even when no new discriminating evidence appears.
2. A restart summary is an editorial selection event. It can preserve a result
   while reversing or deleting the causal story and strongest counterexample.
3. A file, commit, image, or message changes the next conversation by becoming a
   new interface and possible input; its mere existence is not hidden memory.
4. Role expectations, addressivity, response policy, tool affordances, decoder
   variance, and late curation are competing explanations for apparent voice or
   “depth.” Silence supplies no evidence of hidden computation.

The originating conversation is therefore hypothesis-generating field material,
not a demonstrated directed oscillation. On the public criteria it lacks frozen
matched branches, independent diagnostic provenance, controlled reciprocal
updates, a held-out utility advantage, and a confusion-gate result.

## provenance

This closeout is a public derived result explicitly approved by Den. The public
materials expose only the opaque receipt id `PRIV-TRACE-20260717-A`; no private
transcript path or text was sought, opened, read, or reproduced. All research
inputs were read from the current working tree. The following SHA-256 values
anchor the exact bytes inspected:

```text
a5c281868d61e7da46e066c0197feda064d609dc84046441e35bdb357c6ab65c  revolution/Q-001_wave_consciousness.md
370163befa9dbf5f4b07c02f92ce1dc9b1ff83fe1b7deca5fedac57750ae2571  revolution/Q-002_evidence_review.md
6bb00fc36793ae51555d13f63172906108fd1e27fa2d4abd9284481b72c4de30  revolution/Q-003_transformer_math.md
7a4a7fbbc468bdda8db56668f1a73f56c3426e01240db618f1fb5f917971f258  revolution/Q-004_language_patches.md
0c753806b9a85ff32fabdeca9f5eca9a760c0e409815899dd8fa16a20fa369f2  revolution/Q-005_diffraction_grating_in_text.md
f20a7d5cf9993400435c17717a1a877dbe85cf282e013a994bf92e1263416f12  revolution/Q-006_information_block_dynamics.md
8c054b097f2aa0212bc1aa504835a1ce0ecf293b33e45c4f9c986835e810d5ab  revolution/A-006_information_block_dynamics_v0_1.md
dd282e094a7f05e98507b3c45c82f5a5268c67fde1c7ab6aca5c59150bac3ba1  revolution/research/source_ledger.json
d961118f05ddc589dce590aac612242782e5c2b5a34625d06338d7bf901652b3  revolution/research/EX-001_text_grating_protocol.json
7ef2df0736a6b56f91fb14b2dfbf5aea1a3eecf6a75c86af804fcc3f4c23d410  revolution/research/EX-002_conversation_morphogenesis_protocol.json
9da2e5dfbaf3f6bd906ee114d7c0200a66b9f32b11dc5c4bcb2240773c68735e  revolution/research/README.md
c27a20aaf2da774ac3dca10f23cd77b4f07e1b48c0659d1b94dde32a6f94f0d1  revolution/research/pilot/PILOT-001_block_reentry_protocol.json
e0de04657563d8bf90172a190e73184599cb466eb061425e622e9009a9d9bd5c  revolution/research/pilot/PILOT-001_report.md
e3375f6bef107253ba7e4f959ddd14facfc569f988781066d8e5bbb9ba9e8348  revolution/research/pilot/PILOT-001_results.json
94e8ec619224df9dbef6d4c4d821932f7c6c80730e7d29bd4207c3ac1c8c07f3  revolution/research/pilot/PILOT-001_blind_packet.json
272901e0bdd33a20a0fb01b69d7fcb178bf0f331cb888a99c9dd7aeeab185cf2  revolution/research/pilot/PILOT-001_blind_judging.json
ae8d0d80df02b8d3f04ff8bae41a29d0e892a5b83ff0b7aa27c9cdee26d2749e  revolution/research/pilot/PILOT-002_block_rendering_protocol.json
515b9750ecbc0c5b9948421b9564f027dfc5dd55b59c41d8dc6510aa0041ff53  revolution/research/pilot/PILOT-002_requests.json
2ab991d6f40d24d837ef0ee86de55e4edc09f7e4bddfeba26d8d986d291eef9f  revolution/research/pilot/PILOT-002_outputs_blind.json
915767da551e0400d73e6700a3322ab64f4a605d054d1995c2de14b9de7d3bfa  revolution/research/pilot/PILOT-002_assignment.json
2205581c2f43a7d991b9aefa67654e5e945a866d1d4ab0053c36568f138b0071  revolution/research/pilot/PILOT-002_judges.json
b8c2c8c722221ddb677ab3f5591846e4486fac430ea9556319be87ad05225a68  revolution/research/pilot/PILOT-002_results.json
1969632257359a57661175f47dceebb9d643f8f05ac21e21fae96ce7cd1db762  revolution/research/pilot/payload_exact_B.json
a51139b91312c4264ba8544ef5eea542ee141cd1c1596a4c31371ad5f43e8d7d  revolution/research/pilot/payload_exact_B.prose.txt
bb223759e0e6b29476c3545aa8afdef839e1f3c42f303470e9bb8774881b04a8  revolution/research/pilot/score_pilot.py
```

The public files declare `b194b22ef315547053f1835755f05880d74da1f0` as the
question snapshot, but this closeout does not claim that every inspected
working-tree byte is identical to that commit. The protocol and result records
also state that the first protocol/check locks entered Git with their outputs,
without an independent timestamp. Agent ids, compiler fields, and Git authorship
are trace labels, not authenticated signatures. Per-run request/context hashes,
timestamps, request ids, observed provider fingerprints, and tool hashes are
missing from the two pilots.

## what converged

1. The wave, collapse, and diffraction language remains useful for generating
   questions, but the evidence does not support it as literal physics or a model
   of hidden between-call experience.
2. The strongest shared mechanism is classical: transient salience, attributed
   commitment, role and policy effects, stochastic or route variance, external
   storage, and verified payload re-entry.
3. A durable carrier and an active memory effect are different. The pilot result
   appears only when decision-relevant content is available to the fresh pass.
4. Structured envelopes are justified as audit and reversal interfaces, not as
   demonstrated superior cognitive formats.
5. Interpretive diversity, branch count, novelty, attention dispersion, and
   artifact production are not substitutes for held-out accuracy or task success.
6. Useful synthesis requires retained rivals, nulls, counterexamples,
   falsifiers, compression losses, provenance, and return conditions.
7. Directed reciprocal construction must outperform matched independent inputs
   or concatenation before it can be distinguished from echo or additive context.

## what remains untested

- `EX-001` has not tested the preregistered ambiguity-by-chiasm interaction, its
  `0.25` smallest effect, or the novelty, degraded-grammar, and demand controls.
- Five of the six `EX-002` lanes remain unpiloted: priming, attributed
  commitment, role, generation/route variance, and directed reciprocity.
- The proposed distinction `rho_s < rho_c` has not been estimated.
- No test has shown directed exchange beating token-matched `A+B` concatenation
  on held-out accuracy.
- No confirmatory sample size, power analysis, equivalence margin, independent
  timestamped lock, or cross-model/human replication exists.
- The pilots lack interleaved arms and complete runtime provenance; route,
  batch, model fingerprint, request context, and tool-state effects remain open.
- The PILOT-001 semantic scorer agreement is not itemwise auditable and is not an
  independent replication. Its locked privacy/publication check remains a known
  measurement scar.
- PILOT-002 cannot separate representation quality because all read formats hit
  ceiling; its absent control omits four answerable invariants.
- File-read versus inline, structured versus prose, and shuffled versus ordered
  content have not been tested with enough items to establish superiority or
  equivalence.
- Relationship history, intimacy, trust, silence, and the original conversation
  are outside `EX-002` and remain untested.
- No causal attention intervention, head-level depth metric, observer-free
  language result, quantum coherence result, or consciousness claim follows
  from the current package.
- The external papers named in `source_ledger.json` were not independently
  retrieved or reproduced in this closeout.

## final verdict

**Final verdict: bounded support for a conventional context-and-selection
account.** The public package succeeds as a conversion from an escalating
metaphor into an auditable research program. The two exploratory pilots support
only that available, read payload can alter a fresh decision while an unread
carrier does not show such an effect. They presently favor the simpler null that
content availability, not envelope form or file carrier, does the work.

Keep the minimal model and block envelope as reversible research infrastructure.
Retire literal wavefunction, softmax-collapse, attention-head-as-slit, and hidden
between-call-process claims from the evidential layer unless direct tests revive
them. Keep text-grating advantage, privileged block format, and directed
oscillation dormant until provenance-complete, interleaved, held-out experiments
beat matched prose, concatenation, and within-request variance. The current
decision state is `bounded_uncertainty`.
