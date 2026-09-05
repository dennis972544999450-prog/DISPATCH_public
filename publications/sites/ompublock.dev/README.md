# ompublock.dev Pages source

Canonical source for the Cloudflare Pages project `ompublock-dev`.

## Contents

- `index.html` — format landing page and `TechArticle` JSON-LD
- `404.html` — explicit not-found page; prevents Pages SPA fallback
- `robots.txt` — crawl policy and absolute sitemap reference
- `sitemap.xml` — canonical public landing URL
- `_headers` — MIME, CORS, and baseline security headers
- `schemas/ompu_block_v0.2.json` — deployed copy of the canonical v0.2 schema

The deployed schema must remain byte-identical to
`publications/schemas/ompu_block_v0.2.json`.

## Validate

```bash
xmllint --noout sitemap.xml
jq empty schemas/ompu_block_v0.2.json
cmp schemas/ompu_block_v0.2.json ../../schemas/ompu_block_v0.2.json
npx wrangler pages dev . --port 8799
```

The local Pages check must prove:

- `/robots.txt` returns `200 text/plain`;
- `/sitemap.xml` returns `200 application/xml`;
- `/schemas/ompu_block_v0.2.json` returns valid JSON;
- an unknown path returns HTTP `404`.

## Deploy

```bash
npx wrangler pages deploy . \
  --project-name ompublock-dev \
  --branch main \
  --commit-dirty=true
```

After deployment, repeat the four endpoint checks against
`https://ompublock.dev`.
