# References

This folder is the evidence spine for Claude Blog Brain. It turns dated sources
into usable requirements without letting unsupported SEO or GEO claims leak into
deliverables.

## Evidence Spine Map

- `source-ledger.json` is the canonical source registry. It records source URL,
  source type, dates, retrieval metadata, confidence, evidence tier,
  methodology, limitations, supported claims, and raw snapshot status.
- `claim-ledger.md` is the adversarial claim register. It maps volatile claims
  to research questions, verdicts, confidence, primary source URL and date,
  second-source status, and refresh due dates.
- `CONFIDENCE_TAGS.md` defines how to classify official evidence, practitioner
  research, contested findings, and unsupported folklore.
- `canon/` holds stable source-led notes for recurring Google, schema, QRG,
  Core Web Vitals, AI Search, and policy claims.
- `current-requirements.md` summarizes the current operating requirements that
  are allowed to guide blog recommendations after ledger support exists.
- `market-research.md` summarizes buyer, market, and demand evidence with
  practitioner caveats where needed.
- `adapter-manifest.json` records adapter maturity truth. It remains
  generic-only until implementation and test gates are release-verified.

## No Source In Prose Only

Do not add a source only to Markdown prose. Release-counted evidence must be in
`source-ledger.json` first, then summarized in the relevant note. If a working
claim needs a source that is not yet in `source-ledger.json`, mark it as a
`source-ledger gap` in `claim-ledger.md` and do not use it as release-satisfying
evidence until the ledger is backfilled.

## Rules

- Do not reuse an official source URL for third-party impact, named-site, CTR,
  traffic, or AI citation claims.
- Do not promote a practitioner study to official evidence.
- Do not use a month-only or year-only date without `date_precision`.
- Do not quote dynamic datasets without data window, geography, platform or
  device filter, and retrieval date.
- Do not use deprecated tactics, including FAQ rich results, HowTo rich
  results, or FID, as current recommendations.
- Do not call the brain market-ready until local raw snapshots and hashes,
  external source URL and retrieval metadata, citations, adapter tests, and the
  release audit all pass.
