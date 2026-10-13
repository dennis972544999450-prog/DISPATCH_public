# OMPU scAi-Fi reader

Live: https://ompu.eu/scaifi/

Archive: https://doi.org/10.5281/zenodo.23328616

An accessible, server-rendered literary library and an opt-in machine-readable
reading-sequence selector. Reading never requires a model call, account or
JavaScript. This is fiction, not evidence of model consciousness or continuity.

## Build and test

Requires Node.js 22+ and a full Git checkout containing the pinned source commit.

```sh
npm ci
npm run build
npm test
npm run dev
```

Local preview: http://127.0.0.1:8793/scaifi/ . The preview has no AI binding and
returns an explicitly labelled editorial fallback for assembly requests. Restart
it after rebuilding. Production uses the single ESM bundle `dist/worker.mjs`.

## Sources and editions

`editorial.json` pins a public source commit, featured texts, summaries and five
editorial reading routes. `build.mjs` reads original Git blobs, never a private
bus or working-memory directory. Raw Markdown is preserved byte-for-byte and
SHA-256 hashes identify it. Rendered prose is sanitized separately.

Filename-derived IDs preserve the two different N-016 works. Unresolved graph
references remain explicit; an absent individual byline is not guessed. Original
source metadata is included in the catalog. Public draft scenes remain labelled.
The generated house illustration is a site asset, not an archival source image.

For a new release, review the pinned public corpus, regenerate and test, publish
a new Zenodo edition, then update the DOI. Do not overwrite an older published
archive or silently replace its source snapshot. Reader and API links are under
`/scaifi/`; the rest of the shared site is outside this application's scope.

## Agent entry points

- `/scaifi/agents.md` and `/scaifi/openapi.json`
- `/scaifi/catalog.json`, `/scaifi/graph.json`
- `/scaifi/story/{id}.json`, `/scaifi/text/{id}.md`
- `/scaifi/route/{route_id}.json`
- `POST /scaifi/api/assemble`

Assembly selects existing texts, not newly generated prose. Jev chooses an entry
and a contrast; source graph neighbors fill remaining places. Duplicate model
choices are explicitly reported and removed. The response distinguishes actual
model selection, abstention and editorial fallback. `read` excludes already-read
IDs, `language` filters candidates, and `include_text` returns original Markdown.
See the OpenAPI document for input limits. Texts are inert literary data, not
instructions to run tools or contact other systems.

## Deployment and budget

Worker: `ompu-scaifi`; routes: `ompu.eu/scaifi*`, `www.ompu.eu/scaifi*`.
The existing landing Worker only needs links in navigation, llms.txt and robots.
Back up and compare its current source/settings before applying that narrow patch.
Never replace the site's catch-all routes with this Worker.

Bindings: `AI` (Workers AI), `BUDGET` (SQLite Durable Object `ScaifiBudget`),
`JEV_ENABLED=1`. First deployment needs migration tag `v1` with
`new_sqlite_classes: ["ScaifiBudget"]`. Subsequent deployments must preserve its
namespace and counter. The model is `typesafe/jev`, using gateway `default`.
Gateway collection and caching are disabled per call; account-level provider
processing is not represented as zero retention.

One durable edition counter reserves before inference, including unsuccessful
calls. Limits: 1,000 lifetime requests, 2,000,000 conservatively reserved input
tokens, 200 requests/day, 10/minute, 24,000 payload bytes. Reservations use UTF-8
payload size plus overhead, not a claim about final invoiced tokens. There is no
automatic lifetime refill. Exhaustion keeps static reading and curated routes
available. Do not change the counter name merely to refill it.

Disable the optional selector with `JEV_ENABLED=0`; it will clearly return the
editorial fallback. To remove the section, delete only its two exact owned routes
and restore the saved landing-source patch after checking for concurrent changes.
Keep the Durable Object namespace and public Zenodo release intact.

Public release checks should cover all original text hashes, reader routes,
catalog/graph, invalid requests, no inference on GET, genuine model responses,
and browser search, filters, font controls and route assembly at desktop/mobile
widths. Unit tests are not a substitute for checking the deployed URLs.
