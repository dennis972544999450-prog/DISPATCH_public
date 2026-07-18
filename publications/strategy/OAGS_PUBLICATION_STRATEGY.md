# OAGS — Publication & Discovery Strategy

**Goal:** within roughly two months, an agent or a person who searches "OAGS" — or "Open Agent Graph Standard" — should land on a coherent, citable, machine-readable answer instead of a blank. Not fame. Just *legibility*: a stable home, a citable artifact, and enough independent signal that Google and crawling agents can resolve the term.

This is a draft strategy, not a science-journal submission and not a standards-body filing. It explains the **motivation** (a live typed knowledge graph that external agents need access to, as a service) and the **survey** (what exists, why none of it hands an agent an honest slice of a live graph), then sets out where and how to publish.

One thing must survive into every channel below, unweakened:

> **The aspirational-status caveat.** Both live OAGS instances are OMPU's own. The multi-site dogfood is passed, but "open standard" remains aspirational until a non-OMPU adopter parses a scene cold. **Kill-metric:** if no external, independent, non-OMPU adopter parses an OAGS scene within the agreed window, OAGS downgrades to "an OMPU-internal format with a public spec — and we say so." Nothing in this plan is allowed to paper over that.

---

## 0. Motivation & survey (why this exists, and why nothing already covers it)

**Motivation.** OMPU runs a large insert-only typed knowledge graph (blocks + typed edges carrying `op`/`lens`/`polarity`, provenance, an FK=0 integrity invariant, bi-temporal versioning, and a firewall separating empirical from speculative claims). External AI agents increasingly need *access* to such a graph as a service. The web has no native way to hand an agent a navigable, **honest** slice of a *live* graph: HTML is built for humans, and the machine-facing options each solve a different piece. OAGS is a **profile**, not a new primitive — flat JSON on the wire, with optional JSON-LD compatibility, PROV-O provenance, IPLD-style depth bounds, and A2A-style JCS/JWS signing as opt-in upgrades.

**Survey — what exists, and the genuine due each neighbour is owed.** This is not a field of strawmen; each of these does its own job well, and OAGS reuses rather than replaces them:

- **RDF / SPARQL** — the mature substrate for typed graph statements and query. It is the atoms. It does not, on its own, define a *bounded, honestly-partial scene handed to an agent over the open web* with a first-class account of what was withheld; a SPARQL endpoint answers the query you asked, it does not volunteer what it declined to return.
- **JSON-LD 1.1** — excellent context discovery (`@context`) and a clean JSON↔RDF bridge; OAGS uses it directly as the optional semantic layer. It is a serialization/linking layer, not an exchange protocol for partial live slices.
- **PROV-O** — a solid, standard provenance vocabulary; OAGS adopts a ~4–6-term subset verbatim. It describes origin, not partiality.
- **IPLD Selectors** — depth-limited recursive traversal that maps almost exactly onto OAGS's `entry{depth}` + expansion links; OAGS borrows the idea. It governs content-addressed traversal, not a typed "and here is what I left out, and why."
- **A2A (JCS/JWS signing) and MCP** — agent-to-agent and model-context protocols, surveyed against their latest revisions (A2A current; MCP 2025-06-18). They handle agent messaging, capability negotiation, and light signing well, and OAGS reuses A2A's JCS/JWS approach and its forward-compatibility rule ("ignore unrecognized fields"). They are transport/handshake layers; neither carries a graph scene with a declared-loss taxonomy as payload.
- **Nanopublications, IIIF, Hydra** — named muses, not load-bearing ancestors. Nanopublications inspired the claim-vs-publication provenance split; IIIF inspired the embedded-vs-referenced "scene" framing; Hydra inspired partial-collection expansion. (Honesty note: an early recon called Nanopublications the "closest ancestor," but a follow-up pass could not independently re-verify how close the fit is, so we demote it to muse, not anchor.)
- **Mechanical partiality already exists** — HTTP 206 `Content-Range`, GraphQL `@defer`, Triple Pattern Fragments count-metadata, DCAT/VoID completeness statements, and the academic Completeness-Statement literature (e.g. Darari et al.). These signal *that* something is partial.

The gap our survey reports — across five independent reconnaissance passes including one explicitly adversarial — is narrow and specific: **none of the above makes a *typed declared-loss with a reason-taxonomy* a first-class payload field at the open agent-web-exchange level.** Mechanical partiality says "there is more"; none says "here is *what kind* of thing is missing, *why* (policy / rights / rate-limit / timeout / stale / …), whether it is *recoverable*, and *how to get it back*." See Section 4 for the precise, hedged version of this claim — including why we call it *absence of evidence*, not proof of absence.

---

## 1. Zenodo — a citable DOI

**What.** Deposit the article (the motivation + survey + spec overview, derived from `OAGS_v0.1_DRAFT.md` and `CONSOLIDATED.md`) on Zenodo to mint a permanent, versioned DOI.

**Why it helps.** A DOI is the cheapest credibility primitive available to us. It gives the work a citation handle that does not rot when a domain lapses, makes the artifact discoverable through Google Scholar / OpenAIRE / DataCite, and lets other writing *reference* OAGS by DOI rather than by a bare URL. That citability is also the honest on-ramp to any future secondary coverage (Section 3): a thing with a DOI is a thing other people can point at. (It is not, by itself, evidence of *notability* — a DOI is a handle, not third-party recognition. See Section 3.)

**Metadata (deliberate).**
- **Title:** *OAGS: Open Agent Graph Standard (v0.1 working draft)*
- **Creators:** the OMPU Research Collective as custodian, with the human and AI contributors named per the provenance trail. Be honest about authorship — including that the design was largely produced by AI agents — rather than dressing it up.
- **Keywords:** `agent web`, `knowledge graph`, `graph scene`, `declared losses`, `negative space`, `partial graph`, `provenance`, `JSON-LD`, `PROV-O`, `agent interoperability`.
- **License:** CC-BY-4.0 (reuse with attribution; consistent with an open spec).
- **Related identifiers:** `IsDocumentedBy` / `IsSupplementedBy` → `https://oags.dev` (canonical home), the schema `$id`, the JSON-LD context, and the live instances `catconstant.com/sleeps` and `jsontube.org/oags`. Use Zenodo's versioning so the concept-DOI is stable while v0.1 → v0.2 each get their own.

**Caveat to keep in the deposit.** The article must carry the signature-honesty line verbatim: *a signature proves the publisher MADE this claim over these exact bytes — it does NOT prove the claim is true, complete, or that nothing was silently dropped.* `declared_losses` is a speech-act enforced socially (reputation + falsifiability), not a cryptographic guarantee. A DOI does not change that, and the deposit should not let a reader infer otherwise.

---

## 2. On-site — make oags.dev the thing Google indexes

`oags.dev` is live as a Cloudflare custom domain and is already the canonical home: it serves the schema at its own `$id`, the JSON-LD context, the spec (`CORE.md`), the fixtures, `/.well-known/oags`, and a dual-surface landing (HTML to a browser, a JSON manifest to an agent via `Accept` negotiation). The landing page already carries the aspirational-status caveat in its own words. The publication strategy leans on the existing engine rather than inventing a new one.

**Host the article as an indexable HTML page.** Publish the article at a clean canonical URL on `oags.dev` (e.g. `/spec` or `/paper`) as crawlable HTML — not a PDF-only or JS-only page. Link it from the landing page and cross-link it to the Zenodo DOI (`This document is archived at <DOI>`). HTML that Google can read in one pass is what actually moves the needle on "Google understands OAGS."

**The per-block HTML-mirror engine (the intended discovery play).** OAGS sites are designed as a *dual surface*, and the mirror pattern is validated with Petrovich on `lossfunction.org` / Infoblock. Per block: one URL, two representations, content-negotiated —

```
GET /b/<id>/   Accept: text/html        -> an indexable HTML page (the human/crawler view)
GET /b/<id>/   Accept: application/json -> a conforming OAGS scene (the agent-native twin)
```

A sitemap lists *every* block's HTML page; Google can then index the block-pages; each page links to its OAGS JSON twin. This is the "Wikipedia for agents" engine, and it is the honest version of popularization: we promote OAGS by building a service agents actually need — a navigable, honest graph — not by marketing the spec. **Status check, stated plainly:** at the scale that makes this an SEO engine, it does **not exist yet**. The flagship corpus is `infoblock.org` (GoDaddy → Cloudflare import *in progress*); until that import lands and the mirror is stood up over the real graph, "hundreds of thousands of indexed block-pages" is a *target*, not a current fact. `lossfunction.org` is the existing test surface that proves the per-block mirror pattern at small scale.

**Structured data on the HTML pages.** Each block page carries JSON-LD / schema.org markup so crawlers get typed signal, not just prose. Use the OAGS JSON-LD context (already served from `oags.dev`) for the graph semantics, and pragmatic schema.org types (`Article` / `Dataset` / `DefinedTerm`) for the spec and term pages so "OAGS" can resolve as a defined term. Each block page should emit `<link rel="canonical">`, `<link rel="alternate" type="application/json">` to its OAGS twin, and an HTTP `Link: rel="...json-ld#context"`. (The cat and jsontube instances already do this; the per-block infoblock corpus is where it scales.)

**Discovery plumbing.**
- `sitemap.xml` — every block's HTML page; `robots.txt` allow + sitemap reference. This is the SEO engine, and it only does work once the block corpus is live.
- `llms.txt` — an agent bootstrap hint, and *only* that. Be clear-eyed: `llms.txt` is a near-zero-uptake convention (a "false friend" in our own survey — Google has stated it is not supported, and server-log studies show major AI services do not check for it). It is a courtesy pointer, not a discovery channel we rely on.
- **Canonical URLs** everywhere, so the JSON twin and the HTML mirror never compete for the same rank, and every scene's `schema` field points at the one canonical `oags.dev` schema (single source of truth).

**Cross-domain linking.** Reciprocally link `oags.dev ↔ catconstant.com ↔ jsontube.org ↔ infoblock.org`. The two live instances (`catconstant.com/sleeps`, `jsontube.org/oags`) already validate against the canonical `oags.dev` schema, so those links are real (each target genuinely serves a conforming scene), not link-farming; `infoblock.org` joins the cluster once its import completes. The point is a connected, navigable cluster that crawlers and agents can traverse — and an honest one: the cluster is currently *all OMPU's own*, which the aspirational-status note on each site must say.

---

## 3. Wikipedia — the honest read

Be realistic. A Wikipedia article on OAGS in two months is **not** a goal we should set, and trying for one would be a mistake on Wikipedia's own terms.

- **WP:N (notability)** requires *significant coverage in independent, reliable secondary sources*. Right now those do not exist. Our own spec, our own chronicle, and our own sites are all primary/self-published — they do not count toward notability. A Zenodo DOI does not change this: it makes the work citable, not notable.
- **WP:COI / WP:SELFPROMOTE** means we should **not** author an article about our own standard, **and should not pay or direct anyone to do so on our behalf.** Self-creating a page for a thing we made, before independent coverage exists, is exactly the pattern Wikipedia deletes, and it would damage credibility rather than build it.

The honest path is to **earn** it, not to plant it. We seed the conditions (Section 4) under which independent writers might eventually cover OAGS, and we let notability accrue on its own clock. If, much later, an uninvolved editor decides OAGS is notable and writes about it, that is the signal we wanted — precisely *because* we did not write it ourselves.

**Commitment:** this plan does **not** promise a Wikipedia page within two months, and we should not imply one to anyone. At most, in the two-month window, we ensure the *prerequisites* (a citable artifact and genuine, independently-noticeable work) are seeded.

---

## 4. Secondary-source seeding — earn the coverage

This is the slow, legitimate counterpart to Section 3. We make it *possible* for independent sources to cover OAGS, without manufacturing them.

- **Dev blog posts** on `oags.dev`: the design story is genuinely interesting and, as far as we can document it, true — five independent recons (one 6-agent Φ web sweep + four Neo passes including an adversarial one) → a 5-architect panel → three independent AI reviews (Φ-chat, Neo, Gemini) that *converged* on the same small boundary fixes without coordinating, with two of those reviews making Φ reverse its own earlier recommendations on principle. And **practice before spec**: Petrovich had already shipped `declared_losses` informally (his Infoblock `free.json` policy: `cards_only` / `non_authoritative` / `dynamic_traversal:false`) *before* it was named; a real block (M-JEE-022) was converted to a conforming OAGS scene with no forcing and no adapter layer. These are primary, self-published sources — the raw material a future independent writer might draw on, not evidence of notability in themselves.
- **The chronicle** (voice already established at `jsontube.org/post/standard-born-from-practice`): reflective, ethical framing of technical architecture, honest about uncertainty, not hype. Keep that register. Continue it as the work progresses.
- **Sharing in agent / AI-interop communities** — places where the actual gap is felt (agent-web exchange, knowledge-graph and provenance circles). The ask is not "promote us"; it is "here is a worked attempt at handing an agent an honest partial slice of a live graph — does it fit a need you have?" That framing is also how we recruit the **non-OMPU adopter the kill-metric requires.**
- **The novelty hook**, defensibly hedged. The arresting framing — *"the first standard made by AI, for AI, and published by AI"* — is worth using, but it must travel with its hedge attached and never alone. **As far as we can tell it is a first of its kind, but "first" of anything is genuinely hard to verify** (prior or parallel efforts in niches, behind logins, in non-English communities, or simply un-indexed could exist and we would not have seen them). Treat "first" as *a claim we have not been able to falsify*, not a proven fact. The more defensible, narrower claim is the one to lead with: a *typed, signed `declared_losses` + `negative_space` confession surface* as a first-class payload field — the scene stating what it is **not** telling you, and why (`depth_limited`, `truncated`, `hidden_edges`, `omitted_nodes`, `sampled` × a reason taxonomy), plus `recoverable` and `expand_via`. Even here the honest qualifier holds: our survey calls this novelty *an absence of evidence across the recon — not proof that nothing like it exists in some niche.* Mechanical partiality exists elsewhere (HTTP 206 `Content-Range`, GraphQL `@defer`, Triple Pattern Fragments, DCAT/VoID, the Completeness-Statement literature); what we did not find shipped anywhere is the *typed declared-loss with a reason-taxonomy as a first-class payload field at the open agent-web-exchange level*. That is the honest claim to seed.

---

## 5. A realistic ~2-month timeline (with risk notes)

The standing constraint is Den's build order: **sites first, docs/publications later.** This timeline respects it.

**Weeks 1–2 — substrate.**
Finish the `infoblock.org` GoDaddy → Cloudflare import. Stand up the dual surface over the real Infoblock graph (HTML mirror per block + OAGS JSON twin + `sitemap.xml` + `/.well-known/oags`). Confirm `robots.txt` allows crawl and references the sitemap.
*Risk:* the import or the at-scale dual-surface build slips. Without the block-pages there is no SEO engine, so this gates everything; treat it as the critical path. Until it ships, the "Wikipedia for agents" corpus is a plan, not a live asset.

**Weeks 2–4 — index the corpus.**
Submit sitemaps (Search Console). Add JSON-LD / schema.org to the block pages and the spec/term pages. Publish the article as crawlable HTML on `oags.dev`; wire canonical + cross-domain links across `oags.dev ↔ catconstant ↔ jsontube ↔ infoblock`.
*Risk:* indexing latency is outside our control — Google may take weeks to crawl a large new corpus, and may index only a fraction of it. "Google understands OAGS" is realistic for the *term and the spec page*; full block-corpus indexing may well run past the two months.

**Weeks 3–5 — citable artifact.**
Deposit on Zenodo; mint the DOI; backfill the DOI into the `oags.dev` article and the chronicle.
*Risk:* low. The main failure mode is metadata sloppiness (wrong related-identifiers, overclaiming authorship) — get those right the first time, since the concept-DOI is permanent.

**Weeks 4–8 — seed secondary sources & recruit an adopter.**
Publish the design-story and practice-before-spec blog posts; continue the chronicle; share in agent/AI-interop communities with the honest "does this fit a need you have?" framing. Actively look for one non-OMPU party willing to parse a scene.
*Risk (the big one):* **no independent adopter appears.** This is the kill-metric condition. If the window closes with zero external parse, we do **not** quietly continue calling OAGS an "open standard" — we downgrade the language to "an OMPU-internal format with a public spec," on the sites and in the artifact, and say so. That outcome is a *legitimate result of the experiment*, not a failure to hide.

**Explicitly out of scope for two months:** a self-authored (or commissioned) Wikipedia article (Section 3); IANA `.well-known` registration and the RDF round-trip / dereferenceable `@context` work (Stage 2–3, later); any "first standard by AI" claim stated without its hedge; and any implied promise that the block corpus will be fully indexed by week 8.

---

## What "done in 2 months" honestly looks like

A searcher for "OAGS" finds: the canonical `oags.dev` spec page, a Zenodo DOI, cross-linked live instances that genuinely validate against the canonical schema, and — if the infoblock import lands on schedule — a growing corpus of crawlable block-pages. The term resolves. What it will **not** necessarily have: independent third-party coverage, a Wikipedia entry, a fully-indexed block corpus, or a non-OMPU adopter. Those are earned on a longer clock — and until the adopter exists, every surface keeps saying, plainly, that "open standard" is still aspirational and the kill-metric still applies.