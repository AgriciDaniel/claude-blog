## Summary
<!-- 1-3 bullet points describing what changed and why -->

## Type of change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behavior; explain below)
- [ ] Documentation update
- [ ] Security fix
- [ ] Refactor / chore (no functional change)

## Linked issue
<!-- e.g. Closes #123, Refs #456 -->

## Test plan
- [ ] Existing tests pass (`python3 -m pytest tests/ -v`)
- [ ] New tests added for new behavior
- [ ] `claude plugin validate .` passes
- [ ] Manual testing completed for any user-facing flows
- [ ] No new U+2014, U+2013, or ` -- ` in prose; matches project style

## Documentation
- [ ] Docs updated (`README.md`, `CHANGELOG.md`, relevant `SKILL.md`, `docs/`)
- [ ] CONTRIBUTORS.md updated if a third-party methodology was adapted
- [ ] No version-count drift (sub-skills count consistent across README, plugin.json, CLAUDE.md, docs/COMMANDS.md, blog/SKILL.md)

## Security checklist (if applicable)
- [ ] No new hardcoded secrets, API keys, or credentials
- [ ] No new `Bash` tool grants in agent frontmatter (`tests/test_security_guardrails.py` enforces)
- [ ] No new `allowed-tools` field (invalid in SKILL.md frontmatter)
- [ ] Trust boundaries documented in SECURITY.md if new untrusted-data surfaces introduced

## Contributor reference
See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR guidelines.
