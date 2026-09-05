---
type: spoke
title: "Reputation Research Workflow"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[Author Bio Requirements]]"
  - "[[Source Quality Ladder]]"
  - "[[YMYL Escalation Matrix]]"
  - "[[Trust Signal Inventory]]"
source_urls:
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
---
# Reputation Research Workflow

## Reputation Research Workflow Stage Purpose

This workflow gathers outside evidence about an author, brand, publisher, or named expert before the brain treats them as authoritative for a blog topic. It separates internal marketing claims from independent reputation signals. The QRG is the controlling source for reputation review posture (source_id: g-qrg-full). The 2025-01-23 and 2025-09-11 QRG update records matter because the local source ledger tracks changes around generative AI, spammy pages, and expanded YMYL examples (source_ids: g-update-2025-01-23-qrg-update-jan-2025, g-update-2025-09-11-qrg-update-sept-2025). Helpful-content guidance keeps the research tied to reader usefulness (source_id: g-helpful-content).

### Trigger And Entry Criteria

Start this workflow when a page uses an author, brand, or reviewer reputation as part of why readers should trust the advice. Also trigger it for YMYL-adjacent topics, comparison posts with recommendations, and posts where the publisher's own claims are the only authority evidence.

### Output Artifact And Exit Criteria

The output is a dated reputation note with searched entity names, sources checked, positive or negative findings, confidence, and unresolved gaps. The workflow exits only when the review can say whether reputation evidence supports, complicates, or does not prove the claim.

## Reputation Research Step Table

| Step | Input | Evidence required | Produced artifact | Downstream handoff |
|---:|---|---|---|---|
| 1 | Entity name, aliases, site, and author profile | Exact names and URLs to avoid identity confusion | Entity scope line | [[Author Bio Requirements]] |
| 2 | Brand or author claims in the draft | Independent sources, not only the entity's own site | Claim-to-reputation map | [[Source Quality Ladder]] |
| 3 | Search results, reviews, professional profiles, citations, and news | Dated notes with source type and retrieval date | Reputation evidence log | [[Trust Signal Inventory]] |
| 4 | Negative, disputed, or missing evidence | Context and severity, not selective omission | Risk note | [[YMYL Escalation Matrix]] |
| 5 | Final editorial decision | Confidence label and limit statement | Handoff summary | [[E-E-A-T Review Rubric]] |
| 6 | Same-name people, brands, products, or domains | Disambiguating URLs, roles, dates, and locations | Identity match note | [[Author Bio Requirements]] |
| 7 | Sponsored awards, directories, testimonials, or partner pages | Independence check and relationship label | Reputation limitation | [[Editorial Transparency Checklist]] |

## Input, Evidence, Action, Owner, And Handoff

Assign research ownership to someone other than the article author when reputation is a core trust claim. If the only evidence is self-authored, mark the claim as unsupported for authority purposes. If the topic crosses money, health, safety, legal, civic, or political decision-making, apply the stricter path in [[YMYL Escalation Matrix]] before the reputation note closes.

## Reputation Research Control Points

1. Do not use a brand's About page as independent reputation proof.
2. Record neutral or negative evidence instead of filtering for favorable mentions.
3. Separate reputation for the entity from expertise for the individual author.
4. Date every volatile finding and refresh it before a major rewrite or relaunch.
5. Avoid ranking or traffic claims unless a different ledger source supports them.

## Reputation Research Scenario

A draft cites "Jordan Lee" as an outside expert for a cybersecurity article. Search results show a same-name keynote speaker, a vendor employee, and an unrelated crypto commentator. The workflow records aliases, profile URLs, employer, topic area, and date checked before the author bio can use reputation evidence. The QRG-backed posture is to avoid treating internal or ambiguous claims as independent authority proof (source_id: g-qrg-full). If the only strong evidence is a company profile, the handoff says reputation is unproven for outside authority and returns the claim to [[Source Quality Ladder]].

## Reputation Review Failure Points

- Paid directory badges look independent until the relationship is checked; label them as limited proof, not neutral reputation (source_id: g-qrg-full).
- Negative coverage is old but material to the exact advice being given; record date and context instead of suppressing it (source_id: g-qrg-full).
- A brand is reputable for one product line while the article relies on another; split entity reputation from topic expertise (source_id: g-helpful-content).
- Search results mix a person with a same-name entity, causing false trust transfer; disambiguation must happen before the bio gate closes (source_id: g-qrg-full).
- A professional profile confirms employment but not claim-specific expertise; send the unsupported part to the bio gate (source_id: g-qrg-full).
- A customer testimonial supports satisfaction, not editorial independence; keep it out of authority claims (source_id: g-qrg-full).
- A recent acquisition changes who owns the publisher; refresh brand reputation before a relaunch audit (source_id: g-helpful-content).
- A reputation claim depends on a source behind login; record access limits before handing it to reports (source_id: nng-editorial-heuristics).

## Brand Contract Evidence Feed

[[Brand Context Contract]] consumes reputation findings when a proof library claims authority, awards, expert status, or customer trust. Inputs provided are entity scope, independent evidence list, relationship labels, negative-context notes, confidence, and refresh date. The contract expects approved proof points, banned overclaims, and source IDs suitable for future briefs.
