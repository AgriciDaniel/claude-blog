# Publishing notice

## Rights boundary

The Brain contains original operating guidance, source metadata, and source
evidence. The repository is public and the Brain is MIT licensed, but a public
website may expose only reviewed wiki content and the public-facing notices
expressly selected by the sanitizer. Source ownership does not transfer merely
because a URL or paraphrase appears in this repository.

## What can be on the public website

- Reviewed Markdown under `wiki/`, after local-path and secret scanning.
- Public navigation assets generated from reviewed wiki links.
- The license, attribution, and third-party notices required for distribution.
- High-level methods that do not reproduce source captures or internal review
  notes.

## What stays out of the public website

These files are tracked in the repository as public evidence, so anyone can
audit them there. They must stay out of the website projection the sanitizer
builds:

- Everything under `.raw`, including captures, manifests, and ingestion history.
- `references/source-ledger.json`, `references/claim-ledger.md`, source-review
  decisions, and other source evidence used for verification.

## What never goes into the repository

- Credentials, tokens, and other secrets.
- Customer data, account identifiers, unpublished drafts, operator-only
  decision records, and local absolute build paths.

The public projection is a separate sanitized artifact. Do not point a web
publisher directly at the Brain root. Run `site/scripts/sanitize-public.mjs`,
inspect its manifest, scan the resulting directory, and obtain the rights
holder's approval before publishing. The sanitizer is a safety control, not a
license grant or publication authorization.
