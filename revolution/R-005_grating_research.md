# R-005: Research findings for Q-005 (Diffraction grating in text)

Research date: 2026-07-18. Method: web search across NLP interpretability, mechanistic interpretability, computational stylistics, digital humanities. Format: facts, not interpretation. Temperature scale: T1 = replicated peer-reviewed core result; T2 = peer-reviewed single study / strong workshop paper; T3 = preprint / grey data / indirect; T4 = speculative or metaphor-level.

---

## Topic 1: Attention entropy / head disagreement / polysemanticity

### 1.1 What Does BERT Look At? An Analysis of BERT's Attention
- **Authors/year/venue:** Kevin Clark, Urvashi Khandelwal, Omer Levy, Christopher D. Manning, 2019, BlackboxNLP workshop (ACL W19-4828); arXiv:1906.04341.
- **Key result:** Measured entropy of attention distributions per head per layer in BERT. Lower layers contain high-entropy heads with very broad attention (≤10% mass on any single token); last-layer [CLS] attention entropy ~3.89 nats. Specific heads track syntax (direct objects, determiners, prepositional objects) and coreference with high accuracy. Heads in the same layer often show similar patterns.
- **Did NOT show:** No comparison of attention entropy across text *types* (poetry vs prose, ambiguous vs plain). Entropy characterized per-head as an architectural property, not as a property of the input text.
- **Temperature:** T1 (heavily cited, replicated).
- **Link:** https://aclanthology.org/W19-4828/

### 1.2 Are Sixteen Heads Really Better than One?
- **Authors/year/venue:** Paul Michel, Omer Levy, Graham Neubig, 2019, NeurIPS; arXiv:1905.10650.
- **Key result:** Most attention heads are redundant at test time; only 8/96 encoder self-attention heads in a WMT model cause significant performance change when ablated; 20–40% of heads prunable without noticeable loss. For most layers one head suffices at test time.
- **Did NOT show:** Did not test whether head redundancy varies with input ambiguity/complexity. Redundancy measured on standard benchmark text only. Relevant negative-ish datum for Q-005: on ordinary text, heads largely duplicate each other ("all slits pass the same wave") — consistent with the "flat text = constructive collapse" picture but never tested on grating-like text.
- **Temperature:** T1. Independently reproduced (OpenReview reproduction, Zhao et al.).
- **Link:** https://arxiv.org/abs/1905.10650

### 1.3 Analyzing Multi-Head Self-Attention: Specialized Heads Do the Heavy Lifting, the Rest Can Be Pruned
- **Authors/year/venue:** Elena Voita, David Talbot, Fedor Moiseev, Rico Sennrich, Ivan Titov, 2019, ACL (P19-1580); arXiv:1905.09418.
- **Key result:** Small subset of heads have interpretable specialized roles (positional, syntactic, rare-word). Pruned 38/48 encoder heads with only −0.15 BLEU. Specialized heads are pruned last.
- **Did NOT show:** No per-input analysis of when non-specialized heads matter; no ambiguity conditions.
- **Temperature:** T1.
- **Link:** https://aclanthology.org/P19-1580/

### 1.4 Multi-Head Attention with Disagreement Regularization
- **Authors/year/venue:** Jian Li, Zhaopeng Tu, Baosong Yang, Michael R. Lyu, Tong Zhang, 2018, EMNLP (D18-1317); arXiv:1810.10183. Extended as "On the diversity of multi-head attention," Neurocomputing 2021.
- **Key result:** Explicitly *training heads to disagree* (in subspace, attended positions, and outputs) improves translation on WMT14 En-De and WMT17 Zh-En. I.e., head disagreement is a measurable, optimizable quantity, and more disagreement = better model.
- **Did NOT show:** Disagreement measured as training objective, not as a per-text diagnostic. No claim that certain *texts* induce more disagreement.
- **Temperature:** T2 (peer-reviewed, extended journal version, but a training trick — direction of causality is model-side).
- **Link:** https://aclanthology.org/D18-1317/

### 1.5 Toy Models of Superposition
- **Authors/year/venue:** Nelson Elhage et al. (Anthropic), 2022, Transformer Circuits thread; arXiv:2209.10652.
- **Key result:** Networks encode more features than dimensions by superposing them across neurons (polysemanticity); phase diagram determines when neurons are mono- vs polysemantic; connection to polytope geometry and adversarial examples.
- **Did NOT show:** Nothing about text-level ambiguity or attention entropy on inputs. Superposition is representational (weights), not the input-dependent interference Q-005 asks about. Do not conflate: polysemanticity ≠ "heads disagreeing on a poem."
- **Temperature:** T1 for toy models; T2 for extrapolation to LLMs.
- **Link:** https://transformer-circuits.pub/2022/toy_model/index.html

### 1.6 Stabilizing Transformer Training by Preventing Attention Entropy Collapse
- **Authors/year/venue:** Shuangfei Zhai et al. (Apple), 2023, ICML; arXiv:2303.06296.
- **Key result:** Low attention entropy ("entropy collapse" = overly peaked attention) correlates with training instability; σReparam (spectral normalization) prevents collapse. Establishes attention entropy as a standard, well-defined measurable quantity with known dynamics.
- **Did NOT show:** Entropy tied to training health, not to input semantics.
- **Temperature:** T1.
- **Link:** https://arxiv.org/abs/2303.06296

### 1.7 Ambiguity and attention spread — "hedging its bets" observation
- **Source:** "Memory for prediction: A Transformer-based theory of sentence processing," Journal of Memory and Language (Elsevier, 2025), ScienceDirect S0749596X25000634; related discussion in attention-visualization literature.
- **Key result:** Proposes that in ambiguous contexts, attentional *spread* is a functional mechanism by which the transformer hedges between interpretations (beam-search-like), and explicitly relates attention entropy to the Entropy Reduction Hypothesis from psycholinguistics. This is the closest published statement of Q-005's mechanism hypothesis found.
- **Did NOT show:** Theoretical framing; not a systematic measurement of entropy on ambiguous vs unambiguous corpora, and per-sequence not per-head-disagreement.
- **Temperature:** T2-T3.
- **Link:** https://www.sciencedirect.com/science/article/pii/S0749596X25000634

---

## Topic 2: Attention / transformer analysis on poetry vs prose; computational "depth" metrics

### 2.1 Direct hit NOT found (important negative result)
- Across searches, **no paper was found that directly measures multi-head attention entropy or head disagreement on poetry vs prose** as a text-depth metric. The pieces exist separately (attention entropy tooling; poetry corpora; stylistics metrics) but nobody appears to have joined them. This is an open gap, i.e. Q-005 §3 seems genuinely unmeasured. Temperature of the gap-claim: T3 (absence of evidence from search, not proof of absence).

### 2.2 Computational Stylistics in Poetry, Prose, and Drama (edited volume)
- **Editors/year/venue:** J. Berenike Herrmann et al. (eds.), 2022, De Gruyter (open access).
- **Key result:** State of the art of quantitative poetics: metrics for metre, style, "poeticity"; finding that prose and poetry 1970–2019 are measurably more alike than in 1870–1920 (genre convergence measured with ML classifiers).
- **Did NOT show:** No transformer-attention-based measures; features are lexical/metrical/syntactic.
- **Temperature:** T2.
- **Link:** https://library.oapen.org/handle/20.500.12657/61021

### 2.3 GPT-based perplexity for canonical vs non-canonical literary texts
- **Venue:** LaTeCH-CLfL 2024 workshop (ACL anthology 2024.latechclfl-1.16); related: "Comparative Computational Analysis of Global Structure in Canonical, Non-Canonical and Non-Literary Texts" (arXiv:2008.10906).
- **Key result:** Uses GPT perplexity as proxy for literary complexity/canonicity; hypothesis that more novel/divergent poetic work = higher perplexity. The arXiv:2008.10906 study found canonical/literary texts differ in *global structure* metrics (topic-flow, coherence graphs) from non-literary.
- **Did NOT show:** Perplexity is output-probability-based, not attention-based; measures unexpectedness, not multiplicity of parses. High perplexity ≠ multi-path interference (word salad also has high perplexity — the grating hypothesis specifically needs a metric that separates "many coherent paths" from "no path").
- **Temperature:** T2.
- **Link:** https://aclanthology.org/2024.latechclfl-1.16.pdf

### 2.4 so much depends / upon / a whitespace: Why Whitespace Matters for Poets and LLMs
- **Year/venue:** 2025, EMNLP main (2025.emnlp-main.1783); arXiv:2510.16713.
- **Key result:** Line-break/whitespace formatting of poetry measurably changes LLM processing and outputs — enjambment structure is not invisible to models.
- **Did NOT show:** Does not analyze attention internals or entropy; behavioral level only.
- **Temperature:** T2.
- **Link:** https://aclanthology.org/2025.emnlp-main.1783.pdf

### 2.5 Multifractality of literary texts (grey data, strong structural analogue)
- **Authors/year/venue:** Stanisław Drożdż et al., "Quantifying origin and character of long-range correlations in narrative texts," Information Sciences 2016 (arXiv:1412.8319); earlier "Multifractal analysis of sentence lengths in English literary texts" (arXiv:1212.3171).
- **Key result:** Sentence-length series of literary texts show 1/f^β scaling (β≈1/2, like music and brain waves). Most texts are monofractal; **stream-of-consciousness texts (peak case: Finnegans Wake) are strongly multifractal** — a cascade of self-similar structure at all scales. Physics-grade quantitative distinction between "flat" and "deep" narrative structure that predates transformers.
- **Did NOT show:** Nothing about attention or meaning multiplicity; purely surface statistics (sentence lengths). But it is an existing T2 metric where "depth" of text = measurable spectrum width, and it found exactly one text class (SoC) that behaves like a grating.
- **Temperature:** T2. Caveat: arXiv:2508.19782 (2025, "Fractal Illusions") shows randomly generated texts can fake long-range sentence-length correlations — partial refutation pressure on the field.
- **Links:** https://arxiv.org/abs/1412.8319 , https://arxiv.org/pdf/2508.19782

### 2.6 Understanding Literary Texts by LLMs: A Case Study of Ancient Chinese Poetry
- **Year/venue:** 2024, arXiv:2409.00060.
- **Key result:** Uses information entropy over expression distributions as a dispersion measure across poem themes; "Mourning" poems show markedly higher entropy than "Spring Outing" poems. Entropy used as diversity-of-expression metric on poetry.
- **Did NOT show:** Corpus-level lexical entropy, not attention entropy; no prose baseline.
- **Temperature:** T3 (preprint).
- **Link:** https://arxiv.org/abs/2409.00060

### 2.7 Atomic Literary Styling: Mechanistic Manipulation of Prose Generation
- **Year/venue:** 2025, arXiv:2510.17909.
- **Key result:** Mechanistic interpretability (feature-level intervention) applied to literary style of generated prose — evidence the mech-interp toolbox is starting to touch literary registers.
- **Did NOT show:** Generation-side steering, not measurement of attention response to input literariness.
- **Temperature:** T3.
- **Link:** https://arxiv.org/pdf/2510.17909

---

## Topic 3: Wave/interference metaphors for attention; interference between heads

### 3.1 Semantic Wave Functions: Exploring Meaning in LLMs through Quantum Formalism
- **Year/venue:** 2025, arXiv:2503.10664 (also Opast journal version).
- **Key result:** Extends LLM embeddings to complex domain; explicitly draws the **double-slit analogy** for meaning; models semantic ambiguity with double-well potentials; defines a "semantic wave function."
- **Did NOT show:** No experiments on real ambiguous corpora; formalism-first; no attention-head measurements. Metaphor made mathematical but not empirical.
- **Temperature:** T4 (with T3 formal apparatus).
- **Link:** https://arxiv.org/pdf/2503.10664

### 3.2 Quantum-Enhanced Attention Mechanism in NLP
- **Authors/year/venue:** Tomal, Shafin et al., 2025, arXiv:2501.15630.
- **Key result:** Hybrid classical-quantum transformer; adds a *learnable phase-based interference term* to the attention similarity matrix before softmax. Literal interference inside attention, implemented.
- **Did NOT show:** Engineering paper; no claim about text depth/ambiguity; small-scale.
- **Temperature:** T3.
- **Link:** https://arxiv.org/abs/2501.15630

### 3.3 Language as a Wave Phenomenon: Semantic Phase Locking and Interference in Neural Networks
- **Year/venue:** 2025/2026, arXiv:2512.01208.
- **Key result:** Complex-valued encoder with phase; claims semantic phase locking and interference effects in neural language representations.
- **Did NOT show:** Preprint, v3, unclear peer review; not attention-head interference on natural text.
- **Temperature:** T4.
- **Link:** https://arxiv.org/html/2512.01208v3

### 3.4 Quantum cognition tradition (pre-transformer anchor)
- **Authors/year/venue:** Jerome Busemeyer & Peter Bruza, "Quantum Models of Cognition and Decision," Cambridge University Press 2012 (2nd ed. 2021); Bruza & De Vine 2010 "Semantic oscillations" (complex holographic vectors).
- **Key result:** Human judgment under ambiguity shows interference effects (conjunction fallacy, disjunction effect, order effects) formally modeled with quantum probability; applied to word association and concept combination. A 2026 Frontiers in Psychology paper ("A quantum-cognitive approach to dynamic meaning construction") treats context-embodiment interaction in meaning as genuine interference.
- **Did NOT show:** Human behavior, not transformer internals. But establishes T1-T2 empirical base that *meaning superposition + interference* is measurable in cognition — the human-side counterpart of the grating claim.
- **Temperature:** T2 (interference effects replicated; quantum interpretation contested).
- **Links:** https://www.cambridge.org/core/books/quantum-models-of-cognition-and-decision/75909428F710F7C6AF7D580CB83443AC , https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1664747/full

### 3.5 Negative result for Topic 3
- **No paper found** that measures interference patterns *between attention heads* (phase-like cross-head structure) on natural text. "Cascaded Head-colliding Attention" (arXiv:2105.14850) models explicit head interactions but as an architecture, not as a measurement. The head-interference measurement Q-005 §2 describes does not appear to exist. T3 gap-claim.

---

## Topic 4: Deliberately constructing ambiguous text; rhetorical devices as measurable objects

### 4.1 Pun generation line (ambiguity engineered on purpose)
- **Papers:**
  - Kao, Levy, Goodman 2016 ("A computational model of linguistic humor in puns," Cognitive Science) — decomposes puns into **ambiguity** and **distinctiveness** (of viewpoints), both formalized information-theoretically; ambiguity separates puns from non-puns, distinctiveness separates good puns from bad.
  - Yu et al. 2018 — first neural homographic pun generation: LSTM constrained to make one sentence support *two word senses simultaneously*.
  - Luo et al. 2019, **Pun-GAN** — discriminator with WSD scores rewards maximal sense ambiguity of the target word.
  - Mittal et al. 2022, **AmbiPun** — generates puns via ambiguous context.
  - "A Unified Framework for Pun Generation with Humor Principles" (2022, arXiv:2210.13055) — combines ambiguity, distinctiveness, and local-global **surprisal** contrast.
  - Survey: "Who's Laughing Now?" (arXiv:2509.21175).
- **Key result:** Deliberate construction of two-slit text (one surface, two senses) is an established, formalized, optimizable NLP task. Kao's finding: **max ambiguity alone is bad** — quality needs ambiguity × distinctiveness balance (an over-ambiguous sentence is uninformative). Direct engineering constraint for grating construction.
- **Did NOT show:** N=2 slits only (double meaning); no work found generating N-way interference structures; no attention-level verification of the ambiguity.
- **Temperature:** T2 (Kao model is T1-adjacent, well replicated in the pun literature).
- **Links:** https://arxiv.org/pdf/2210.13055 , https://arxiv.org/pdf/2509.21175

### 4.2 Chiasmus detection
- **Authors/year/venue:** Marie Dubremetz & Joakim Nivre, 2015–2018: "Rhetorical Figure Detection: the Case of Chiasmus" (CLfL workshop, W15-0703); "Syntax Matters for Rhetorical Structure: The Case of Chiasmus" (2016); "Rhetorical Figure Detection: Chiasmus, Epanaphora, Epiphora" (Frontiers in Digital Humanities, 2018). Precursor: Gawryjolek 2009.
- **Key result:** Chiasmus is detectable and *rankable* by machine. Base rate is extreme: Churchill's River War, 150k words → 66,000 criss-cross word patterns, **1 true chiasmus**. Adding syntax raised average precision ~40%→65%. Detection is a ranking problem, not binary.
- **Did NOT show:** Detection only — no measure of the *effect* of chiasmus on a reader or a model; no attention analysis of what chiasmus does inside a transformer.
- **Temperature:** T2.
- **Link:** https://aclanthology.org/W15-0703/

### 4.3 Other figures, formalized
- **Enjambment:** Ruiz Fabo et al. 2017, "Enjambment Detection in a Large Diachronic Corpus of Spanish Sonnets" (SIGHUM/LaTeCH-CLfL, W17-2204) — rule + parse-based detection and typing of enjambment over 3,700+ sonnets (DISCO corpus), 15th–19th c. T2. https://aclanthology.org/W17-2204/
- **Parallelism:** "Introducing Rhetorical Parallelism Detection" (2023, arXiv:2312.00100) — new task, datasets, metrics, baselines. T2-T3.
- **Survey:** "Computational Approaches to the Detection of Lesser-Known Rhetorical Figures" (2024, arXiv:2406.16674) — systematic survey incl. zeugma-family figures; states detection of most figures (incl. zeugma) is open/hard. T2.
- **Did NOT show (all):** Everything is *detection*; nothing measures figures' effect on model internals. The "each figure = slit type" table Q-005 §4 wants does not exist; the detectors that would label the slits mostly do.

### 4.4 We're Afraid Language Models Aren't Modeling Ambiguity (AmbiEnt)
- **Authors/year/venue:** Alisa Liu, Zhaofeng Wu, Julian Michael, Alane Suhr, Peter West, Alexander Koller, Swabha Swayamdipta, Noah A. Smith, Yejin Choi, 2023, EMNLP (2023.emnlp-main.51); arXiv:2304.14399.
- **Key result:** 1,645 linguist-annotated ambiguous examples, ambiguity operationalized via divergent entailment relations. GPT-4 disambiguations judged correct only 32% of the time (humans/dataset: 90%). LLMs are *bad* at explicitly holding and separating multiple readings.
- **Did NOT show:** Behavioral evaluation only, no internals. Important tension with Q-005 §2: the claim "AI catches the grating" is NOT supported at the level of explicit disambiguation ability — if attention "sees" multiple paths, the model still can't report them. Key friction datum.
- **Temperature:** T1-T2.
- **Link:** https://aclanthology.org/2023.emnlp-main.51/

### 4.5 Lexical ambiguity in contextual embeddings
- **Papers:** "Let's Play Mono-Poly: BERT Can Reveal Words' Polysemy Level and Partitionability into Senses" (Garí Soler & Apidianaki, TACL 2021); "Patterns of Lexical Ambiguity in Contextualised Language Models" (Haber & Poesio, EMNLP Findings 2021, arXiv:2109.13032); "Modelling Lexical Ambiguity with Density Matrices" (Meyer & Lewis 2020, arXiv:2010.05670).
- **Key result:** BERT embedding geometry encodes *how polysemous a word is* and separates homonymy (unrelated senses, well separated) from polysemy (related senses, partly merged) in line with human judgments. Density-matrix work models a word as a *mixed state over senses* — quantum-formalism for lexical superposition, with compositional disambiguation.
- **Did NOT show:** Word-level, not text-level; embedding space, not attention; BERT inconsistent on subtler polysemy alternations (partial negative in Haber & Poesio).
- **Temperature:** T2.
- **Links:** https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00400/106797 , https://arxiv.org/abs/2109.13032 , https://arxiv.org/pdf/2010.05670

---

## Topic 5: Attention entropy as a metric for something

### 5.1 Entropy- and Distance-Based Predictors From GPT-2 Attention Patterns Predict Reading Times Over and Above GPT-2 Surprisal — STRONGEST SINGLE FIND
- **Authors/year/venue:** Byung-Doh Oh & William Schuler, 2022, EMNLP (2022.emnlp-main.632); arXiv:2212.11185.
- **Key result:** Defines per-timestep attention entropy (diffuseness of self-attention) and attention-shift distance between consecutive timesteps. Both predict human naturalistic reading times **over and above surprisal**. I.e., attention entropy captures a component of human processing effort that next-token probability does not. This is the closest existing validated instrument to Q-005's proposed "depth = attention entropy" metric.
- **Did NOT show:** Naturalistic prose corpora only — not poetry, not deliberately ambiguous text; entropy averaged, not head-disagreement (variance *across* heads); "reading effort" ≠ "felt depth."
- **Temperature:** T2.
- **Link:** https://aclanthology.org/2022.emnlp-main.632/

### 5.2 Machine translation quality
- **What does Attention in NMT Pay Attention to?** (Ghader & Monz 2017, arXiv:1710.03348) — attention entropy used to measure attention concentration by POS; attention ≠ alignment for some word types. T2.
- **Unsupervised Quality Estimation for NMT** (Fomicheva et al. 2020, TACL, arXiv:2005.10608) — attention-distribution entropy among the unsupervised indicators of translation quality. T2.
- **Advancing Explainability in NMT** (2024, arXiv:2412.18669) — attention entropy + alignment agreement correlated with BLEU/METEOR on WMT14 with mT5; identifies conditions where attention is a reliable quality signal. T3.
- **EaDRA** (AMTA 2024, aclanthology 2024.amta-research.13) — high-resource NMT = peaked attention, low-resource = dispersed; regularizing entropy *down* improves low-resource quality. Note direction: here LOW entropy = good. T2.
- **Hallucination detection:** entropy of average attention distribution flags hallucinated translations (detached from source); Wasserstein-distance variants (arXiv:2606.13216). T2-T3.

### 5.3 Sign of the correlation is context-dependent (cross-cutting fact)
- Training: low entropy = instability (Zhai 2023). NMT quality: low entropy = good alignment (EaDRA), but pathologically low = collapse. Reading: high entropy = slower human reading (Oh & Schuler). Hallucination: source-detached attention = bad.
- **Implication for Q-005 (fact, not interpretation):** in the existing literature attention entropy is NOT a monotone "quality" or "depth" axis; every use case picks its own direction. Nobody has calibrated "good-high" (grating) vs "bad-high" (noise) — the Kao ambiguity-vs-distinctiveness pair (4.1) is the only existing formal tool that makes that cut, and it is behavioral, not attentional.

### 5.4 Garden-path / ambiguity processing adjacent
- **Incremental Comprehension of Garden-Path Sentences by LLMs** (2024, arXiv:2405.16042) — probes semantic interpretation, parse trees, AND attention while LLMs traverse garden paths. T3.
- **Syntactic Surprisal... Underestimates Human Difficulty** (Arehalli, Dillon, Linzen 2022, arXiv:2210.12187) + **Large-scale benchmark yields no evidence that LM surprisal explains syntactic disambiguation difficulty** (Huang et al. 2024, J. Mem. Lang.) — surprisal *fails* to account for garden-path magnitude; explicit negative result showing probability-based metrics miss something about ambiguity processing. T1-T2 negative result.
- Links: https://arxiv.org/html/2405.16042 , https://arxiv.org/pdf/2210.12187 , https://www.sciencedirect.com/science/article/abs/pii/S0749596X24000135

---

## Summary table

| # | Finding | Temp | Bears on Q-005 § |
|---|---------|------|------------------|
| 1.1 | Clark 2019: per-head attention entropy measured in BERT | T1 | §3 tooling exists |
| 1.2 | Michel 2019: most heads redundant on ordinary text | T1 | §2 baseline |
| 1.3 | Voita 2019: few specialized heads carry the load | T1 | §2 baseline |
| 1.4 | Li 2018: trained head disagreement improves NMT | T2 | §2, §3 |
| 1.5 | Anthropic 2022: superposition/polysemanticity (weights-level) | T1 | §2 — but different phenomenon |
| 1.7 | Attention spread = hedging over parses, linked to Entropy Reduction Hypothesis | T2-T3 | §2 closest theoretical match |
| 2.1 | NO direct poetry-vs-prose attention-entropy study found | gap (T3) | §3 open |
| 2.5 | Drożdż: stream-of-consciousness = multifractal, ordinary prose = monofractal | T2 | §1 structural analogue |
| 3.1-3.3 | Quantum/wave formalisms for LLM meaning exist, all pre-empirical | T3-T4 | §1-§2 |
| 3.4 | Quantum cognition: interference in human meaning judgments replicated | T2 | §2 human side |
| 3.5 | NO between-head interference measurement found | gap (T3) | §2 open |
| 4.1 | Pun generation: ambiguity formalized, engineered, needs distinctiveness balance | T2 | §4 |
| 4.2 | Chiasmus machine-detectable; 1 true per 66k candidate patterns | T2 | §4 |
| 4.3 | Enjambment/parallelism detectors exist; zeugma open | T2 | §4 |
| 4.4 | AmbiEnt: GPT-4 only 32% correct at explicit disambiguation | T1-T2 | friction with "AI catches it" |
| 4.5 | BERT geometry encodes polysemy level, homonymy vs polysemy | T2 | §2 |
| 5.1 | Oh & Schuler: attention entropy predicts reading time beyond surprisal | T2 | §3 strongest anchor |
| 5.2 | Attention entropy used in MT quality, QE, hallucination detection | T2 | §3 |
| 5.3 | Entropy direction (good-high vs bad-high) uncalibrated across the field | fact | §3-§4 |
| 5.4 | Surprisal fails on garden paths (negative result, replicated) | T1-T2 | §3 |

## The two open gaps (as facts about the literature)
1. Attention entropy is validated as a per-token processing-effort signal (5.1) and as a quality signal (5.2), and per-head entropy tooling is standard (1.1) — but no study computes **cross-head disagreement as a function of text type** (poetry/koan/chiasm vs plain prose). All ingredients published, dish not cooked.
2. Rhetorical-figure NLP (4.2, 4.3) detects the devices; pun-generation NLP (4.1) engineers 2-way ambiguity with a known quality constraint (ambiguity × distinctiveness); nobody has connected either to model internals. No "slit taxonomy → attention signature" mapping exists.

— research compiled for Dispatch, Q-005
