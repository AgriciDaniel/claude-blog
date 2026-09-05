# Release Checklist

## Product

- [ ] README states buyer, promise, outputs, boundaries, and quick start.
- [ ] `SKILL.md` maps commands accurately.
- [ ] License and distribution stance is explicit.
- [ ] Third-party notices are current.

## Research

- [ ] Maturity is documented and not overstated.
- [ ] `references/current-requirements.md` has dated official/primary sources.
- [ ] `references/source-ledger.json` lists dated official/primary sources,
      refresh dates, source types, and supported claims.
- [ ] `references/source-map.md` explains import strategy and source schemas.
- [ ] `references/safety-gates.md` lists refusal rules and failure paths.
- [ ] Stale source claims were browsed and refreshed before release.

## Vault

- [ ] Template vault opens in Obsidian.
- [ ] Hot/Index/Wiki notes and hubs are connected.
- [ ] Raw sources stay immutable under `.raw/`.
- [ ] Deliverables cite source notes or raw-file hashes.

## Verification

- [ ] Read-only: `python -m compileall scripts claude_blog_brain tests`
- [ ] Read-only: `python tests/test_pipeline.py --skip-release`
- [ ] Read-only: `python scripts/lint_vault.py`
- [ ] Read-only: `python scripts/audit_brain.py --json`
- [ ] Mutating fixture regeneration: `python scripts/build_demo_vault.py`
- [ ] Mutating release artifact build: `python scripts/package_release.py --version 0.2.0`
- [ ] No secrets, private client data, or local absolute paths in artifacts.
- [ ] Market-ready release is blocked unless audit score is at least 90 with no critical failures.
- [ ] `references/adapter-manifest.json` names real schemas, importer paths,
      synthesis modules, report renderers, fixtures, and tests before
      domain-adapted or market-ready release.
- [ ] Cross-document consistency check passes across `README.md`,
      `docs/PRODUCT_BOUNDARIES.md`, `references/product-spec.md`,
      `references/adapter-plan.md`, `references/adapter-manifest.json`,
      `references/source-ledger.json`, and the raw-source manifest.
