# Current Requirements

Status: researched. Evidence is captured in `references/source-ledger.json`.
Last verified: 2026-07-10.
Refresh due: 2026-08-09.

## Source Standard

Use official, primary, vendor, standards body, regulator, authority, or dated
practitioner sources. Every blog recommendation needs a source URL, retrieval
date, confidence tag, and rollback note when it changes a live content decision.

## Mid 2026 Requirements

Zero-click behavior is a planning constraint, not a guaranteed outcome.
Source: SparkToro, 2026-06-08, retrieved 2026-07-09.
Claim: US Google zero-click searches reached 68.01% for January through April
2026 in SparkToro's Similarweb desktop and mobile web panel, with about 276
clicks to the open web per 1,000 searches.
Confidence: medium. Evidence tier: PRACTITIONER.
Operational rule: report expected visibility, impressions, and citation
exposure alongside click goals.

AI Overview click behavior is mixed and must be measured by citation status.
Sources: Seer Interactive, 2026-04-24; Pew Research Center, 2025-07-22; Ahrefs,
2026-02-04; retrieved 2026-07-09.
Claim: Seer reported AIO-present organic CTR rebounded from about 1.3% in
December 2025 to about 2.4% in February 2026 and that being cited in the AI
Overview produced about 120% more clicks per impression than not being cited.
Pew and Ahrefs support the broader direction that AI summaries can reduce
clicking, but their measurements differ.
Confidence: medium. Evidence tier: CONTESTED for a universal CTR effect,
PRACTITIONER for individual vendor benchmarks.
Operational rule: optimize for citation eligibility and reader value, but use
client GSC data when available before forecasting traffic impact.

AI Mode is strategically important but still needs query-share caveats.
Sources: Google I/O Search update, 2026-05-19, and SparkToro, 2026-06-08,
retrieved 2026-07-09.
Claim: Google reported AI Mode surpassed 1B monthly users at I/O 2026.
SparkToro reported AI Mode at about 0.34% of US Google searches in its January
through April 2026 Similarweb desktop and mobile web panel.
Confidence: high for the Google user-count claim, medium for the SparkToro
behavior-share claim. Evidence tier: EVIDENCE-BASED for Google, PRACTITIONER
for SparkToro.
Operational rule: treat AI Mode as a distinct citation surface, but do not
over-weight it against standard Google organic and AI Overview work.

FAQ rich results are retired for Google Search.
Source: Google Search Central documentation updates, effective 2026-05-07 and
removal noted 2026-06-15, retrieved 2026-07-09.
Claim: FAQ rich results no longer show for any site. Google removed the old FAQ
rich result documentation and is removing related Rich Results Test and Search
Console support.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: do not sell FAQPage as a rich result tactic. For blogs,
prioritize Article or BlogPosting, Person, Organization, BreadcrumbList, and
visible Q and A content when it helps readers.

Article schema is the priority schema family for blog posts after FAQ and HowTo
visibility loss.
Sources: Google structured data introduction and Search Gallery, retrieved
2026-07-09.
Claim: JSON-LD remains a supported structured data format, and supported rich
result types are defined by Google Search Central. The blog priority framing
comes from the brain substrate and must stay separate from Google's official
eligibility rules.
Confidence: high for Google schema rules, medium for blog priority framing.
Evidence tier: EVIDENCE-BASED for Google, PRACTITIONER for blog priority
framing.
Operational rule: generate a coherent entity graph, not isolated snippets.

Product structured data changed on 2026-07-07.
Source: Google Search Central documentation updates, 2026-07-07, retrieved
2026-07-09.
Claim: Google added `Product.category` guidance for merchant listing structured
data and added sale-duration guidance for `validFrom`, `validThrough`, and
`priceValidUntil`.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: ecommerce or product-review blog work must distinguish Product
snippets from merchant listings, include category data only when relevant, and
model sale price dates explicitly when sale pricing is present.

The Search Quality Rater Guidelines are the active vault reference as of
2026-07-09.
Source: Search Quality Rater Guidelines PDF, 2025-09-11, retrieved 2026-07-09.
Claim: the vault's verified QRG source is the 182-page 2025-09-11 version, which
includes AI Overview evaluation examples and says there was no change to rating
guidance.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: keep E-E-A-T, YMYL, low-value AI content, reputation, and
trust checks current.

Passage-level citability is a practitioner GEO lever, not a guarantee.
Sources: ZipTie source selection guidance, 2026-03-25, and Ahrefs AI search
studies listed in the source ledger, retrieved 2026-07-09.
Claim: self-contained answer passages are a practical unit for AI citation
readiness. The substrate recommends concise summaries under headings, entity
clarity, visible source attribution, and first-hand experience signals.
Confidence: medium. Evidence tier: PRACTITIONER.
Operational rule: priority sections should include self-contained answer
passages where useful, with source context close to the claim.

Google says generative AI optimization is SEO, not a separate file or markup
game.
Sources: `g-ai-opt-guide` page last updated 2026-06-29, retrieved 2026-07-10;
`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` changelog
event 2026-06-15, retrieved 2026-07-10.
Claim: Google Search does not use `llms.txt` for Search, AI Overviews, or AI
Mode. Google says no special AI schema, Markdown conversion, chunking file, or
AI rewrite layer is required for its generative AI Search features.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: do not recommend `llms.txt` as a Google visibility tactic. It
can exist for other LLM consumers only with that caveat.

Current Google update memory is refreshed through 2026-07-09.
Source: Google Search Central documentation updates and
`references/source-ledger.json`, last verified 2026-07-09.
Claim: the verified requirements now include the 2026-07-07 Product
structured-data documentation updates. No Google-owned ranking, spam, QRG, or AI
search update was added in this remediation pass after the 2026-06-24 June spam
update entry.
Confidence: high for official documentation updates. Evidence tier:
EVIDENCE-BASED.
Operational rule: keep third-party July 2026 volatility reports quarantined
until a Google-owned source confirms a ranking or spam update.
