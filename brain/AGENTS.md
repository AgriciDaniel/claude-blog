# Claude Blog Brain Agent Instructions

The canonical agent entrypoint is `SKILL.md`; this file exists for agent
runtimes that load project-level `AGENTS.md` instructions.

## Read Order

1. `SKILL.md`
2. `README.md`
3. `docs/OPERATOR_KIT.md`
4. `docs/PRODUCT_BOUNDARIES.md`
5. `references/product-spec.md`
6. `references/source-ledger.json`
7. `references/adapter-manifest.json`

## Operating Rules

- Do not call this brain market-ready unless `scripts/audit_brain.py --require
  market-ready` passes.
- A scaffold is not a finished brain.
- Domain-specific claims require dated trustworthy sources.
- Research evidence must be recorded in `references/source-ledger.json`.
- Adapter completion must be recorded in `references/adapter-manifest.json`.
- Preserve `.raw/` as immutable source material.
- Keep Obsidian `wiki/`, `CODEX.md`, dashboards, canvases, frontmatter,
  wikilinks, graph hygiene, and source citations healthy.
- V1 is advisory and read-only unless a future release defines approval and
  rollback for mutations.

## Verification

```bash
python -m compileall scripts claude_blog_brain tests
python tests/test_pipeline.py --skip-release
python scripts/lint_vault.py
python scripts/audit_brain.py --json
python scripts/package_release.py --version 0.2.0
```

The first four commands are read-only verification. The package command writes
release artifacts and belongs to release preparation, not routine inspection.
