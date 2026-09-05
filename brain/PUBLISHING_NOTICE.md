# Publishing notice

## Rights boundary

The Brain contains original operating guidance, source metadata, and private
working evidence. A public website may expose only reviewed wiki content and
the public-facing notices expressly selected by the sanitizer. Source ownership
does not transfer merely because a URL or paraphrase appears in this repository.

## What can be public

- Reviewed Markdown under `wiki/`, after local-path and secret scanning.
- Public navigation assets generated from reviewed wiki links.
- The license, attribution, and third-party notices required for distribution.
- High-level methods that do not reproduce private source captures or internal
  review notes.

## What must stay private

- Everything under `.raw`, including captures, manifests, and ingestion history.
- `references/source-ledger.json`, `references/claim-ledger.md`, source-review
  decisions, and other source evidence used for internal verification.
- Local absolute build paths, credentials, account identifiers, customer data,
  unpublished drafts, and operator-only decision records.

The public projection is a separate sanitized artifact. Do not point a web
publisher directly at the Brain root. Run `site/scripts/sanitize-public.mjs`,
inspect its manifest, scan the resulting directory, and obtain the rights
holder's approval before publishing. The sanitizer is a safety control, not a
license grant or publication authorization.
