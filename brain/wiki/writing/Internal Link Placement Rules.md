---
type: spoke
title: "Internal Link Placement Rules"
domain: "Blog Writing"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [writing, six-pillar, evergreen]
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://ziptie.dev/blog/google-ai-overviews-source-selection/"
---

# Internal Link Placement Rules

## Internal Link Placement Rules Scope

This note owns where links are placed inside a draft, not the full cluster architecture. A good internal link appears when the reader needs the next explanation, proof, template, or caveat. It should support comprehension and navigation before it supports any abstract SEO quota.

### Allowed Actions And Disallowed Actions

Allowed actions include adding a contextual link after a concept is introduced, replacing a vague anchor with a specific one, and removing a link that interrupts the answer. Disallowed actions include stuffing the first paragraph with hub links, linking only for exact-match anchors, or using links to hide missing explanation. `g-helpful-content` supports the reader-first standard, and `g-ai-opt-guide` prevents hidden AI-only navigation advice.

### Exceptions That Require Approval

Approval is required before adding links in legal, medical, financial, or other trust-sensitive passages where the link might imply endorsement. Approval is also required when linking from a citation-ready paragraph could separate the claim from its source. `g-qrg-full` supplies the trust lens; `ziptie-aio-source-selection` supports keeping extraction candidates clean and self-contained.

## Internal Link Rule Table

| Rule | Source basis | Applies to | Exception | Approval path |
|---|---|---|---|---|
| Link at the moment of reader need | `g-helpful-content` | Educational and advisory sections | No link if the paragraph already resolves the task | Editor approves during draft review |
| Keep citation passages intact | `g-ai-opt-guide`, `ziptie-aio-source-selection` | Answer blocks and sourced paragraphs | Link after the source cue if needed | GEO reviewer checks extraction risk |
| Avoid link quotas | `g-helpful-content` | All blog drafts | Cluster hub may require a defined navigational link | Strategist documents reason |
| Use trust-aware anchors | `g-qrg-full` | YMYL-adjacent or expert-heavy sections | Generic anchor may be safer for legal text | Lead editor reviews |
| Route architecture elsewhere | `g-helpful-content` | Hub and spoke planning | Broken cluster ownership | Send to [[Semantic Topic Clusters]] |
| Link after proof | `g-helpful-content`, `g-ai-opt-guide` | Claim-bearing answer sections | Source cue must stay before the tangent | Editor checks paragraph flow |
| Mark stale targets | `g-helpful-content` | Links to old refresh or update posts | Do not send readers to outdated guidance | Owner schedules target review |

## Internal Link Review And Rollback

1. Read the paragraph before and after each proposed link.
2. Ask what reader question the link answers at that exact point.
3. Remove links that send the reader away before the section's answer is complete.
4. Check whether the link target is the canonical owner of the deeper topic.
5. Record exceptions in the review note, not in hidden markup.
6. Roll back any link that creates a dead wikilink, duplicate anchor, or unsupported endorsement.

### Placement Scenario

In a paragraph explaining why FAQPage markup is not a current rich-result tactic,
the source cue should appear before any link to a broader schema guide.
That keeps the claim attached to its evidence and avoids using a link as proof.
For Google-facing AI advice, links should deepen visible reader context rather
than act like hidden optimization infrastructure (`g-ai-opt-guide`).
The reader-first anchor test remains the controlling rule (`g-helpful-content`).

### Link Placement Hazards

- The first paragraph contains three hub links before answering the page promise (`g-helpful-content`).
- A citation-ready passage sends readers away before the caveat appears (`ziptie-aio-source-selection`).
- A link target is correct generally but stale for the current claim (`g-helpful-content`).
- Anchor text implies endorsement or certainty the source does not support (`g-qrg-full`).

### Deliverable Wiring

[[Semantic Cluster Execution Plan]] consumes this note for link briefs:
source page, target page, anchor reason, reader need, and stale-target flag.
It expects internal links to support hub and spoke execution without creating
thin duplicate paths (`g-helpful-content`). [[SEO Check Validation Checklist]]
consumes the final link list as a prepublication sanity check (`g-helpful-content`).

## Source Handling

The wired IDs are `g-helpful-content`, `g-ai-opt-guide`, `g-qrg-full`, and `ziptie-aio-source-selection`. This note does not claim internal links guarantee rankings or AI citations.

## Related

- [[Semantic Topic Clusters]]
- [[Citation Ready Paragraphs]]
- [[Intent Fit Writing Pass]]
- [[Blog Quality Score]]
