---
type: spoke
title: "FLOW Review Stage"
domain: "Blog Workflow"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [flow, active]
confidence: advisory
related:
  - "[[FLOW Framework]]"
  - "[[FLOW Draft Stage]]"
  - "[[FLOW Factcheck Stage]]"
  - "[[Blog Quality Score]]"
  - "[[Blog Schema Stack]]"
---

# FLOW Review Stage

## Review Stage Purpose

FLOW Review Stage evaluates draft quality before factcheck and delivery. It checks whether the piece answers the reader's task, preserves the brief, uses links sensibly, handles schema and AI visibility claims carefully, and exposes any risk that should move into approval.

## Review Lenses

The review uses usefulness, source fidelity, structure, internal links, trust presentation, and implementation risk. `g-helpful-content` supports the usefulness lens. `g-qrg-full` supports trust and quality-evaluation framing. `g-intro-sd` supports structured-data eligibility checks, while `g-ai-opt-guide` keeps AI optimization advice inside normal Search guidance.

## Draft Review Table

| Review lane | Input | Evidence required | Action | Owner | Handoff |
|---|---|---|---|---|---|
| Reader usefulness | Draft, brief, target reader | `g-helpful-content` | Mark missing answer, thin section, or unsupported promise | Editor | [[FLOW Draft Stage]] |
| AI feature language | Draft AI Search section | `g-ai-opt-guide` | Remove special-file framing or unsupported inclusion claims | SEO reviewer | [[FLOW Factcheck Stage]] |
| Market context | Visibility or click behavior paragraph | Approved source packet with limits | Add scope caveat or move to report note | Strategy reviewer | [[AI Citation Mechanics]] |
| Link and schema readiness | Internal links, visible page elements | `g-intro-sd` plus [[Blog Schema Stack]] | Flag hidden-content or unsupported schema risk | Technical reviewer | [[FLOW Approval Queue]] |
| Trust and tone | Byline, disclosures, examples | `g-qrg-full` plus [[E-E-A-T for Blog Content]] | Request clearer ownership or reviewer evidence | Managing editor | [[Blog Quality Score]] |
| Source proximity | Claim placement and cited source list | Source IDs beside current claims | Move source closer or send to factcheck | Research reviewer | [[Factcheck Claim Register]] |
| Technical readiness | Rendered preview, schema note, image list | `g-intro-sd`, `g-google-images` | Flag implementation blockers before SEO check | Technical reviewer | [[SEO Check Validation Checklist]] |

## Risk Flags And Rework Routing

Send structure and answer problems back to the draft owner. Send unverifiable claims to [[FLOW Factcheck Stage]]. Send live implementation questions to [[FLOW Approval Queue]]. The review should not bury a blocker in prose; it names the owner and the stage that must resolve it.

## Exit Decision

The exit state is ready for factcheck, revise, blocked, or approval needed. A draft cannot be ready when it contains a current claim without source ID support or when a live-content change lacks a rollback path.

## Example: Review Before Factcheck

A draft introduction answers the target query, but the third section adds an AI
visibility promise that was absent from the brief.

The reviewer keeps the useful answer, marks the new AI sentence for factcheck,
and cites `g-ai-opt-guide` as the boundary for Google AI guidance.

The schema note says the proposed JSON-LD must describe visible content, so the
technical reviewer routes that item to [[Schema Generation Output Contract]]
under `g-intro-sd`.

The exit state becomes "revise plus factcheck" rather than "ready."

## Review Gaps That Create Rework

- A reviewer fixes wording but leaves the unsupported claim alive.
- A trust concern is scored without naming byline, reviewer, or source issue.
- Internal links are counted, but their reader task is never checked.
- Schema risk is deferred until publication and becomes a late blocker.

## Consumed By Scoring Deliverables

[[Blog Analyzer Score Report]] consumes review lanes, severity labels,
source-backed evidence, owner notes, and blocked categories.

[[SEO Check Validation Checklist]] consumes technical blockers, visible-content
schema concerns, image issues, and final-copy readiness.

The deliverables return score deductions, fix states, or blocked publication
reasons for the next owner.
