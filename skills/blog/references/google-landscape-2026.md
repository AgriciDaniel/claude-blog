# Google Search Landscape 2026

Verified against Google-owned sources on 2026-10-11. The machine-readable
source of truth is `data/google-updates.json`. This reference contains only
Google-confirmed events, documented product behavior, and explicit operational
inferences. It intentionally excludes unsourced market-share, CTR, recovery,
winner, and penalty claims.

## Evidence Boundary

Use these labels when applying this reference:

| Label | Meaning | Allowed use |
|------|---------|-------------|
| Confirmed | A Google-owned source directly supports the fact | Guidance within the documented scope |
| Pending observation | Google confirms an event, but not its effect on a site | Monitoring and comparison planning only |
| Data anomaly | Google confirms a reporting defect | Exclude or annotate the affected measurement window |
| Source conflict | Current Google-owned pages disagree | Cite both and verify in the affected account |
| Inference | A recommendation follows from confirmed facts but is not Google's wording | Label it and keep it reversible |

Product announcements are product context, not ranking factors. Update dates do
not prove why a site gained or lost visibility.

## September 2026 Baseline

The latest confirmed ranking event is the September 2026 spam update. Google
says it began on September 24, applies globally to all languages, and may take
up to two weeks to complete. Its status dashboard marked the rollout complete
as of October 8, 2026. Google did not publish a target profile.

Sources:
https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history
https://status.search.google.com/incidents.json

Treat any property-level impact as pending observation. Google's core-update
analysis guidance says to wait a full week after rollout before comparison.
October 15 is therefore the first complete post-update comparison date for the
September update. The August 2026 spam update (August 18 to August 21) is the
previous event; its comparison window has already closed, so do not mix the two
windows when analyzing a change that falls between them.

Source:
https://developers.google.com/search/docs/appearance/core-updates

## 2026 Confirmed Ranking Timeline

| Event | Confirmed dates | Operational treatment |
|------|-----------------|-----------------------|
| February 2026 Discover update | February 5 to February 27 | Analyze Discover separately from Web Search |
| March 2026 spam update | March 24 to March 25 | Check spam-policy exposure only when local evidence exists |
| March 2026 core update | March 27 to April 8 | Use the documented post-update comparison procedure |
| May 2026 core update | May 21 to June 2 | Keep event timing separate from causation |
| June 2026 spam update | June 24 to June 26 | Do not infer a policy category from the rollout alone |
| August 2026 spam update | August 18 to August 21 | Compare against the closed window; do not merge it with the September event |
| September 2026 spam update | September 24 to October 8 | Keep impact pending until at least October 15 |

Source history:
https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history

## Post-Update Analysis

Use Google's documented procedure:

1. Confirm that the rollout has finished.
2. Wait at least one full week.
3. Compare a post-update week with a week before rollout.
4. Analyze Web Search, Images, Video mode, and News separately.
5. Distinguish small movement from a large, sustained drop.
6. Avoid quick fixes and mass deletion.
7. Check technical, policy, and editorial evidence before naming a cause.

Source:
https://developers.google.com/search/docs/appearance/core-updates

## Search Console Measurement Anomalies

Google records two relevant August logging defects:

- August 13: reduced reported Discover clicks and impressions, including
  reduced generative-AI Discover impressions where that report is available.
- August 13 through August 17: reduced reported impressions in the
  generative-AI Search performance report.

Google says these affected data logging only. They began before the August 18
spam update, so those dates cannot support a spam-update diagnosis.

Source:
https://support.google.com/webmasters/answer/6211453?hl=en

## Helpful Content, Spam, and E-E-A-T

Google recommends helpful, reliable, people-first content. Generative AI use is
not automatically a violation. Scaled content abuse concerns many pages created
primarily to manipulate rankings without adding value, regardless of whether
people, automation, or both produced them.

Sources:

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/essentials/spam-policies
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

E-E-A-T is quality-rater language, not a published numeric Google ranking
factor. Use experience, expertise, authoritativeness, and trust as editorial
review lenses. Do not fabricate first-hand experience, credentials, testing,
statistics, reviews, or testimonials.

### Helpful-content page update (2026-10-05)

Google's helpful-content page shows "Last updated 2026-10-05 UTC" (fetched
2026-10-11). The Search Central updates log carries no matching entry, so that
date comes from the page itself. The page says:

- Evaluate content by Who, How, and Why. Why is described as perhaps the most
  important question.
- Add accurate authorship information, such as bylines, where readers might
  expect it.
- Fabricating creator profiles (AI-generated headshots, made-up names, false
  credentials) is a form of deception.
- Changing page dates to look fresh when the content has not substantially
  changed is listed as a warning sign.
- Ask whether the use of automation, including AI generation, is self-evident
  to visitors through disclosures or other ways.
- Trust is the most important E-E-A-T aspect, and E-E-A-T itself is not a
  specific ranking factor.

Operational reading (inference): publish `dateModified` only after a
substantive edit, use only real author profiles, and disclose AI assistance
where readers would expect to know.

Related Search Central entries, verified from the updates log and the pages
themselves on 2026-10-11:

- 2026-10-01: the generative-AI content guide
  (https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)
  says to fact-check AI output before publishing, to consider explaining how
  content was created, and that many pages generated without added value may
  violate the scaled content abuse policy.
- 2026-09-16: the Search profile badge guide
  (https://developers.google.com/search/docs/appearance/search-profiles) covers
  a badge that links readers to a claimed Search profile. It states no ranking
  effect for the badge.

## Structured Data

Recommend structured data only when the visible page supports it and the type
is eligible for the intended Google Search feature.

- FAQ rich results are no longer shown in Google Search. FAQPage can remain
  schema.org-valid, but it provides no Google rich-result or documented
  generative-AI advantage.
- QAPage is for a page focused on one question where users can submit answers.
- PracticeProblem is no longer shown in Google Search.
- Dataset markup is for Dataset Search, not ordinary Google Search results.
- JavaScript-generated structured data can be processed when it appears in the
  rendered DOM and matches visible content.

Sources:

- https://developers.google.com/search/updates
- https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript
- https://developers.google.com/search/docs/appearance/structured-data/search-gallery

### Review Integrity

Google's July 24 review snippet guidance says not to include fake reviews or
incentivized reviews without clear and prominent disclosure. Review content and
ratings in structured data must be visible to users, and aggregate ratings must
not be copied from other websites.

Source:
https://developers.google.com/search/docs/appearance/structured-data/review-snippet

Schema validation proves syntax and eligibility fields. It does not prove that
a review, reviewer, rating, or experience is authentic.

## Search Console Generative-AI Reports

Google announced separate Search and Discover generative-AI reports on June 3,
initially for a subset of properties. Its August 31 update says the insights
have rolled out to all websites worldwide. Do not promise clicks or queries in those dedicated
views. No supported Search Console API endpoint is documented for the dedicated
reports, so API tooling must report the capability as unavailable rather than
synthesize it.

Source:
https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports

Standard Search Analytics includes AI-feature activity under Google's normal
aggregation rules. It does not isolate AI Overviews or AI Mode.

## Platform Properties

Search Central's July 29 announcement says platform properties for Instagram,
TikTok, X, and YouTube are globally available to everyone. The current Search
Console Help page still says gradual rollout. This is a source conflict.

Sources:

- https://developers.google.com/search/blog/2026/07/platform-properties-social-video-guide
- https://support.google.com/webmasters/answer/17148418?hl=en-GB

Verify account availability. Do not claim that the current Search Console API
or `/blog google gsc` retrieves the dedicated platform reports.

## Preferred Sources

Preferred Sources is reader-controlled audience development, not a general
ranking signal. It works at domain or subdomain level, not subdirectory level.
Google documents standard and custom interactive buttons plus a non-JavaScript
deeplink. The action must remain user-triggered.

Source:
https://developers.google.com/search/docs/appearance/preferred-sources

## Discover

Discover requires no special structured data. Use useful, original, timely,
non-sensational content and relevant, representative images. Google's preferred
image guidance calls for at least 1200px width, more than 300,000 pixels, and
large-image preview eligibility.

Source:
https://developers.google.com/search/docs/appearance/google-discover

## Crawl, Navigation, and Snippets

- Googlebot processes the first 2MB of supported files and the first 64MB of
  PDFs, measured uncompressed. Keep critical metadata and primary content
  before the cutoff. This is not a ranking factor.
- Back-button hijacking requires deceptive behavior. Normal History API use is
  not a violation by syntax alone.
- Content targeted by a Read more deep link should remain visible and retain
  its hash on load.

Sources:

- https://developers.google.com/search/docs/crawling-indexing/googlebot
- https://developers.google.com/search/blog/2026/04/back-button-hijacking
- https://developers.google.com/search/docs/appearance/snippet

## Canonical Reevaluation

After a material canonicalization fix, Google may keep a URL in the duplicate
cluster for up to two weeks. When the implementation is correct and still
inside that window, report `PENDING_REEVALUATION`. Request Indexing is
quota-limited and should be reserved for important URLs.

Source:
https://developers.google.com/search/docs/crawling-indexing/canonicalization-troubleshooting

## Google Ads Keyword Planning

Google Ads API v25.1 was released on August 19, 2026. Google's support table
lists Python client 31.2.0 as the minimum for API v25.

Sources:

- https://developers.google.com/google-ads/api/docs/release-notes
- https://developers.google.com/google-ads/api/docs/sunset-dates

Keyword Planner competition represents advertiser competition, not organic SEO
difficulty. Account eligibility and developer-token access are separate from
package compatibility. Test client and request construction offline before any
credentialed call.

## Cost and Authorization Boundary

Most implemented integrations have no usage fee within their documented
quotas. Cloud Natural Language requires billing and can incur charges after its
free monthly tier. Google Ads requires account and developer-token access.
Never enable billing or make a paid request without explicit user approval.

Sources:

- https://cloud.google.com/natural-language/pricing
- https://developers.google.com/google-ads/api/docs/access-levels

## Refresh Procedure

Maintainer steps, run against a trusted checkout of this repository (`<repo-root>` is
its absolute path):

1. Run `python3 "<repo-root>/scripts/check_google_currentness.py" --root "<repo-root>" --json`.
2. Review all manual sources in `data/google-updates.json`.
3. Add only claims directly supported by the cited source.
4. Keep source conflicts and pending impact explicit.
5. Run `python3 "<repo-root>/scripts/sync_google_updates.py" --root "<repo-root>"`.
6. Run the Google ledger tests and repository release gates.

The automated checker reports new source dates and stale reviews. It never
creates guidance, changes scoring, or decides what an update targeted.
