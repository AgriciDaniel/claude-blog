# Publishing Workflow

This guide is for maintainers publishing releases from the public
[`AgriciDaniel/claude-blog`](https://github.com/AgriciDaniel/claude-blog)
repository. Contributors should open a pull request rather than pushing
directly to `main`.

## Standard Release Flow

1. Prepare the release on a feature branch.
2. Confirm that the version and dated changelog entry agree.
3. Run the complete local validation set:

   ```bash
   python3 -m pytest tests/ -q
   python3 scripts/lint_prose.py --root .
   python3 scripts/consistency_check.py --root .
   python3 scripts/validate_public_release.py --root .
   claude plugin validate .
   git diff --check
   ```

4. Open a pull request against `main` and wait for all CI checks to pass.
5. Review the final diff for generated files, dependency locks, installer
   hashes, canonical repository references, and release-version coherence.
6. Merge the reviewed commit without bypassing failed checks.
7. Create a signed annotated tag from the merged `main` commit.
8. Publish the GitHub release from that existing tag.

## Version And Changelog

Keep the release version coherent across the canonical version surfaces:

- `.claude-plugin/plugin.json`
- `pyproject.toml`
- `CITATION.cff`, including `date-released`
- `skills/blog/SKILL.md`
- Any sub-skill `metadata.version` values

Move completed changes from `## [Unreleased]` into a dated
`## [X.Y.Z] - YYYY-MM-DD` section. Release notes should describe user-visible
behavior, compatibility, dependency changes, security fixes, and known
limitations. Historical issue and pull-request links may remain when they help
users trace a fix.

## Tag And GitHub Release

Run these commands only after the release pull request is merged and `main` is
green:

```bash
git switch main
git pull --ff-only origin main
git tag -s vX.Y.Z -m "claude-blog vX.Y.Z"
git verify-tag vX.Y.Z
git push origin refs/tags/vX.Y.Z

gh release create vX.Y.Z \
  --repo AgriciDaniel/claude-blog \
  --verify-tag \
  --fail-on-no-commits \
  --generate-notes \
  --title "claude-blog vX.Y.Z"
```

`--verify-tag` prevents GitHub CLI from silently creating a different tag.
Never move or replace a published release tag. If a release needs correction,
publish a new patch version.

## Public Release Review

Before tagging, confirm:

- Installer commands, raw URLs, canonical repository metadata, and marketplace
  instructions point to the public project.
- Installer hashes match the committed installer files.
- No credentials, local paths, audit workspaces, unpublished customer
  information, or maintainer-only operational notes are tracked.
- Dependency requirements agree with their hash-pinned locks.
- The Google update ledger contains primary-source records only; unverified
  observations cannot affect scoring.
- Release notes describe AI citation scores as internal readiness heuristics,
  not calibrated probabilities or inclusion guarantees.

## Release Artifacts

The source tag and GitHub release are the canonical release artifacts. Keep
local audit output, temporary environments, generated screenshots, and
project-specific `BRAND.md`, `VOICE.md`, or `DISCOURSE.md` files out of the
release unless a documented workflow explicitly requires them.

If publishing fails after the tag is pushed but before the GitHub release is
created, investigate the failure before retrying. Do not retag a different
commit with the same version.
