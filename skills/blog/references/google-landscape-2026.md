# Google Search Landscape 2026

Verified against Google-owned sources on 2026-08-25. The machine-readable
source of truth is `${CLAUDE_PLUGIN_ROOT}/data/google-updates.json`. This reference contains only
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

## August 2026 Baseline

The latest confirmed ranking event is the August 2026 spam update. Google says
it ran from August 18 through August 21 and applied globally to all languages.
Google did not publish a target profile.

Source:
https://status.search.google.com/incidents/LEubPCm2octf2uMqCFKE

Treat any property-level impact as pending observation. Google's core-update
analysis guidance says to wait a full week after rollout before comparison.
August 28 is therefore the first complete post-update comparison date.

Source:
https://developers.google.com/search/docs/appearance/core-updates

## 2026 Confirmed Ranking Timeline

| Event | Confirmed dates | Operational treatment |
|------|-----------------|-----------------------|
| February 2026 Discover core update | February 5 to February 27 | Analyze Discover separately from Web Search |
| March 2026 spam update | March 24 to March 25 | Check spam-policy exposure only when local evidence exists |
| March 2026 core update | March 27 to April 8 | Use the documented post-update comparison procedure |
| May 2026 core update | May 21 to June 2 | Keep event timing separate from causation |
| June 2026 spam update | June 24 to June 26 | Do not infer a policy category from the rollout alone |
| August 2026 spam update | August 18 to August 21 | Keep impact pending until at least August 28 |

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

Google documents separate Search and Discover generative-AI reports for a
subset of properties. Do not promise clicks or queries in those dedicated
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

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_google_currentness.py --root . --json`.
2. Review all manual sources in `${CLAUDE_PLUGIN_ROOT}/data/google-updates.json`.
3. Add only claims directly supported by the cited source.
4. Keep source conflicts and pending impact explicit.
5. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sync_google_updates.py --root .`.
6. Run the Google ledger tests and repository release gates.

The automated checker reports new source dates and stale reviews. It never
creates guidance, changes scoring, or decides what an update targeted.
