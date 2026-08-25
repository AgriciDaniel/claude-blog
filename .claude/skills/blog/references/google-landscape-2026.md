# SEO Landscape 2026: Google Updates & E-E-A-T

## July 2026 Search Baseline

As verified on 2026-07-23, the latest confirmed ranking event is the June 2026
spam update, 2026-06-24 to 2026-06-26. The latest confirmed core update is the
May 2026 core update, 2026-05-21 to 2026-06-02. Do not turn status-dashboard
dates into causal claims about what a specific update rewarded or penalized.
E-E-A-T is quality-rater language, not a single confirmed ranking factor;
evidence expectations apply broadly and are highest for YMYL topics.

### Authenticity Signals Google Evaluates

| Signal | Description |
|--------|-------------|
| Original images/video | Not stock photos - real screenshots, photos, demos |
| Specific language | Details only direct experience provides |
| Verifiable first-hand evidence | Method, sample, result, screenshots, or other proof when experience is claimed |
| Original data | Proprietary surveys, case studies, experiments |
| Build-in-public docs | Process documentation, behind-the-scenes |

### What Gets Penalized
- Articles that read like "summaries of top five search results"
- Scaled low-value content created primarily to manipulate Search, regardless of
  whether people, automation, or both produced it
- Content without unique perspective or original information

### Key Clarification
Google evaluates helpfulness, reliability, originality, and value rather than
assigning quality by production method. Generative AI use is not itself a
violation. Scaled content abuse applies when many pages are produced primarily
to manipulate rankings and provide little value, whether the production is
manual, automated, or mixed.

### Post-Update Analysis

Use Google's documented procedure rather than reverse-engineering a winner
profile:

1. Confirm the update has finished, then wait at least one full week.
2. Compare a week after completion with a week before rollout.
3. Separate Web Search, Images, Video mode, and News tab data.
4. Distinguish small position movement from a large, sustained site-wide drop.
5. Avoid quick fixes and mass deletion. Improve reader value and structure in
   durable ways; deletion is a last resort for content that cannot be salvaged.
6. Remember that smaller core changes can be unannounced and improvements can
   take effect without waiting for another named update.

### Quality Rater Guidelines Updates

**September 2025 QRG Update:**
- Added AI Overview evaluation criteria - raters now assess AI-generated summary accuracy
- Expanded YMYL definitions to cover broader range of topics affecting wellbeing
- Key principle codified: "Trust is the most important member of the E-E-A-T family"
- This 182-page September 11, 2025 version remains current as of 2026-07-07

**January 2025 QRG Update:**
- First formal "generative AI" definition added to the guidelines
- Scaled content abuse is explicitly flagged when content is produced at scale
  primarily to manipulate rankings and provides little value
- Raters evaluate the resulting page's purpose, originality, accuracy, effort,
  and value rather than treating production method as a quality verdict

## 2026 Algorithm Timeline

Google-owned status sources are current through 2026-07-23.

| Update | Dates | Blog Impact |
|--------|-------|-------------|
| December 2025 Core Update | 2025-12-11 to 2025-12-29 | Quality reassessment; reinforce helpful, trustworthy, differentiated content |
| Discover Update | 2026-02-05 | Monitor Discover traffic separately from core ranking volatility |
| March 2026 Spam Update | 2026-03-24 | Spam enforcement; keep scaled and low-value AI pages out of the index |
| March 2026 Core Update | 2026-03-27 to 2026-04-08 | Named core update; use the standard post-update analysis procedure |
| May 2026 Core Update | 2026-05-21 to 2026-06-02 | Latest named core update as of 2026-07-23 |
| June 2026 Spam Update | 2026-06-24 to 2026-06-26 | Spam enforcement; thin aggregation and abusive automation remain high risk |

Treat third-party reports of an unconfirmed July 2026 update as volatility only,
not as a Google-confirmed event.

## E-E-A-T Framework Since December 2025

Google's helpful-content guidance uses E-E-A-T as quality-rater language. It is
not a published numeric ranking factor. Use it as an internal quality lens, with
the highest scrutiny for YMYL and other high-harm topics.

| Factor | Internal review emphasis | Key Signals |
|--------|--------------------------|-------------|
| Experience | Internal heuristic only | First-hand knowledge when genuine, original content, case studies |
| Expertise | Internal heuristic only | Credentials, depth, technical accuracy |
| Authoritativeness | Internal heuristic only | Industry recognition, citations, reputation |
| Trustworthiness | Internal heuristic only | Contact info, transparency, security |

### YMYL Topics (Highest Scrutiny)
Health, finance, legal, news, elections, democratic processes, groups of people.

### Content Assessment (September 2025 QRG)
- Apply the same purpose, quality, accuracy, and value review regardless of how
  the page was produced
- Generic language, unsupported claims, no unique contribution, and
  regurgitated facts are quality defects, not authorship proof

## Hidden Gems Ranking System

Experience-based niche content is handled by Google's core ranking systems, not
a separate "Hidden Gems" system to optimize for directly. The practical takeaway
is to publish first-hand knowledge and personal insights where they genuinely
answer the query.

- 70.85% of keyphrases with product reviews show "Discussions and Forums" SERP feature
  (Jul 2024 re-analysis; original Feb 2024 figure was 77%, now outdated)
- 7,085 of 10,000 keyphrases show "Discussions and Forums" features (Detailed.com)
- Perspectives filter replaced by "Forums" filter (March 2024)
- User-generated content (YouTube, TikTok, Instagram) appears in carousels

## Structured Data 2026

### Active (Recommend Freely)
- Article or BlogPosting with Person author and Organization publisher. Article is
  the priority type for blog content after FAQ and HowTo rich result removal.
- Organization, LocalBusiness
- BreadcrumbList
- Person (author credentials)
- Product, SoftwareApplication
- AggregateRating, Review (only supported on eligible types: Product, Recipe,
  SoftwareApplication, LocalBusiness, Movie, Book - NOT on BlogPosting directly)
- Video, Product, Review, and Event when the page has eligible visible content

Still rich-result-eligible for blog content in 2026: Article, BreadcrumbList,
Video, Product, Review, and Event.

FAQPage is optional only when visible Q&A independently helps readers. Google
retired FAQ rich results for all sites starting 2026-05-07, including
government and health sites, and removed the feature documentation in June.
Existing FAQPage markup remains schema.org-valid, but it earns no Google rich
result or generative-AI advantage.

### Rich-Result Eligibility Notes
- FAQ rich results were fully retired for all sites starting 2026-05-07. HowTo
  was fully deprecated as of 2023-09-13.
- ClaimReview, SpecialAnnouncement, Course Info, Estimated Salary, Learning
  Video, and Vehicle Listing are former Google Search experiences.
- PracticeProblem was removed from Search and its documentation. Dataset is for
  Dataset Search, not ordinary Google Search rich results.
- Course Info is retired, but Course list is a distinct currently documented
  feature. QAPage remains narrow: one question with user-submitted answers.
- Schema.org validity is separate from Google Search feature eligibility.

### Critical Technical Note

Google can process JavaScript-generated structured data when it is present in
the rendered DOM. Test the rendered URL and make sure the markup matches visible
content. Source or server-rendered JSON-LD remains more portable for crawlers
that do not render JavaScript, but it is not a Google requirement.

## Google AI Overviews & AI Mode

### Coverage
- AI Overview coverage is methodology-dependent, not one fixed 49% figure.
- Conservative floor: about 20% of searches in Ahrefs data cited by SparkToro
  (SparkToro, 2026-06-09).
- Higher upper estimate: about 48% in BrightEdge reporting, but this is
  unconfirmed second-hand data.
- Semrush recalibrated AI Overview visibility to about 15.7% in November 2025.

### Traffic Impact (Seer Interactive, April 2026, 53 brands, 5.47M queries)
- AI Overview organic CTR hit a 1.3% floor in December 2025, then rebounded to
  about 2.4% by February 2026.
- The AIO-present CTR gap narrowed from about 61% to about 38% compared with
  no-AIO results.
- Vendor reporting described an association between being included as an AI
  Overview source and higher click activity. Treat this as unverified,
  methodology-specific, non-causal research context. It does not justify a
  citation-format, citation-position, or optimization target.

### AI Mode and Product Context

Google I/O 2026 announced Gemini 3.5 Flash as AI Mode's global default,
follow-up transitions from AI Overviews into AI Mode, multimodal inputs, and
information agents. Google's May 2026 Explore-the-web update highlighted
in-depth analyses, original content, public discussions, inline links, and link
previews. These are product capabilities, not published ranking factors.

Use them only as landscape context. Do not invent agent-specific schema,
fan-out landing-page factories, or scoring bonuses. The defensible response is
the same people-first SEO baseline: accurate, original, in-depth material;
authentic public discussion where relevant; clear page identity; and useful
images or video.

## Market Context

- Google market share is about 89.85% global in March 2026 and about 90% in
  April 2026; mobile is about 95.5%, desktop about 84.5%, and Bing about 5.1%
  (StatCounter).
- ChatGPT: 900M weekly users (Feb 2026), 2.5B daily queries (Jul 2025)
- AI referral traffic is small but the fastest-growing channel. It grew 3x+
  year over year from September 2024 to September 2025; Gemini surged to about
  18% share with 237% YoY growth, while ChatGPT share slid from about 87% to the
  high-60s (Similarweb, 2026-05-28). Do not cite a standardized share of total
  web traffic.
- Zero-click searches reached 68.01% of US Google searches from January to
  April 2026, up from 60.45% in 2024. About 276 clicks reach the open web per
  1,000 searches (SparkToro, 2026-06-09).
- Gartner: 25% decline in traditional search volume by 2026 (appears accurate)
- B2B SaaS discovery search declined 70-80% as buyers use AI assistants instead
  (primarily based on HubSpot case study; no rigorous sector-wide study confirms this as
  an industry average)

## Agentic Commerce & AI Advertising

Emerging trends reshaping search monetization:

- **ChatGPT Agent**: Autonomous web browsing, form-filling, purchasing on user's behalf
- **Universal Commerce Protocol (UCP)**: An open commerce standard for agentic
  product discovery and transactions, not a campaign type or advertising
  platform
- **AI Overview Ads**: Sponsored placements in AI Overviews grew from 1% to 25% of queries;
  projected to reach 50%+ by end of 2026
- **ChatGPT shopping traffic**: 11.4% conversion rate vs 5.3% organic search
  (Similarweb/Digiday, Sep 2025; finding contested by University of Hamburg/Frankfurt
  School study of 973 sites that found organic search outperforming ChatGPT by ~13%)
- **Perplexity**: Launched sponsored answers (Nov 2024, $50+ CPM), paused new
  advertisers (Oct 2025); OpenAI confirmed ad testing in ChatGPT during 2026
- **Implication for blogs**: Content must be structured for AI agent extraction (clear
  pricing, specs, comparisons) as agentic commerce bypasses traditional click paths

## AI Content Prevalence in Search

- 17.31% of top 20 search results contain AI-generated content (Originality.ai, Sep 2025,
  tracking 500 keywords)
- AI-generated content is now embedded across all verticals, not just low-quality niches
- Google's systems evaluate quality regardless of origin - but the sheer volume of AI
  content raises the bar for differentiation through original research and experience

## AMP Status

AMP is supported but not required and has no special ranking benefit. As of
2026-07-01, Google Search sends users directly to the publisher-hosted AMP URL
instead of routing through the AMP viewer or cache. Keep AMP when it provides
operational value; otherwise remove it carefully with correct canonicals and
redirects. AMP content ranks like other web pages.

## Search Feature Operations

### Canonical Changes

After fixing a duplicate or canonicalization issue, Google may keep pages in the
same duplicate cluster for up to two weeks. Mark a recently fixed case as
pending reevaluation rather than an immediate failure. Search Console's Request
Indexing feature is quota-limited; reserve it for the most important URLs.

### Search Console Generative AI Reports

The dedicated generative-AI reports are rolling out to a subset of properties.
Search and Discover have separate views. The Search view covers AI Overviews
and AI Mode and exposes impressions, pages, countries, devices, and dates.
Do not promise clicks or queries in this report. The blog-google API tooling
does not fetch the dedicated view; report `SKIPPED` or unavailable and direct
the user to Search Console until Google documents API support.

Platform properties for Instagram, TikTok, X, and YouTube are also rolling out
gradually. In their Search Console UI, eligible creators can see Search and
Discover performance, including clicks, impressions, posts, and queries. Do not
promise that the current Search Console API supports these property reports.

### Discover

Run Discover checks only when the site targets Discover or has Discover data.
Favor original, in-depth, timely, non-sensational content with topic-level
expertise and local relevance where applicable. Older useful content can still
appear. No special schema is required.

For a preferred Discover image, check all of:

- At least 1200px wide.
- More than 300,000 total pixels.
- Prefer a useful 16:9 crop.
- Relevant and representative, not generic or text-heavy.
- Enabled with `max-image-preview:large` or AMP.
- Declared through appropriate image markup or `og:image`.

### Preferred Sources

Preferred Sources is optional audience development, not a ranking signal. A
reader-selected domain or subdomain is more likely to appear in Top Stories and
may receive a preferred badge in AI Mode or AI Overviews for that reader. A
subdirectory alone is not eligible. Offer Google's publisher button only when
it fits the audience strategy.

### Crawling, Navigation, and Snippets

- Googlebot processes the first 2MB of a supported file and the first 64MB of a
  PDF, using uncompressed size. Keep the title, metadata, canonical, essential
  schema, and primary content before the HTML cutoff. Flag large inline
  base64, CSS, or JavaScript payloads.
- Back-button hijacking requires behavioral evidence that navigation is
  obstructed or users are sent to deceptive history entries. Do not flag normal
  History API use by syntax alone.
- For "Read more" deep links, keep target content immediately visible and retain
  its hash on page load. Avoid forced scroll resets or hash removal. This does
  not ban every accordion elsewhere on the page.

## Readability & Engagement Signals

Google does NOT use readability as a direct ranking factor. John Mueller has
stated this explicitly. Readability still affects user satisfaction and task
completion, but do not assert analytics metrics such as bounce rate, time on
page, scroll depth, or return visits as direct ranking inputs.

### Core Update Quality Patterns in 2026
Raptive analysis (published Feb 2026, high reliability) found:
- Sites with <7% of pages ≤500 words had more stable rankings
- Winning pages averaged 393 days freshness vs 500 for losers
- Sites with >4% branded search clicks showed stronger resilience
- Ad-to-content ratio <25% correlated with 4pp better performance
- **LCP >3 seconds** = 23% more traffic loss (ALM Corp, not Raptive)
- **INP >300ms** = 31% more traffic loss (ALM Corp, not Raptive)
- Thin content, template-based pages, and generic AI aggregation were penalized

### E-E-A-T Framing
Helpful, trustworthy content matters across topics. Evidence expectations scale
with topic risk, user harm, and YMYL sensitivity; do not claim a dated expansion
of E-E-A-T to every competitive query unless a primary Google source is loaded.

### Quality Rater Guidelines Updates
- **January 2025 QRG**: Added "Filler" section penalizing pages that bury useful
  information under padding content. Topical dilution and entity drift are
  explicit quality signals raters evaluate.
- **September 2025 QRG**: Added AI content evaluation criteria. AI content is
  acceptable IF it demonstrates genuine E-E-A-T. Low-quality markers: generic
  language, no unique insights, regurgitated facts.

### Hidden Gems Ranking System
Experience-based niche content is part of core ranking systems. It surfaces
useful first-hand content from forums, social media, and small blogs when that
content best satisfies the query. 70.85% of keyphrases with product reviews now
show "Discussions and Forums" SERP features (Jul 2024 re-analysis, Detailed.com).
Depth, originality, and strong intent alignment matter more than optimizing for a
separate Hidden Gems system.
