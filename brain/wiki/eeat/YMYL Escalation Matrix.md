---
type: spoke
title: "YMYL Escalation Matrix"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[YMYL Adjacent Blog Policy]]"
  - "[[Reviewer And Expert Review Rules]]"
  - "[[Source Quality Ladder]]"
  - "[[Editorial Transparency Checklist]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/essentials/spam-policies"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
---
# YMYL Escalation Matrix

## YMYL Escalation Matrix Comparison Job

This matrix compares reader risk across intents, assets, locales, links, and recommendation types. It turns "might be YMYL" into an auditable routing decision. `g-helpful-content` and `g-qrg-full` provide the quality and sensitivity basis, `g-spam-policies` is relevant when scaled pages or misleading claims compound the risk, and `nng-editorial-heuristics` supports clear status labels so escalations are not lost in handoff.

### Rows The Matrix Must Contain

Every review should include the topic, reader decision, claim type, asset format, locale or jurisdiction sensitivity, source strength, review requirement, and final action. Add a row for every page section that changes risk level.

### Columns That Make Escalation Auditable

Each row needs source IDs, evidence status, owner, confidence, and next action. Without those cells, the matrix becomes a label rather than a decision record.

## YMYL Escalation Decision Matrix

| Topic pattern | Reader decision risk | Required reviewer | Source requirement | Evidence cells | Confidence | Next action |
|---|---|---|---|---|---|---|
| General informational context | Low if no recommendation or instruction is given | Editor | Reliable source relevant to the explanation | Purpose, source date, limitation | Medium to high | Keep in normal E-E-A-T review |
| Product or service recommendation affecting money | Medium to high depending on cost and commitment | Editor plus subject reviewer | Primary, official, or first-party evidence for material claims | Price basis, comparison method, disclosure | Medium | Apply [[YMYL Adjacent Blog Policy]] |
| Health, safety, legal, or financial instruction | High | Qualified expert or remove advice | Official, clinical, regulator, or primary source as applicable | Reviewer scope, limitation, jurisdiction | Low until reviewed | Escalate before publication advice |
| Civic, political, or social decision content | High when it could affect public action | Senior editor plus topic reviewer | Primary documents and dated context | Claim map, date, dispute status | Medium only after review | Add review note and limitations |
| AI-generated sensitive page cluster | High if pages are scaled or repetitive | SEO lead plus reviewer | Source map and originality proof | Template check, added value, owner | Low until cleared | Open [[Value Less AI Content Warnings]] |
| Jurisdiction-dependent explanation | Medium to high when location changes the answer | Reviewer familiar with the named location | Official local source or primary document | Jurisdiction, date, limitation | Low until source verified | Narrow or split by locale |
| Calculator, checklist, or score tool | High when output guides action | Topic reviewer plus source owner | Formula source and assumption note | Inputs, assumptions, reviewer scope | Low until tested | Add caveat or remove tool |
| Vulnerable reader or minor audience | High when advice affects safety, rights, or wellbeing | Senior editor plus qualified reviewer | Primary or official source suited to the audience | Audience risk, guardian note, limits | Low until reviewed | Escalate before brief approval |

## Evidence Cells, Confidence, And Next Action

Confidence starts at `low` when the matrix depends on missing reviewer evidence, weak sources, or unclear jurisdiction. Raise confidence only after the required source tier and reviewer path are satisfied. A low-confidence row is still useful because it tells the workflow where to stop.

## YMYL Escalation Matrix Interpretation Rules

1. Use the highest-risk row for the page-level handoff, even if most sections are ordinary.
2. Treat locale and jurisdiction as risk multipliers when rules, eligibility, or safety standards differ.
3. Do not use disclaimers to replace expertise, source quality, or review.
4. If a row identifies scaled or generic AI risk, pause the YMYL decision until [[AI Assisted Content Accountability]] is complete.
5. Send unresolved source disputes to [[Source Quality Ladder]] before scoring trust readiness.

## Matrix Decision Example

A blog post asks, "Can I deduct my home office?" and includes a checklist for remote workers in several countries. The matrix chooses the jurisdiction-dependent row because location changes the answer and a wrong claim can affect money decisions. The article either splits by jurisdiction with official source IDs and reviewer scope, or narrows to general recordkeeping questions that do not tell readers what to claim. The QRG and helpful-content sources support choosing the highest reader-risk row before scoring trust (source_ids: g-qrg-full, g-helpful-content).

## Matrix Failure Modes

- The article uses one national source for readers in multiple countries; mark jurisdiction evidence incomplete (source_id: g-qrg-full).
- A comparison table includes affiliate products and financial recommendations; combine money-risk and disclosure checks before handoff (source_ids: g-qrg-full, nng-editorial-heuristics).
- A tool calculates savings from hidden assumptions; require formula source and limitation before the output is shown (source_id: g-helpful-content).
- An emergency or safety topic uses calming language while delaying urgent professional guidance; escalate severity regardless of keyword intent (source_id: g-qrg-full).
- A page mixes low-risk background with one high-risk tool; escalate the page by the tool row (source_id: g-qrg-full).

## Analyzer Escalation Output

[[Blog Analyzer Score Report]] consumes the matrix when a page has trust-risk flags. Inputs are selected risk row, reader decision, jurisdiction, source tier, reviewer status, confidence, and next action. The report expects blocker or advisory severity, reviewer owner, limitation wording, and source IDs for the highest-risk page section.
