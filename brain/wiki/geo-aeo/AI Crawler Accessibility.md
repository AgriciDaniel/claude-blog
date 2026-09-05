---
type: spoke
title: "AI Crawler Accessibility"
domain: "GEO and AEO"
status: evergreen
created: 2026-07-10
updated: 2026-07-10
tags: [geo-aeo, ai-citation, technical]
---

# AI Crawler Accessibility

## AI Crawler Accessibility Review Scope

This note checks whether an important blog URL can be fetched, read, and evidenced for Google Search AI features and selected non-Google answer engines. It is an evidence-routing note, not a promise that crawler access will create citations.

Use `g-ai-opt-guide` and `g-ai-features` for Google Search AI boundaries: Google does not require a special AI file or AI-only schema. Use `g-robots-intro`, `g-googlebot`, `g-inside-googlebot`, and `g-common-crawlers` for Google crawler and robots discussions. For GPTBot, ClaudeBot, PerplexityBot, CDN bot controls, and provider-specific bot behavior, use owner-supplied provider documentation, raw fetch tests, server logs, or CDN screenshots until a matching source-ledger ID exists.

### Evidence This Note Accepts

- Rendered HTML source captured with JavaScript disabled or by raw fetch.
- robots.txt rule, meta robots directive, and HTTP header evidence.
- CDN or bot-management setting screenshot supplied by the owner.
- Status code, response headers, response size, and timestamp for each tested user agent.

### Evidence This Note Rejects

Do not treat Google-Extended as an AI Overview control, do not apply Google's 2 MB Googlebot fetch limit to GPTBot, ClaudeBot, or PerplexityBot without provider evidence, and do not claim a CDN setting is safe without owner-supplied proof.

## Accessibility Evidence Table

| Check | What to verify | Source IDs or evidence | Boundary | Owner | Action |
|---|---|---|---|---|---|
| Google AI Search eligibility | URL is crawlable, indexable, and not blocked by snippet controls | `g-ai-features`, `g-ai-opt-guide` | Official Google Search AI guidance only | Technical SEO | Route preview issues to [[AI Feature Preview Controls]] |
| Googlebot fetch size | Important HTML and links appear early enough in the response | `g-googlebot`, `g-inside-googlebot` | Googlebot evidence, not non-Google bot evidence | Developer | Reduce bloat or move content into initial HTML |
| robots.txt policy | Rules match the intended crawler access policy | `g-robots-intro`, `g-common-crawlers` for Google; owner-supplied for GPTBot, ClaudeBot, PerplexityBot | Robots controls crawling, not guaranteed indexing or citation | Technical SEO | Capture the rule and the business owner |
| Static or SSR HTML | Article body, source links, and schema are present without client-side rendering | `g-ai-opt-guide` for Google; owner-supplied raw fetch evidence for non-Google bots | Non-Google JavaScript behavior needs provider evidence | Developer | Use SSG, SSR, or ISR for article body |
| GPTBot access | Status code, response body, and bot-management result for GPTBot | owner-supplied provider doc or fetch/log evidence | No ledger source ID in this brain yet | Site owner | Add provenance before client reporting |
| ClaudeBot access | Status code, response body, and bot-management result for ClaudeBot | owner-supplied provider doc or fetch/log evidence | No ledger source ID in this brain yet | Site owner | Add provenance before client reporting |
| PerplexityBot access | Status code, response body, and bot-management result for PerplexityBot | owner-supplied provider doc or fetch/log evidence | No ledger source ID in this brain yet | Site owner | Add provenance before client reporting |
| CDN or firewall controls | Bot category, challenge rule, block rule, and bypass rule state | owner-supplied CDN screenshot or export | Provider UI claims are not source-ledger evidence | Site owner | Attach screenshot date and rollback owner |

## Review Procedure

1. Pick the target surface: Google AI feature, GPTBot, ClaudeBot, PerplexityBot, or another documented bot.
2. Capture raw HTML, status code, response size, and response headers for the target URL.
3. Confirm the article body, source attribution, canonical link, and structured data are visible in initial HTML.
4. Compare robots.txt, meta robots, HTTP headers, and CDN rules against the intended access policy.
5. Mark non-Google bot claims as owner-supplied until a source-ledger entry is added.

## Handoff Rule

A URL passes this note only when the target crawler can fetch a useful HTML response and the evidence packet names the crawler, date, status code, response-size evidence, source IDs or owner-supplied proof, and rollback owner. Passing means "accessible for review", not "will be cited".
