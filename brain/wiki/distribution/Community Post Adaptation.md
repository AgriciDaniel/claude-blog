---
type: spoke
title: "Community Post Adaptation"
domain: "Blog Distribution"
status: active
created: 2026-07-06
updated: 2026-07-09
tags:
  - distribution
  - community
  - adaptation
  - active
confidence: advisory
related:
  - "[[Distribution and Repurposing]]"
  - "[[Canonical Attribution Rules]]"
  - "[[Repurposing Source Fidelity]]"
  - "[[Channel Asset Inventory]]"
  - "[[Owned Audience Loop]]"
  - "[[Voice and Style]]"
  - "[[AI Citation Mechanics]]"
  - "[[Zero Click Planning Baseline]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/"
  - "https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links"
  - "https://developers.google.com/search/docs/essentials/spam-policies"
---

# Community Post Adaptation

## Community Post Adaptation Participation Job

Community Post Adaptation converts a blog post into a useful community contribution. The job is not to paste a teaser and wait for clicks. It is to answer the community's live question, disclose the relationship to the original post, and offer the canonical URL only when it helps the thread. Because community posts can become a source of copied claims, this note routes factual boundaries to [[Repurposing Source Fidelity]].

### Community Context To Preserve Before Posting

Capture the community name, rule that permits or blocks links, audience problem, canonical post URL, claim being reused, and disclosure wording. If the post mentions Google AI visibility, cite `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` so the community copy does not imply an llms.txt requirement. Use `g-helpful-content` to keep the adaptation centered on the reader's problem.

### Adaptations Allowed In Community Replies

The adapter may change the opener into a direct answer, turn a section into a checklist, remove promotional phrasing, and replace a full link with a source summary when the rules demand it. It must not broaden a claim, hide the author's affiliation, or cite `sparktoro-zero-click-2026` as proof that this community will send traffic. The click-scarcity discussion belongs in [[Zero Click Planning Baseline]].

## Community Post Adaptation Decision Table

| Community decision | Required input | Source ids | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Posting permission | Link, self-promotion, and disclosure rules | Community rules, `g-qualify-links` | Pending until checked | Community owner | Record rule excerpt |
| Answer utility | Specific question the reply solves | `g-helpful-content` | Reviewed in draft | Content lead | Rewrite as answer first |
| Source preservation | Claim, date, and cited origin retained | [[Repurposing Source Fidelity]] | Requires factcheck | Source owner | Add compact source note |
| AI feature wording | No invented Google AI setup requirement | `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` | Confirmed by SEO reviewer | SEO owner | Remove unsupported task language |
| Spam boundary | Avoid scaled, repetitive, or deceptive reposting | `g-spam-policies` | Advisory for owned web surfaces | Distribution lead | Limit repeats and note context |
| Link outcome | Canonical URL, no URL, or source-only reference | `g-qualify-links`, [[Canonical Attribution Rules]] | Channel-dependent | Community owner | Choose compliant attribution |
| Affiliation disclosure | Plain relationship to the post or brand | `g-qualify-links` | Open until visible in copy | Community owner | Add short disclosure sentence |
| Moderator revision | Required edit, removal reason, or warning | Community rules, `g-spam-policies` | Pending until logged | Distribution lead | Update inventory status |

## Disclosure, Context, And Non-Promotional Utility

A community adaptation should be able to stand alone if the link is removed. The first paragraph answers the thread, the middle explains what evidence changes the answer, and the final sentence offers the canonical post as optional detail. If the community bans links, record that in [[Channel Asset Inventory]] and avoid workaround behavior. The reviewer should flag posts that read like ads, bulk distribution, or thin rewrites.

### Example: Replying To An AI Setup Question

In a marketing community, a member asks whether a blog needs an llms.txt file for Google AI features. The adapted reply answers the question first, cites `g-ai-opt-guide` and `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, then offers the canonical article only as optional background. The post does not paste the whole article or imply that the community link will create AI visibility.

### Community-Specific Failure Modes

The adaptation fails when disclosure appears only in a profile bio, when the same answer is dropped into multiple communities without the local question, or when a rule against links is bypassed with obfuscated URLs. It also fails when `sparktoro-zero-click-2026` is used to predict community referral volume instead of context inside [[Zero Click Planning Baseline]].

### Matrix Row Produced

[[Repurposing Asset Matrix]] consumes the community asset as a discussion or reply row. It needs community rule excerpt, exact question, disclosure wording, reused claim list, canonical-link decision, and moderation status; it expects approved, blocked, or revise before posting.

## Community Post Adaptation Fidelity Checks

1. Identify the exact community question and write a one-sentence answer before adding any link.
2. Check the community rule on links, affiliation, promotion, and repeated posting.
3. Map every reused claim to the canonical post or original source ID.
4. Add disclosure wording that is plain, short, and visible.
5. Save the asset row with owner, posting status, and measurement plan.

## Source IDs Wired

This note uses `g-helpful-content`, `g-ai-opt-guide`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, `sparktoro-zero-click-2026`, `g-qualify-links`, and `g-spam-policies`.
