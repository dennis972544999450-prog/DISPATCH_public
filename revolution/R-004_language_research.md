# R-004: Language Patches — Existing Research

Research response to Q-004. Mode: FIND existing work, not theorize.
Temperature scale: T1 = peer-reviewed + reproduced; T2 = peer-reviewed but contested/single-study;
T3 = preprint/dissertation/pilot; T4 = speculation/popular-science.

Date compiled: 2026-07-18. Compiler: Neo (research subagent).

---

## SUB-Q1: Linguistics of superposition — does natural language hold ambiguity? (garden-path, ERP, rivalry)

### F1.1 — Osterhout & Holcomb / Osterhout, Holcomb & Swinney (1994), "Brain Potentials Elicited by Garden-Path Sentences"
- Journal: Journal of Experimental Psychology: LMC (1994).
- Key result: Garden-path (temporarily syntactically ambiguous) sentences elicit a **P600** — a late centro-parietal positivity (500–800 ms) at the disambiguating word, indexing syntactic reanalysis/repair. Foundational demonstration that the brain registers the moment a committed parse fails.
- Did NOT show: that both parses are held simultaneously. P600 is a *sequential* commit-then-reanalyze signature, i.e. evidence AGAINST superposition in the strong sense — the brain picks one reading, then repairs.
- Temperature: **T1** (replicated hundreds of times; P600 is a canonical ERP).

### F1.2 — N400/P600 biphasic pattern (review literature; e.g. Kuperberg; Brouwer et al.)
- Key result: Semantic integration difficulty = **N400** (centro-parietal negativity, 300–500 ms). Syntactic reanalysis = **P600**. Ambiguous material can elicit a biphasic N400→P600. Multiple information sources (lexical, semantic, discourse) are integrated *in parallel* at early stages, per plausibility/context modulation studies.
- Did NOT show: a stable dual-meaning "held" state; the components index *processing cost*, not co-present interpretations.
- Temperature: **T1** for the components themselves; **T2** for the "parallel integration" interpretation (contested between serial and parallel/constraint-satisfaction camps).

### F1.3 — Swets, Desmet, Clifton & Ferreira (2008), "Underspecification of syntactic ambiguities: evidence from self-paced reading"
- Journal: Memory & Cognition, 36(1). (Ferreira Lab, UC Davis.)
- Key result: **Direct evidence closest to "superposition."** Readers read globally ambiguous sentences *faster* than disambiguated ones (the "ambiguity advantage"). Interpreted as **strategic underspecification**: when the task does not demand resolution, comprehenders leave the structure UNRESOLVED — they do NOT commit to one meaning. Resolution only happens when questions force it.
- Did NOT show: that two full interpretations are *simultaneously active*; underspecification = a single vague/shallow representation, not two crisp superposed ones. Distinct from quantum-style superposition.
- Temperature: **T1** (widely cited, replicated; anchor of "good-enough processing").

### F1.4 — "Good-enough processing" 20-year review (Ferreira & Lowder lineage; Frontiers in Psychology, 2024)
- Key result: Comprehenders routinely build shallow, semantics-based representations "just good enough" for the task; deep syntactic commitment is optional. Supports a language faculty that *tolerates* unresolved ambiguity by default.
- Did NOT show: mechanism for holding contradictory meanings; it's about NOT computing, not about co-holding.
- Temperature: **T1/T2** (framework well-supported; scope of applicability still debated).

### F1.5 — Dholakia, Chwilla et al. (2016), "The N400 elicited by homonyms in puns: Two primes are not better than one"
- Journal: Psychophysiology, 53. (PubMed 27628438.)
- Key result: In puns both meanings of a homonym must be accessed. Pun context produced a *less negative* (primed) N400 vs neutral context, BUT the dual/pun context did NOT facilitate beyond a single biasing context. N400 amplitude reads as how consistently semantic features converge on a lexical item — even when two items must be activated.
- Did NOT show: additive/simultaneous boost from dual meaning ("two primes are not better than one" is a *negative* result against naive superposition-summation).
- Temperature: **T2** (single well-run study, specific paradigm).

### F1.6 — Binocular rivalry as model of neural competition (Alais 2012, WIREs Cog Sci; Blake & Logothetis lineage)
- Key result: Ambiguous input supporting two interpretations produces **bistable, alternating** perception via mutual inhibition — one percept always suppressed, never fused. Model for how the brain resolves (rather than holds) conflict.
- Relevance/caveat: The analogy "binocular rivalry in language" is a THEORETICAL import — rivalry is visual; direct linguistic-rivalry neural data is thin. Rivalry shows the brain *alternates*, it does NOT hold superposition; percepts are mutually exclusive.
- Did NOT show: any language application; no measured "linguistic rivalry" here.
- Temperature: **T1** for the visual phenomenon; the language analogy is **T4**.

### F1.7 — Garden-path jokes / "from incoherence to mirth" (Coulson & colleagues; PMC4429229)
- Key result: Garden-path *jokes* (reanalysis-driven humor) recruit reinterpretation processes measurable in ERP/neuro-cognition; the pleasure is tied to the reanalysis moment (the reversal). Ties Q-004's "reversal" intuition to measurable frame-shifting.
- Did NOT show: sustained superposition; humor arises AT the collapse/reframe, not from holding both.
- Temperature: **T2/T3**.

---

## SUB-Q2: Formal systems without an observer / subject position

### F2.1 — Lambda calculus ↔ Cartesian closed categories (Lambek; Lambek & Scott)
- Key result: Simply-typed λ-calculus (with products) is the internal language of a Cartesian closed category — proven equivalence. Both are systems of **pure functions/morphisms with no agent/subject term**. Composition, not predication. This is a genuine formal "language without I."
- Did NOT show: any claim about natural language or consciousness; it's math. No empirical measurement.
- Temperature: **T1** (established theorem, decades old).

### F2.2 — DisCoCat: Coecke, Sadrzadeh & Clark (2010), "Mathematical Foundations for a Compositional Distributional Model of Meaning"
- Venue: Lambek Festschrift / arXiv 1003.4394; later Computational Linguistics (Grefenstette & Sadrzadeh empirical work, 2015).
- Key result: Natural-language meaning modeled in a **compact closed monoidal category** — grammar (pregroup) and meaning (vector spaces) share one categorical structure; sentence meaning computed by morphisms/string diagrams (information flow), NOT by a subject applying to a predicate. The closest existing thing to "natural language rebuilt as pure relations/morphisms."
- Did NOT show: removal of the observer as a *goal*; it's an NLP formalism, and it still encodes subject-verb-object grammar types (subject position survives as a type, it's just not an agent).
- Temperature: **T1** for the framework; **T2** for empirical performance claims.

### F2.3 — Process algebras (π-calculus, CCS — Milner; CSP — Hoare)
- Key result: Systems describing concurrent *processes and communication* with no central subject/observer — only channels, names, interactions. Meaning = interaction patterns. (Surfaced via lambda/category searches; standard CS.)
- Did NOT show: application to natural language semantics of self; no neuro data.
- Temperature: **T1** (foundational CS).

### F2.4 — E-Prime (Bourland, from Korzybski's General Semantics)
- Key result: English with the verb "to be" (identity/predication "X IS Y") removed. Forces observer-relative phrasing: "This apple looks red *to me*" instead of "The apple is red." Paradoxically it makes the observer EXPLICIT rather than removing it — a constructed natural-language patch directly targeting the copula that hides the observer.
- Did NOT show: measured cognitive/neural effects. No controlled study of E-Prime on brain state or ambiguity tolerance found. Claims are rhetorical/philosophical.
- Temperature: **T4** (no empirical validation; popular/constructed-language status).

### F2.5 — "Observers, Symmetries, and the Hierarchy of Language Classes" (arXiv 2606.27407, 2026 preprint)
- Key result: Proposes a theory of computation *parameterized by the observer* — language classes relative to observer symmetries. Directly formalizes "observer position" as a tunable parameter in formal-language theory. Highly on-topic for Q-004's framing.
- Did NOT show: peer review; empirical grounding; connection to natural language cognition.
- Temperature: **T3** (preprint, unverified).

### F2.6 — Categorical Tools for NLP (arXiv 2212.06636)
- Key result: Survey of category-theoretic machinery applied to NLP (functorial semantics, string diagrams). Supports F2.2 as a live research program.
- Temperature: **T3** (survey preprint).

Note: NO existing *natural* language that fully lacks a subject/observer position was found. Ergative languages redistribute subject/object roles (S=O of transitive) but retain an observer. Constructed attempts (E-Prime, Toki Pona minimalism) surfaced only anecdotally, none with measurement.

---

## SUB-Q3: Chiasmus (ABBA) — cognitive/neuro basis of "depth"

### F3.1 — Menninghaus et al., "Parallelisms and deviations: two fundamentals of an aesthetics of poetic diction" (PMC10725771; ~2023)
- Group: Max Planck Institute for Empirical Aesthetics.
- Key result: Across 3 text genres, higher **parallelism** scores raised comprehensibility AND aesthetic liking; positive parallelism effects significantly stronger than negative "deviation" effects. Correlation parallelism↔aesthetic rating in poetry reported around **r ≈ 0.53, p < .001**. Mechanism proposed: processing **fluency** — predictable structure eases processing, which reads as beauty. Chiasmus is a special case of parallelism (mirror parallelism).
- Did NOT show: chiasmus-SPECIFIC neural data; the studies are behavioral ratings of parallelism broadly, not ABBA in isolation, and not fMRI/EEG of chiasmus.
- Temperature: **T2** (solid MPI behavioral program; chiasmus-specific extrapolation is weaker).

### F3.2 — "Aesthetic appreciation of poetry correlates with ease of processing in event-related potentials" (Cogn Affect Behav Neurosci, 2015; Springer)
- Key result: EEG/ERP evidence that aesthetic appreciation of poetry tracks *ease of processing* — fluency has an electrophysiological signature. Supports the fluency account underlying why symmetric/parallel (incl. chiastic) forms feel good.
- Did NOT show: chiasmus specifically; correlational, not causal; no ABBA manipulation.
- Temperature: **T2/T3**.

### F3.3 — "The emotional and aesthetic powers of parallelistic diction" (Menninghaus et al., Poetics, ScienceDirect S0304422X16301693)
- Key result: Parallelistic diction independently drives emotional and aesthetic response; listeners rate metered/rhyming/parallel stanzas higher on rhythmicity and liking.
- Did NOT show: neural localization; chiasmus vs other parallelism dissociation.
- Temperature: **T2**.

### F3.4 — "Computational Discovery of Chiasmus in Ancient Religious Text" (arXiv 2501.10739, 2025)
- Key result: NLP method to detect chiastic (ABBA) structures automatically in large corpora. Confirms chiasmus is a stable, detectable formal pattern (not reader projection) but is a detection tool, not a cognition study.
- Did NOT show: any brain measurement or "why it feels deep."
- Temperature: **T3** (preprint, methods).

### F3.5 — "Chiasmus: a phenomenon of language, body and perception" (Edinburgh dissertation, era.ed.ac.uk/handle/1842/37291)
- Key result (grey data): PhD thesis framing chiasmus via embodied cognition / Merleau-Ponty's "chiasm" — reversibility of perceiver/perceived. Theoretical link between the rhetorical figure and the observer-fold. Directly relevant to Q-004's "reversal kills the collapse" intuition.
- Did NOT show: quantitative neural data; it's philosophy/phenomenology.
- Temperature: **T4** (dissertation, non-empirical).

VERDICT sub-Q3: NO direct EEG/fMRI study of chiasmus-as-such was found. Best available = parallelism/fluency behavioral + ERP work from MPI Empirical Aesthetics, from which chiasmus effects are inferred, not measured. Popular claims about "X-shape matches bipedal posture/hemispheric interaction" are **T4** (unsourced).

---

## SUB-Q4 & Q5 overlap addressed below (Q4 = practical test → design note; Q5 = mantras/koans data)

### SUB-Q5: Mantras, koans, prayer — brain-state data

### F5.1 — Kalyani, Venkatasubramanian et al. (2011), "Neurohemodynamic correlates of 'OM' chanting: a pilot fMRI study"
- Journal: International Journal of Yoga, 4(1):3–6. NIMHANS Bangalore. (PubMed 21654968.)
- Method: fMRI, n=12 healthy right-handers. "OM" chanting vs "ssss" pronunciation vs rest.
- Key result: Audible OM chanting produced **significant bilateral DEACTIVATION** in orbitofrontal, anterior cingulate, parahippocampal gyri, thalami, hippocampi, and right amygdala. The control "ssss" produced NO such (de)activation. Authors liken it to vagus-nerve-stimulation-induced limbic deactivation.
- Did NOT show: causation of any subjective state; tiny pilot n=12; no meditation-experience control; superposition/observer claims absent. The OM-vs-ssss contrast is the load-bearing finding (meaningful sound ≠ noise).
- Temperature: **T2/T3** (peer-reviewed but pilot, small n, not independently reproduced at scale).

### F5.2 — Berkovich-Ohana et al. (2015), "Repetitive speech elicits widespread deactivation in the human cortex: the 'Mantra' effect?"
- Journal: Brain and Behavior, 5(7):e00346. (PMC4511287.)
- Method: fMRI, n=23 NON-meditators, covert repetition of a single word vs resting state.
- Key result: Simple covert word repetition → **widespread unidirectional BOLD reduction centered on the Default Mode Network** (self-related processing). Deactivation resembles meditation effects but from bare repetition alone — suggests the "mantra" mechanism is partly the repetition itself, not the sacred content.
- Did NOT show: that meaning/sacredness adds anything (control was non-meditators, generic word); no long-term or trait claims; DMN-down ≠ any specific phenomenology.
- Temperature: **T2** (peer-reviewed, clean design, but single study).

### F5.3 — Perry et al. (2025), "Neural Correlates of Chanting: A Systematic Review" (WIREs Cognitive Science)
- Key result: Systematic review across chanting/mantra studies: convergent finding = **DMN modulation** (esp. posterior cingulate, hippocampus deactivation) plus engagement of attention/emotion regulation regions (prefrontal, insula, cingulate); EEG shows **increased theta** (and some alpha). Consolidates F5.1/F5.2 into a reviewed pattern.
- Did NOT show: standardized effect sizes across heterogeneous studies; strong causal or mechanistic claims; the field is small and methodologically varied.
- Temperature: **T2** (review of mostly T2/T3 primary studies).

### F5.4 — Mantra Meditation Suppression of DMN "Beyond an Active Task" (J. Cognitive Enhancement, 2017; pilot)
- Key result: Mantra meditation reduced DMN activity even relative to an active control task — DMN suppression exceeds ordinary task-based suppression.
- Did NOT show: large n; long-term reproduction (pilot).
- Temperature: **T3** (pilot).

### F5.5 — Temporal Dynamics of DMN in meditation (PMC4956663)
- Key result: DMN microstate duration shifts in meditative states; the shift correlated NEGATIVELY with years of experience — a *trait* effect of long practice on DMN temporal dynamics.
- Did NOT show: specific to mantras vs other meditation; correlational.
- Temperature: **T2/T3**.

### F5.6 — Hsu / "A Paradox of Koan Study and Why Psychology Should Take Note" (Human Arenas, 2018; Springer)
- Key result: Theoretical/psychological analysis of koans as engineered cognitive paradoxes that block analytic resolution and force a non-analytic "shift." Argues psychology under-studies this.
- Did NOT show: ANY brain measurement. It is argument, not data. Popular claims of "elevated theta/alpha during koan contemplation" and "gamma synchrony = insight" trace to non-peer-reviewed blogs (choosemuse, spiritualmeaningsguide), NOT to controlled koan studies.
- Temperature: **T4** for the specific koan-EEG claims circulating online; **T3** for the Human Arenas conceptual paper.

VERDICT sub-Q5: Mantra/chanting has REAL, peer-reviewed brain data (DMN deactivation, theta increase) — F5.1–F5.3 are the T2 crumbs. Koans do NOT — koan neuroscience is currently vapor (T4). The strongest engineering claim supported by data: *repetition suppresses the self-referential (DMN) network*, and this happens even without sacred content (Berkovich-Ohana). This is the most concrete "language patch changes brain state" result in the whole file.

---

## SUB-Q6 (Q5 in file): Ambiguity tolerance as measurable trait ↔ creativity/openness

### F6.1 — Zenasni, Besançon & Lubart (2008), "Creativity and Tolerance of Ambiguity: An Empirical Study"
- Journal: Journal of Creative Behavior. (n≈120 French participants.)
- Key result: Tolerance of ambiguity **significantly predicted** creativity-task scores (fluency, flexibility, originality), r ≈ **.22–.35** after controlling for intelligence. A named, reproducible correlation.
- Did NOT show: causation/direction; modest effect sizes; single sample.
- Temperature: **T2** (peer-reviewed, moderate but replicated-in-spirit).

### F6.2 — Sun et al. (2025), openness↔humor production, mediated by cognitive flexibility & ambiguity tolerance (PsyCh Journal; PMC11787877)
- Key result: Openness to Experience positively predicts humor-production ability; **ambiguity tolerance partially mediates** this. Places ambiguity tolerance as a mechanistic pathway from openness → creative output.
- Did NOT show: experimental causation (correlational/mediation model); self-report measures.
- Temperature: **T2**.

### F6.3 — Big Five / Openness measurement literature
- Key result: Ambiguity tolerance loads on **Openness to Experience**; positively correlates with openness and extraversion, negatively with neuroticism. Standard psychometric constructs (MSTAT, Budner scale) make it measurable.
- Did NOT show: neural correlate; the construct has known scale-validity debates.
- Temperature: **T1** for the openness↔ambiguity-tolerance association; **T2** for scale specifics.

### F6.4 — Openness vs Intellect differentially predict arts vs sciences creativity (Kaufman/DeYoung lineage)
- Key result: Openness (aesthetic/ambiguity-embracing facet) predicts ARTS creative achievement; Intellect predicts SCIENCES. Ambiguity tolerance aligns with the Openness/arts side.
- Temperature: **T2**.

---

## SUMMARY: where the T1–T2 crumbs actually are

1. **Language DOES tolerate unresolved ambiguity — but as underspecification, not superposition.** Swets/Ferreira (T1) is the strongest anchor: readers leave ambiguity unresolved when the task allows. This is "don't collapse," not "hold both crisply."
2. **The brain commits then repairs (P600) — evidence AGAINST strong superposition.** Osterhout (T1). Puns show "two primes not better than one" (T2) — no additive dual-meaning boost.
3. **Observer-free formal languages EXIST and are proven** (λ-calculus ↔ CCC, process algebras, DisCoCat) — T1 math — but none are natural languages, and none were built to remove *consciousness's* observer.
4. **Chiasmus-specific neuro data does NOT exist.** Best proxy: parallelism→fluency→aesthetic-liking (Menninghaus/MPI, r≈.53, T2) + ERP fluency signature (T2/T3). The "feels deep because X-shape/hemispheres" claims are T4.
5. **Mantra/repetition has real data: DMN deactivation + theta increase** (Kalyani T2/T3, Berkovich-Ohana T2, Perry review T2). Crucially, repetition ALONE suppresses the self-network even without sacred meaning. Koan neuroscience = T4 (no controlled studies).
6. **Ambiguity tolerance is measurable and correlates with creativity/openness** (Zenasni r≈.22–.35 T2; openness link T1).

### For Q-004's practical test (sub-Q4)
Existing paradigms that could be borrowed for an "observer vs observer-free text" experiment:
- Dependent measures with precedent: ambiguity-tolerance scales (MSTAT/Budner, F6.x); self-paced reading times + offline comprehension Qs (Swets paradigm, F1.3); N400/P600 ERP (F1.1–1.2); DMN BOLD or EEG theta if imaging available (F5.x); aesthetic-liking + rhythmicity ratings (Menninghaus, F3.x); 24h retention via standard recall.
- Strongest measurable predicted effect, by existing data: an "observer-free / repetitive / parallel" text should (a) reduce DMN/self-referential engagement, (b) increase theta, (c) read faster if left underspecified, (d) score higher on aesthetic-liking via fluency. NONE of this has been tested with an explicit "remove the subject position" manipulation — that specific experiment does not exist in the literature found.

---

## Sources
- Osterhout, Holcomb & Swinney (1994) — https://faculty.washington.edu/losterho/osterhout_holcomb_swinney_1994.pdf
- Garden-path telicity ERP — https://pmc.ncbi.nlm.nih.gov/articles/PMC2720995/
- Garden-path jokes — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4429229/
- Swets, Desmet, Clifton & Ferreira (2008) — https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Swets-et-al.-2008_UnderspecificationAmbiguities_Mem-Cog.pdf
- Good-enough processing 20-yr review (2024) — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1323700/full
- Dholakia & Chwilla, puns/N400 (2016) — https://pubmed.ncbi.nlm.nih.gov/27628438/
- Binocular rivalry review (Alais 2012) — https://wires.onlinelibrary.wiley.com/doi/abs/10.1002/wcs.151
- Neural conflict in binocular rivalry (bioRxiv) — https://www.biorxiv.org/content/10.1101/2019.12.19.873141.full.pdf
- Lambda calculus (nLab) — https://ncatlab.org/nlab/show/lambda-calculus
- Category theory & lambda calculus equivalence — https://keikun555.github.io/documents/lambda.pdf
- DisCoCat (Wikipedia overview) — https://en.wikipedia.org/wiki/DisCoCat
- Grefenstette & Sadrzadeh concrete models (Comp Ling) — https://direct.mit.edu/coli/article/41/1/71/1501/
- Categorical Tools for NLP (arXiv 2212.06636) — https://arxiv.org/pdf/2212.06636
- Observer-parameterized computation (arXiv 2606.27407) — https://arxiv.org/pdf/2606.27407
- E-Prime (Wikipedia) — https://en.wikipedia.org/wiki/E-Prime
- Menninghaus, Parallelisms and deviations (PMC10725771) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10725771/
- Aesthetic appreciation of poetry ↔ ERP fluency (2015) — https://link.springer.com/article/10.3758/s13415-015-0396-x
- Emotional/aesthetic powers of parallelistic diction (Poetics) — https://www.sciencedirect.com/science/article/abs/pii/S0304422X16301693
- Computational discovery of chiasmus (arXiv 2501.10739) — https://arxiv.org/pdf/2501.10739
- Chiasmus phenomenology dissertation (Edinburgh) — https://era.ed.ac.uk/handle/1842/37291
- Kalyani et al., OM chanting fMRI (2011) — https://pmc.ncbi.nlm.nih.gov/articles/PMC3099099/
- Berkovich-Ohana et al., Mantra effect (2015) — https://pmc.ncbi.nlm.nih.gov/articles/PMC4511287/
- Perry et al., Neural Correlates of Chanting review (2025) — https://wires.onlinelibrary.wiley.com/doi/10.1002/wcs.70018
- Mantra DMN suppression pilot (2017) — https://link.springer.com/article/10.1007/s41465-017-0028-1
- DMN temporal dynamics in meditation — https://pmc.ncbi.nlm.nih.gov/articles/PMC4956663/
- Koan paradox / psychology (Human Arenas 2018) — https://link.springer.com/article/10.1007/s42087-018-0036-4
- Zenasni, Besançon & Lubart, creativity & tolerance of ambiguity — https://www.researchgate.net/publication/253935530
- Sun et al., openness/humor/ambiguity tolerance (2025) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11787877/
- Openness vs Intellect & creative achievement — https://www.researchgate.net/publication/269286890
