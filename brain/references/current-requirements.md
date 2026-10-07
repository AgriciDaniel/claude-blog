# Current Requirements

Status: research-reviewed. Evidence is captured in `references/source-ledger.json`.
Claim review: 2026-10-07. Historical study and event dates remain explicit;
source review does not establish market-ready release status.
Refresh due: 2026-11-07 for living Google documentation.

## Source Standard

Use official, primary, vendor, standards body, regulator, authority, or dated
practitioner sources. Every blog recommendation needs a source URL, retrieval
date, confidence tag, and rollback note when it changes a live content decision.

## Mid 2026 Requirements

Zero-click behavior is a planning constraint, not a guaranteed outcome.
Source: SparkToro, 2026-06-08, retrieved 2026-10-07.
Claim: US Google zero-click searches reached 68.01% for January through April
2026 in SparkToro's Similarweb desktop and mobile web panel. This estimates
weighted panel behavior, not all Google searches or native-app use.
Confidence: medium. Evidence tier: PRACTITIONER.
Operational rule: report expected visibility, impressions, and citation
exposure alongside click goals.

AI Overview click behavior is mixed and must be measured by citation status.
Sources: Seer Interactive, 2026-04-24; Pew Research Center, 2025-07-22; Ahrefs,
2026-02-04; retrieved 2026-10-07.
Claim: Seer reported AIO-present organic CTR rebounded from about 1.3% in
December 2025 to about 2.4% in February 2026. In its informational-query
cohort, citation was associated with about 120% more organic clicks per
impression than no citation. The 53-brand study used actual data through
February 2026 and projected March values; it does not establish causation.
Pew and Ahrefs support the broader direction that AI summaries can reduce
clicking, but their measurements differ.
Confidence: medium. Evidence tier: CONTESTED for a universal CTR effect,
PRACTITIONER for individual vendor benchmarks.
Operational rule: optimize for citation eligibility and reader value, but use
client GSC data when available before forecasting traffic impact.

AI Mode is strategically important but still needs query-share caveats.
Sources: Google I/O Search update, 2026-05-19, and SparkToro, 2026-06-08,
retrieved 2026-10-07.
Claim: Google reported AI Mode surpassed 1B monthly users at I/O in May 2026.
This is a dated, self-reported product-reach milestone, not query share.
SparkToro reported AI Mode at about 0.34% of US Google searches in its January
through April 2026 Similarweb desktop and mobile web panel.
Confidence: high for the Google user-count claim, medium for the SparkToro
behavior-share claim. Evidence tier: EVIDENCE-BASED for Google, PRACTITIONER
for SparkToro.
Operational rule: treat AI Mode as a distinct citation surface, but do not
over-weight it against standard Google organic and AI Overview work.

FAQ rich results are retired for Google Search.
Source: Google Search Central documentation updates, effective 2026-05-07 and
removal noted 2026-06-15, retrieved 2026-10-07.
Claim: FAQ rich results no longer show for any site. Google removed the old FAQ
rich result documentation on June 15. The cited changelog does not establish
every related testing-tool or reporting removal.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: do not sell FAQPage as a rich result tactic. For blogs,
prioritize Article or BlogPosting, Person, Organization, BreadcrumbList, and
visible Q and A content when it helps readers.

Article schema is the priority schema family for blog posts after FAQ and HowTo
visibility loss.
Sources: Google structured data introduction and Search Gallery, retrieved
2026-10-07.
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
2026-10-07.
Claim: Google added `Product.category` guidance for merchant listing structured
data and added sale-duration guidance for `validFrom`, `validThrough`, and
`priceValidUntil`.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: ecommerce or product-review blog work must distinguish Product
snippets from merchant listings, include category data only when relevant, and
model sale price dates explicitly when sale pricing is present.

The full Search Quality Rater Guidelines were reviewed on 2026-10-07.
Source: Search Quality Rater Guidelines PDF, 2025-09-11, retrieved 2026-10-07.
Claim: the current fetched full QRG is the 182-page September 11, 2025
revision. It defines Page Quality and Needs Met evaluation. The separate
36-page overview is dated November 2023. Rater guidance is not a direct
ranking input, and the PDF alone does not establish a claim that rating
guidance was unchanged.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: keep E-E-A-T, YMYL, low-value AI content, reputation, and
trust checks current.

Self-contained answers are an attributed editorial heuristic.
Source: `ziptie-aio-source-selection`, published 2026-03-25, updated
2026-09-15, retrieved and reviewed 2026-10-07.
Claim: ZipTie recommends answer-first, self-contained sections with clear
headings as an editorial heuristic for AI citation readiness. This is the
author's recommendation, without validated causal uplift, Google endorsement,
a fixed word count, entity-density target, or schema-based citation mechanism.
Confidence: medium. Evidence tier: PRACTITIONER.
Operational rule: use self-contained passages where they help readers. Keep
source context close to claims for traceability; do not describe proximity
as an established ranking or citation-selection rule.

Google says generative AI optimization is SEO, not a separate file or markup
game.
Sources: `g-ai-opt-guide` page last updated 2026-07-10, retrieved 2026-10-07;
`g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` changelog
event 2026-06-15, retrieved 2026-10-07.
Claim: Google Search does not use `llms.txt` for Search, AI Overviews, or AI
Mode. Google says no special AI schema, Markdown conversion, chunking file, or
AI rewrite layer is required for its generative AI Search features.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: do not recommend `llms.txt` as a Google visibility tactic. It
can exist for other LLM consumers only with that caveat.

Current Google update memory is refreshed through 2026-10-07.
Sources: Google Search documentation updates RSS, Search Status incident feed,
and `data/google-updates.json`, reviewed 2026-10-07.
Claim: the latest confirmed ranking event is the September 2026 spam update,
which began September 24 and applies globally and to all languages. The
October 1 generative AI content guidance reinforces review for accuracy,
quality, relevance, and added user value. September documentation also added
regional Search experience guidance and VideoObject creator and interaction
properties.
Confidence: high for official documentation updates. Evidence tier:
EVIDENCE-BASED.
Operational rule: event timing never proves site impact. Keep product and
documentation changes separate from ranking factors, preserve regional scope,
and verify structured data against the current Google property tables.

Generative-AI report availability and logging require separate checks.
Sources: `g-genai-reports`, published 2026-06-03, updated 2026-08-31;
`gsc-reporting-anomalies-2026-08-13`, reviewed 2026-10-07.
Claim: Google's August 31 update says the insights rolled out to all websites
worldwide, following the initial June subset. Google also says August 13-17
missing generative-AI impression data was restored on August 21. The separate
August 13 Discover logging incident does not prove traffic loss.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: distinguish report rollout, property access, logging
anomalies, and observed client performance before interpreting a change.

Site-reputation enforcement has a searcher-region boundary.
Sources: `g-spam-policies` and `g-site-reputation-eea-2026-08-28`, reviewed
2026-10-07.
Claim: from August 30, site-reputation manual actions affect results for users
outside the EEA. For users inside the EEA that manual-action impact does not
apply, while affected sections may be separated to rank independently.
Confidence: high. Evidence tier: EVIDENCE-BASED.
Operational rule: retain the policy and searcher-region distinction; a site's
headquarters does not decide the searcher's enforcement scope.

CrUX and soft-navigation measurements require explicit collection scope.
Sources: `chrome-crux-history`, `chrome-soft-nav`, and `chrome-softnav-final`,
reviewed 2026-10-07.
Claim: CrUX History's detailed weekly section documents a default 25 periods,
a maximum 40, and overlapping rolling 28-day windows. Its older introduction
still says six months. Chrome's final origin trial covered versions 147-149;
the current soft-navigation documentation says enabled by default in Chrome
151. The historical trial article alone does not establish current coverage.
Confidence: high for documented behavior; qualified for the CrUX prose conflict.
Operational rule: specify collectionPeriodCount, browser version, and tool
support. Do not treat overlapping periods as independent monthly samples.
