# Confidence Tags

Use two separate fields in `references/source-ledger.json` and cite the same
semantics in notes:

- `confidence`: `high`, `medium`, or `low`.
- `evidence_tier`: `EVIDENCE-BASED`, `PRACTITIONER`, `CONTESTED`, or
  `FOLKLORE`.

## Confidence

`high` means the source directly supports the exact claim, has a clear date,
and is official, primary, standards-based, regulator-authored, first-party
product/API documentation, or first-party property data for the fact being
cited.

`medium` means the source is useful but directional, such as practitioner SEO
research, vendor market analysis, dynamic datasets, or a single non-official
study with methodology limits.

`low` means the claim is weakly supported, stale, indirect, disputed, missing
methodology, or safe only as a hypothesis for further verification.

## Evidence Tier

`EVIDENCE-BASED` is for official Google documentation, standards bodies,
regulators, first-party API docs, first-party property data, primary controlled
datasets, and source-owned product facts.

Examples:

- Google Search Central says `llms.txt` is not needed for Google Search.
- web.dev says INP is a stable Core Web Vital.
- A client's own GSC export shows AI Overview impressions for that property.

`PRACTITIONER` is for SEO/GEO studies, vendor benchmarks, market reports,
observational studies, and expert guidance. These can inform operations but
must not be presented as guaranteed platform behavior.

Examples:

- SparkToro zero-click estimates from a Similarweb panel.
- Seer AI Overview CTR benchmarks.
- Ahrefs, Semrush, seoClarity, SE Ranking, Similarweb, or ZipTie studies.

`CONTESTED` is for claims where credible sources disagree, the methodology is
unstable, or the observed effect varies materially by site, market, query class,
device, or time window.

Examples:

- A universal AI Overview CTR-loss percentage.
- A claim that AI Mode citations and AI Overview citations can be optimized as
  one surface.
- A vendor benchmark contradicted by first-party client data.

`FOLKLORE` is for unsupported ranking hacks, undocumented AI visibility
promises, copied industry assumptions, or tactics with no dated source.

Examples:

- "FAQPage schema improves Google AI extraction."
- "`llms.txt` improves Google AI Overview inclusion."
- "Adding hidden entity blocks guarantees citations."

## Downgrade Rules

- Official Google source used for a third-party impact claim: downgrade the
  impact claim to `PRACTITIONER` or `CONTESTED` and add the actual reporting
  source.
- Vendor study with no property-level data: cap confidence at `medium` and use
  `PRACTITIONER`.
- Single-source numeric benchmark: use `AS-REPORTED` or `SINGLE-SOURCE` in
  `claim-ledger.md`; cap confidence at `medium` unless it is official or
  first-party property data.
- Conflicting studies or unstable SERP behavior: use `CONTESTED`; keep the
  operational rule qualitative unless client data confirms it.
- Source does not prove the operational recommendation: downgrade to
  `FOLKLORE` or remove the recommendation.
- Dynamic dataset: record retrieval date, geography, device/platform filter,
  data window, and methodology before quoting a number.
- Stale living document: refresh before release or downgrade to `low`.

## Operating Rule

Official facts and practitioner analysis must be separate ledger entries or
separate claims with separate limitations. Never attach named-site impact,
traffic loss, CTR change, or AI citation claims to an official Google URL unless
Google itself documents that exact claim.
