---
type: spoke
title: "Trust Signal Inventory"
status: evergreen
created: 2026-07-06
updated: 2026-07-09
tags: [eeat, evergreen]
domain: "Blog Trust"
confidence: verified
related:
  - "[[E-E-A-T for Blog Content]]"
  - "[[Editorial Transparency Checklist]]"
  - "[[Author Bio Requirements]]"
  - "[[Reputation Research Workflow]]"
  - "[[Source Quality Ladder]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
  - "https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf"
  - "https://developers.google.com/search/docs/essentials/spam-policies"
  - "https://www.nngroup.com/articles/ten-usability-heuristics/"
---
# Trust Signal Inventory

## Trust Signal Inventory Distinct Job

This inventory captures visible trust signals on a page or site and turns them into an action list. It is not a reputation verdict and not a design critique. The inventory asks whether readers can inspect ownership, expertise, sourcing, limitations, contact paths, and review status without relying on tone alone. Use `g-helpful-content` and `g-qrg-full` for trust-review substance, `g-spam-policies` when missing signals hide deceptive or mass-produced content, and `nng-editorial-heuristics` for visibility and recoverability of editorial state.

### Inputs Specific To Signal Inventory

Use the live or staged URL, rendered page, author box, About and contact pages, policy pages, source blocks, update date, monetization disclosures, and any review note from [[Editorial Transparency Checklist]].

### Decisions The Inventory Must Record

The inventory records whether each signal is present, absent, weak, stale, contradictory, or not applicable. It also distinguishes visible reader-facing signals from internal workflow proof.

## Trust Signal Inventory Table

| Signal group | Required input | Source ids | Evidence state | Owner | Next action |
|---|---|---|---|---|---|
| Page ownership | Byline, publisher, update date, and editorial owner | g-helpful-content, g-qrg-full | Missing owner creates high trust gap | Editor | Fix visible ownership fields |
| Author relevance | Bio tied to article topic and claim risk | g-qrg-full, nng-editorial-heuristics | Generic bio is weak evidence | Managing editor | Open [[Author Bio Requirements]] |
| Source visibility | Citations or source notes near consequential claims | g-helpful-content, g-qrg-full | Hidden source pack does not help readers | Research editor | Rebuild source placements through [[Source Quality Ladder]] |
| Reputation context | Independent evidence for brand or expert authority | g-qrg-full | Self-description alone is not enough | Research owner | Run [[Reputation Research Workflow]] |
| Limitations and disclosures | Caveats, conflicts, affiliate notes, and correction path | g-qrg-full, nng-editorial-heuristics | Missing disclosure can block recommendation | Content lead | Send to [[Editorial Transparency Checklist]] |
| Production integrity | Evidence that page is not scaled filler or copied template | g-spam-policies, g-helpful-content | Pattern risk requires escalation | SEO lead | Review through [[Value Less AI Content Warnings]] |
| Contact and correction access | Reader can find a practical route to report errors | nng-editorial-heuristics, g-qrg-full | Hidden contact path weakens recovery | Site owner | Add visible contact or correction route |
| Date coherence | Published date, updated date, and source freshness agree | g-helpful-content | Conflicting dates create uncertainty | Managing editor | Reconcile dates before audit closure |
| Mobile visibility | Byline, disclosures, and source notes remain visible on mobile | nng-editorial-heuristics, g-qrg-full | Collapsed trust elements are effectively absent | Editor | Capture mobile state in the inventory |

## Inventory Confidence, Owners, And Follow-up Rules

Inventory confidence is not the same as quality confidence. A page can have a complete inventory and still fail trust review if the signals are weak. Mark `high` only when required signals are visible, current, and aligned with the article's purpose.

## Trust Signal Inventory Operating Procedure

1. Capture the page as a reader sees it, including mobile if the layout hides bylines or disclosures.
2. Fill the table with observed page elements, not intended process.
3. Mark signals as weak when they exist but do not answer the reader's trust question.
4. Send owner, bio, reputation, and source gaps to their sibling notes.
5. Attach the inventory to the audit and list visible changes separately from internal process fixes.

## Inventory Walkthrough

A SaaS comparison page has an author box, citations, and an "updated" date, but the affiliate disclosure appears only after the recommendations and the mobile layout collapses the reviewer note. The inventory marks source visibility as present, limitations as weak, mobile visibility as failed, and production integrity as pending until similar comparison pages are checked. The QRG and helpful-content sources support inspecting whether trust evidence is usable for the reader, while NN/g supports treating hidden or collapsed status information as a usability risk (source_ids: g-qrg-full, g-helpful-content, nng-editorial-heuristics).

## Trust Signal Inventory Pitfalls

- A badge or award appears without date, issuer, or relationship context; send it to reputation research before treating it as authority proof (source_id: g-qrg-full).
- The About page has strong credentials, but the article gives no visible author-topic connection; open [[Author Bio Requirements]] (source_id: g-qrg-full).
- A source pack is complete internally, yet the reader-facing page hides citations after consequential claims; lower source visibility (source_id: g-helpful-content).
- Trust elements appear on desktop but disappear behind accordions on mobile; record the rendered state, not the CMS field (source_id: nng-editorial-heuristics).

## Full Site Audit Inventory Feed

[[Full Site Blog Audit Report]] consumes this inventory for page-level trust findings. Inputs supplied are signal state, observed page element, device checked, source IDs, owner, and visible-versus-internal distinction. The audit expects keep, improve, monitor, merge, or prune recommendations only after signal gaps are separated from quality or traffic assumptions.
