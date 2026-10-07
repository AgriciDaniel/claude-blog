# Claude Blog Brain Operator Kit

## Five-Minute Path

```bash
python -m pip install -e .
claude-blog-brain demo
claude-blog-brain lint --vault examples/sample-vault
claude-blog-brain report --vault examples/sample-vault --html-only
```

Open `examples/sample-vault/` in Obsidian and read:

1. `CODEX.md`
2. `wiki/hot.md`
3. `wiki/index.md`
4. `wiki/meta/dashboard.md`

## Client Vault

```bash
claude-blog-brain new acme --client-name "Acme Co" --owner "Daniel Agrici" --out-dir ~/claude-blog-brain-vaults
claude-blog-brain ingest --vault ~/claude-blog-brain-vaults/acme --file tests/fixtures/sample-source.md
claude-blog-brain synthesize --vault ~/claude-blog-brain-vaults/acme
claude-blog-brain report --vault ~/claude-blog-brain-vaults/acme --html-only
```

## Research Rule

Refresh official or primary sources when their review windows expire or a
material claim changes. The local 2026-10-07 readiness audit passes at 98/100;
that result does not survive source expiry or later changes automatically.

Research evidence must be written into `references/source-ledger.json` with
source URL, source type, published or last-updated date, retrieved date, date
precision, refresh due date, confidence, evidence tier, limitations, and claim
coverage. Markdown research notes alone do not satisfy market-ready release.
Active records require a dated claim review, excerpt, rationale and normalized
content hash. Retired and unverified records cannot support current advice.
The offline ledger check validates review records, not the availability of
external captured files; retain and hash-check the separate source evidence
pack. See `references/source-map.md` for lifecycle and capture conventions.

## Adapter Rule

Domain-adapted status requires `references/adapter-manifest.json` to name real
schemas, importer paths, synthesis modules, report renderers, fixtures, and
tests. Generic scaffold scripts are intentionally capped below market-ready.
