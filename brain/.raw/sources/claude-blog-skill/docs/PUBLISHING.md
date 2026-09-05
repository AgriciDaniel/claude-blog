# Publishing Workflow: Private to Public

This skill ships from two repos:

| Repo | Role | Visibility | Audience |
|---|---|---|---|
| `AI-Marketing-Hub/claude-blog` (origin) | Working repo. All in-development changes land here first. | Private | AI Marketing Hub Pro community + maintainers |
| `AgriciDaniel/claude-blog` (public-mirror) | Release mirror. Receives reviewed, approved versions of work. | Public | Open-source community, no membership required |

The two repos share git history. The private mirror runs ahead of public; public catches up on approved releases.

---

## Standard release flow

1. **Work in `origin`** (the private repo, `AI-Marketing-Hub/claude-blog`).
   - Make changes locally on `main` or feature branches.
   - Push to `origin` freely. Iteration here is cheap and not visible to non-members.

2. **Run the v1.9.0 Blog Delivery Contract** end-to-end on any draft destined for the public mirror. The contract enforces:
   - All 5 gates pass (`scripts/blog_preflight.py --strict`).
   - `blog-reviewer` agent returns `BLOCKING: false`.
   - Score >= 90 and zero P0 issues.

3. **Pre-release sanity check** (run locally before pushing to public):

   ```bash
   python3 -m pytest tests/                        # all 242 tests pass
   python3 scripts/lint_prose.py --root .          # zero prose-hygiene violations
   claude plugin validate .                        # marketplace manifest valid
   ```

4. **Version + CHANGELOG**:
   - Bump version coherently across all 14 surfaces. `tests/test_version_coherence.py` enforces this.
     - `pyproject.toml`
     - `.claude-plugin/plugin.json`
     - `CITATION.cff` (also update `date-released`)
     - All 11 sub-skill `SKILL.md` files with `version:` frontmatter
   - Move the `## [Unreleased]` block in `CHANGELOG.md` to `## [X.Y.Z] - YYYY-MM-DD` and start a fresh empty Unreleased.

5. **Pro-community review** in the [AI Marketing Hub Pro Skool](https://www.skool.com/ai-marketing-hub-pro). Post the release notes and collect feedback. This is the "approval gate" before the public push.

6. **Push to public** (only after explicit approval):

   ```bash
   git push public-mirror main
   git push public-mirror --tags         # if you cut a tag
   ```

   Tags are recommended for the public mirror so users can pin a release version. See "Tag and release" below.

7. **Post-release**:
   - Append a session note to `~/Documents/Obsidian Vault/sessions/` per global rule.
   - Update the public README if the dual-version callout needs adjusting (most edits don't).

---

## Tag and release

For the public mirror to show a clean release on the GitHub Releases tab:

```bash
# 1. Tag the commit (annotated tag with release notes)
git tag -a vX.Y.Z -m "Release vX.Y.Z: <one-line summary>"

# 2. Push the tag to BOTH remotes
git push origin vX.Y.Z          # private
git push public-mirror vX.Y.Z   # public

# 3. Create the GitHub release on the public mirror only
gh release create vX.Y.Z \
  --repo AgriciDaniel/claude-blog \
  --title "vX.Y.Z" \
  --notes-file <(awk '/^## \[X.Y.Z\]/,/^## \[/' CHANGELOG.md | head -n -1)
```

The private mirror does not need a corresponding GitHub release; community members consume via git pull. Tagging both keeps `git describe` and `git checkout vX.Y.Z` consistent across mirrors.

---

## Remote configuration (one-time)

Anyone cloning this repo for development should set up both remotes:

```bash
# If you cloned from the private mirror:
git remote -v
# origin    https://github.com/AI-Marketing-Hub/claude-blog.git (fetch)
# origin    https://github.com/AI-Marketing-Hub/claude-blog.git (push)

# Add the public mirror as a second remote:
git remote add public-mirror https://github.com/AgriciDaniel/claude-blog.git
git remote -v
# origin          https://github.com/AI-Marketing-Hub/claude-blog.git (fetch)
# origin          https://github.com/AI-Marketing-Hub/claude-blog.git (push)
# public-mirror   https://github.com/AgriciDaniel/claude-blog.git (fetch)
# public-mirror   https://github.com/AgriciDaniel/claude-blog.git (push)
```

`git push` (no args) defaults to `origin` (the private repo). Pushing to public requires the explicit `git push public-mirror main` command, which is the approval gate by construction.

---

## When the public mirror is ahead of private

This shouldn't happen normally, but if a hotfix lands on the public mirror first (e.g., a critical security patch contributed by an open-source user), pull it into the private repo:

```bash
git fetch public-mirror main
git merge public-mirror/main
git push origin main
```

Resolve any conflicts before pushing. Tag the merged state on both mirrors with the next patch version.

---

## What does NOT need to sync

Some artifacts are intentionally local-only and should not be pushed to either remote:

- `audit-results.md` (per-audit session evidence, already in `.gitignore`)
- `~/Desktop/claude-blog-audit-YYYY-MM-DD/` proof folders (live outside the repo)
- `.env*` and `BRAND.md` / `VOICE.md` / `DISCOURSE.md` at the repo root (user-specific context)

The `.gitignore` already excludes these.

---

## What this workflow is NOT

- Not an automated mirror. Public pushes are manual and gated on approval.
- Not a fork relationship at the GitHub metadata level. The two repos share history but neither is registered as a fork of the other (which would require a destructive re-creation).
- Not a substitute for branch protection. If you want PR-only merges to `main`, configure branch protection on the private repo via GitHub Settings.

---

## Quick reference card

```
origin            -> AI-Marketing-Hub/claude-blog (private, working repo)
public-mirror     -> AgriciDaniel/claude-blog     (public, release mirror)

git push origin main                    # publish to private (frequent)
git push public-mirror main             # publish to public  (release gate)
git push --tags public-mirror           # publish tags to public
```

Standing rule: never push to `public-mirror` without explicit approval from the maintainer + a clean Blog Delivery Contract pass.
