---
type: spoke
title: "Banned Claims And Phrases"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Banned Claims And Phrases

## Banned Claims And Phrases Review Job

Banned Claims And Phrases is the stoplist for language that overpromises, hides uncertainty, or recycles outdated SEO advice. It protects [[Voice and Style]], [[Blog Quality Score]], and [[FLOW Framework]] from turning a draft into a ranking guarantee or a tool vendor pitch. A banned phrase can be a literal string, a claim pattern, or a missing caveat.

### Claims This Spoke Owns

This note owns guarantees, unsupported superlatives, unverifiable claims, deprecated tactics, and claims that confuse advisory notes with implementation authority. Use `g-helpful-content` for reader usefulness, `g-qrg-full` for trust and purpose, `nng-editorial-heuristics` for clear error prevention, `g-ai-opt-guide` for AI feature boundaries, and `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` when a draft implies a tool can see or control Google's ranking systems.

### Escalation Triggers For Human Review

Escalate any claim that promises rankings, traffic, AI citation, recovery, medical outcome, financial result, legal safety, or automatic compliance. Send sensitive claims to [[YMYL Tone Guardrails]], source disputes to [[Research Pack Index]], and channel exaggeration to [[Distribution Voice Adaptation]].

## Banned Claims And Phrases Blocklist Table

| Constraint | Banned variant | Allowed variant | Scope | Owner | Next action |
|---|---|---|---|---|---|
| Ranking certainty | "guarantees page one" | "may improve eligibility or clarity" | SEO recommendations | SEO lead | Replace with evidence-limited wording |
| AI visibility promise | "gets cited by AI" | "prepares passages for review" | GEO and AEO claims | GEO reviewer | Link to [[AI Citation Mechanics]] |
| Tool authority | "the tool proves Google's view" | "the tool reports its observed data" | Vendor metrics | Analyst | Add first-party data caveat |
| Deprecated tactic | "add this for rich results" when support is absent | "visible content may still help readers" | Schema or SERP features | Technical SEO | Verify through [[Blog Schema Stack]] |
| AI file myth | "upload llms.txt for Google AI" | "Google documents no llms.txt use" | AI Search setup | GEO reviewer | Cite `g-ai-opt-guide` before publishing |
| Vendor certainty | "our audit sees Google's ranking system" | "our audit observes external signals" | Tool-led reports | Analyst | Add `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` |
| FAQ rich result promise | "FAQ schema wins rich results" | "visible Q and A can help readers" | FAQ sections | Schema reviewer | Check `g-faqpage-sd` and current schema notes |

### Constraint, Replacement, Banned Variant, And Scope

Editors should record the exact blocked phrase, the safer replacement, the source ID supporting the block, and the affected template or cluster. A rewrite is not enough if the article still implies the banned claim through headings, CTAs, charts, or examples.

## Schema Promise Rewrite Case

Draft line: "Add FAQ schema so Google shows a rich result and AI quotes the answer."

Block reason: current Google guidance does not support that rich-result promise or AI-citation guarantee, using `g-faqpage-sd` and `g-ai-opt-guide`.

Allowed line: "Keep useful Q and A visible for readers, and treat schema as a structured-data check only when documentation supports it."

The editor also removes a CTA saying "win AI visibility," because the same unsupported promise appears outside the paragraph.

The factchecker records the blocked claim in [[Factcheck Claim Register]] rather than leaving it as style feedback.

If a vendor screenshot started the claim, the note adds the tool-authority caveat from `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`.

## Stoplist Failure Patterns

- A banned promise survives in the title after body copy is corrected.
- A chart label turns an advisory score into a guaranteed outcome.
- A replacement phrase softens the wording but keeps the same unsupported causal claim.
- A historical tactic remains in a template after the source document changes.
- Legal, medical, or finance caveats are removed because the hook needs fewer characters.
- A source ID appears near the claim but supports a narrower statement than the copy makes.

## Deliverable Wiring

Primary consumer: [[Factcheck Claim Register]].

Inputs supplied: blocked phrase, safer replacement, source ID, affected asset, owner, and rollback trigger.

Output expected back: verdict label, confidence, refresh date, and whether the draft may proceed.

Drafting consumer: [[Blog Write Article Contract]] uses this stoplist for intros, CTAs, headings, and recommendation copy.

## Banned Claims And Phrases Drift Audit

Review this stoplist monthly and after Google documentation changes. If a phrase is blocked only because the brain lacks evidence, label it "unsupported" rather than "false" until [[Research Pack Index]] closes the gap.
