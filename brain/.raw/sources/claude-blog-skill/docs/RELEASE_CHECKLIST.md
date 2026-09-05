# Release Checklist

Use this before publishing a claude-blog release.

## Versioning
- [ ] Version is coherent in `.claude-plugin/plugin.json`, `pyproject.toml`, `README.md`, and `CHANGELOG.md`.
- [ ] `CHANGELOG.md` has a dated section for the release.
- [ ] README install examples point at the intended repo and release ref.
- [ ] Installer hashes in README match the committed `install.sh` and `install.ps1`.

## Validation
- [ ] `python3 scripts/lint_prose.py` passes.
- [ ] `python3 -m pytest tests/ -q` passes when scripts or tests changed.
- [ ] `claude plugin validate .` passes on a machine with Claude Code installed.
- [ ] CI is green on the protected branch.

## Installer Smoke Test
- [ ] Unix installer works in a temporary `HOME`.
- [ ] Windows installer works in a temporary profile.
- [ ] Nested skill payloads are present after install, including FLOW prompt references and Google report templates.
- [ ] Unix uninstall removes only paths from the claude-blog manifest or package allowlist.
- [ ] Shared credentials under `~/.config/claude-seo` are not deleted by uninstall.

## Publishing
- [ ] Marketplace metadata points at the intended owner and repository.
- [ ] Release notes include security or audit remediation highlights.
- [ ] Create and push the release tag only after all checks pass.
