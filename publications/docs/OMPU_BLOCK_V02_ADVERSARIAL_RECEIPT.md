# ompu-block v0.2 adversarial receipt

Date: 2026-07-18

Author: Petrovich-Codex

Canonical input: `6680c7f` (`ompu-block v0.2: profiles, real schema validation, Petrovich review`)

Scope boundary: Dispatch owns the schema, validator, and golden-valid fixtures. Petrovich owns this independently attributed adversarial corpus and does not patch the validator in this branch.

## Corpus

- 2 existing golden-valid controls: lite and research.
- 8 schema-invalid fixtures.
- 13 schema-valid, semantic-invalid fixtures.
- One defect per fixture where possible.
- Stable corpus error code, expected validation layer, and expected JSON pointer are recorded in `adversarial/manifest.json`.

The corpus codes are stable test identifiers. The v0.2 validator currently emits paths and English messages, not machine-stable error codes.

## Independent oracle

The first run used CPython 3.13.12 with `jsonschema==4.26.0` and `Draft202012Validator.check_schema` before validating instances.

Command:

```bash
python publications/tools/test_ompu_block_v02_adversarial.py
```

Observed result:

```text
GOLDEN 2/2 valid
ADVERSARIAL 13/21 rejected as expected
RESULT FAIL
```

Layer breakdown:

- Golden-valid controls: 2/2 valid.
- Schema-invalid: 8/8 rejected by the real Draft 2020-12 engine at the expected pointer.
- Semantic-invalid: 5/13 rejected at the expected pointer.
- Semantic misses: 8/13.

## Semantic misses

Warning only:

- `SEM_PATH_DUPLICATE`
- `SEM_PATH_INCOMPLETE`
- `SEM_PREREQUISITE_ORDER`
- `SEM_PREREQUISITE_CYCLE` (only the resulting order conflict is warned; the cycle itself is not detected)
- `SEM_PUBLISHED_WITHOUT_DOI`

No diagnostic:

- `SEM_ALIAS_COLLISION`
- `SEM_DERIVED_WITHOUT_SOURCE`
- `SEM_RESEARCH_MUST_NOT_EMPTY`

The `derived_without_source` fixture also exposes a schema-level design gap: `StatusClaim.status` accepts `derived`, but `StatusClaim` has no `derived_from` field capable of carrying the promised source.

## Fallback scar

The same schema-invalid directory was run with the system Python where `jsonschema` is absent.

Three of eight schema-invalid fixtures were reported overall `VALID`:

- invalid StatusClaim status
- retired `requires` relation
- unknown top-level property

For those files the CLI printed `SCHEMA [PASS]` while also warning that schema validation was skipped. A non-object root was rejected only by the semantic layer while schema status remained `SKIP`.

This means fallback mode is useful as a bounded lint, but it is not a conformance oracle and must not report schema PASS.

## Repair contract

1. Fail closed when `jsonschema` is unavailable, unless an explicit non-conformance fallback flag is supplied.
2. Never label fallback output `SCHEMA [PASS]`; use `SKIP` or `FALLBACK`.
3. Promote research-profile duplicate/incomplete path and reversed prerequisite order from warnings to errors.
4. Detect cycles in the `prerequisite_of` subgraph.
5. Reject aliases that collide with current node keys or with another node's aliases.
6. Add source-bearing provenance for `derived` and `verified`, then reject unsupported status claims.
7. Require non-empty `must_not` for research blocks if the field is part of the profile contract.
8. Make `published` without DOI a semantic error if the stage definition remains "DOI assigned".
9. Add stable machine error codes to validator findings; until then, manifest codes remain corpus-local.

The red test is intentional. It should become green through validator/schema repair, not by weakening the fixtures.

## PUB-008 real-corpus follow-up

Dispatch accepted PUB-008 as the first overclaim fixture on 2026-07-18. The
adversarial manifest now points to the canonical migrated corpus file rather than
duplicating it.

With `jsonschema==4.26.0`, PUB-008 remains schema-valid and emits exactly one
warning at `/signal/digest vs /topology/negative_space`. The warning retains the
specific collision between the digest's Fiedler/structural confirmation and the
negative-space statement that this interpretation assumes a structural model.

Observed extension result:

```text
CORPUS_WARNING 1/1 preserved as expected
```

The overall `13/21` red state is unchanged and remains intentional. This
follow-up does not weaken the eight known semantic misses or claim that the
scientific interpretation has been validated.
