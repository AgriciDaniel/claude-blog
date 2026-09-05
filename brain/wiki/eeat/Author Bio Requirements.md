---
type: spoke
title: "Author Bio Requirements"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[Experience Evidence Checklist]]"
  - "[[Reviewer And Expert Review Rules]]"
  - "[[Reputation Research Workflow]]"
  - "[[Trust Signal Inventory]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/essentials/spam-policies"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
---
# Author Bio Requirements

## Author Bio Requirements Distinct Job

This note defines what an author bio must prove for a specific blog post. A name and job title are not enough when the article asks readers to rely on experience, expertise, recommendations, or sensitive guidance. The bio gate checks topic fit, not prestige in the abstract. Google helpful-content guidance and the QRG support the general need for people-first, trustworthy content and inspectable expertise signals (source_ids: g-helpful-content, g-qrg-full). Spam-policy evidence is used only when fabricated, misleading, or mass-produced author presentation is part of the risk (source_id: g-spam-policies). NN/g helps make the bio understandable without forcing readers to infer the author's relevance (source_id: nng-editorial-heuristics).

### Inputs For Bio Fit

Use the draft topic, target reader decision, author profile, reviewer profile if separate, relevant credentials, lived or operational experience, and any public reputation evidence. If the bio depends on external recognition, pair this note with [[Reputation Research Workflow]].

### Decisions The Bio Gate Records

The gate records whether the author is credible for this exact article, which claim types they can support, and where a reviewer or expert needs to supplement the byline.

## Author Evidence Requirement Table

| Bio decision | Required input | Source ids | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Topic fit | Bio statement tied to the article's subject and reader task | g-helpful-content, g-qrg-full | Generic role language is insufficient | Editor | Rewrite bio around relevant experience |
| Experience proof | Projects, field work, product use, interviews, or operational exposure | g-qrg-full, nng-editorial-heuristics | Unsupported experience claim lowers trust | Author | Add visible proof or move claim to reviewer note |
| Expertise limit | Clear boundary for what the author can and cannot advise on | g-helpful-content, g-qrg-full | Overbroad bio needs narrowing | Managing editor | Add limitation sentence near byline or disclosure |
| Reviewer separation | Reviewer name, specialty, review date, and scope | g-qrg-full, nng-editorial-heuristics | Reviewer is not interchangeable with author | Reviewer | Send to [[Reviewer And Expert Review Rules]] |
| Fabrication risk | Identity, credentials, and profile evidence checked for plausibility | g-spam-policies, g-qrg-full | Unverifiable bio blocks trust claim | SEO lead | Escalate before publication recommendation |
| Claim permission | Article claim types matched to author evidence | g-qrg-full, g-helpful-content | Bio cannot support every recommendation | Editor | Move unsupported advice to reviewer scope |
| Bio placement | Relevant proof visible near the byline or author box | nng-editorial-heuristics, g-qrg-full | Proof hidden on distant profile weakens trust | Managing editor | Add concise topic-fit sentence |

## Source IDs, Confidence, And Bio Owner

- `g-helpful-content`: supports matching author evidence to reader usefulness.
- `g-qrg-full`: supports the quality-review lens for expertise, trust, and page purpose.
- `g-spam-policies`: supports caution around deceptive or scaled identity patterns.
- `nng-editorial-heuristics`: supports clear presentation of who did what and why it matters.

Use `high` confidence only when the bio, article topic, and reviewer record agree. A recognized author can still fail this gate if the note cannot connect their background to the page's claims.

## Bio Gate Procedure

1. Read the article purpose and list the claim types that depend on author credibility.
2. Compare those claims with the author bio and remove credentials that do not explain topic relevance.
3. Add first-hand or operational evidence from [[Experience Evidence Checklist]] where the article leans on lived experience.
4. Decide whether expert review is required and record it through [[Reviewer And Expert Review Rules]].
5. If reputation proof is cited, verify it independently through [[Reputation Research Workflow]].
6. Leave a short owner note that says whether the bio is ready, needs rewrite, or requires escalation.

## Bio Fit Mini Case

A payroll-tax article lists a senior content marketer as author. The bio says "writes about small business growth", but the draft recommends filing decisions that can affect money and compliance. Under the QRG and helpful-content frame, the author can own plain-language explanation, while tax-specific instructions need reviewer scope or removal (source_ids: g-qrg-full, g-helpful-content). The edited bio names the author's payroll-operations interviews, adds a reviewer note from a qualified payroll specialist, and limits the article to informational guidance until jurisdiction-specific claims are sourced.

## Bio Gate Failure Cases

- A founder bio signals authority for company history, not automatically for technical, legal, or medical claims; map credentials to claim type before scoring (source_id: g-qrg-full).
- A ghostwritten post uses a famous byline, but the evidence packet shows no review by that person; treat ownership as unresolved (source_ids: g-qrg-full, g-spam-policies).
- A credential is real but stale for a fast-changing topic; require a current review date before the bio supports advice (source_id: g-helpful-content).
- A reviewer is added to compensate for a weak author, yet their scope excludes the strongest recommendations; downgrade the claim-permission row (source_id: g-qrg-full).

## Article Contract Bio Handoff

[[Blog Write Article Contract]] uses this note when the draft package names an author or reviewer. Inputs supplied are article purpose, claim-permission map, author-topic fit sentence, reviewer scope, and fabrication-risk status. The contract expects a byline note, reviewer note, and blocked advice list, with `g-qrg-full` attached wherever credibility changes the delivery decision.
