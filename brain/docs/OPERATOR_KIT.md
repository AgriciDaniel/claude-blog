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

Refresh current official or primary sources before turning this scaffold into a
domain-specific release. If the sources are not refreshed, keep the product in
generic scaffold status.

Research evidence must be written into `references/source-ledger.json` with
source URL, source type, published or last-updated date, retrieved date, date
precision, refresh due date, confidence, evidence tier, limitations, and claim
coverage. Markdown research notes alone do not satisfy market-ready release.

## Adapter Rule

Domain-adapted status requires `references/adapter-manifest.json` to name real
schemas, importer paths, synthesis modules, report renderers, fixtures, and
tests. Generic scaffold scripts are intentionally capped below market-ready.
