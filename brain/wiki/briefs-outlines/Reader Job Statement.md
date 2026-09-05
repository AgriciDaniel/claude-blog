---
type: spoke
title: "Reader Job Statement"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Reader Job Statement

## Reader Job Statement Definition Job

This note turns a query set into a specific reader task, success condition, and decision context. It is the brief's first control point because every later choice, from heading order to evidence density, should serve the person using the article. A good reader job is concrete: it names what the reader is trying to decide, what they already know, what risk they are managing, and what the article must help them do next.

`g-helpful-content` supports framing the article around a real person and task. `nng-editorial-heuristics` supports observable success conditions and review ergonomics. When the journey includes Google AI surfaces, use `g-ai-features` to describe eligibility boundaries. If click behavior affects the success condition, cite `sparktoro-zero-click-2026` as market context and route interpretation to [[Dual Optimization]].

### Query To Task Translation

Translate "best CRM blog examples" into a decision such as "content lead needs to choose a repeatable format for a SaaS comparison article." Avoid restating the keyword as the job.

### Success Condition Wording

The success condition should be observable: choose, compare, diagnose, implement, refresh, brief, or escalate. Vague goals such as "rank better" or "be GEO optimized" are not reader jobs.

## Reader Job Planning Table

| Field | Required evidence | Owner | Confidence cue | Next action |
| --- | --- | --- | --- | --- |
| Primary reader | Query set, audience brief, or persona note | brief owner | High when persona and query agree | Write one reader sentence |
| Decision or task | SERP observation plus product or editorial context | strategist | Medium until validated by stakeholder | Pick one main verb |
| Must-know constraints | Source pack and risk notes | source steward | Low if current sources are missing | Add caveat or blocker |
| AI answer exposure | `g-ai-features` and [[AI Citation Mechanics]] | SEO lead | Advisory unless property data exists | State eligibility boundary |
| Click or visit expectation | `sparktoro-zero-click-2026` plus first-party data when available | analyst | Practitioner if market-only | Separate visibility from traffic |
| Usefulness test | `g-helpful-content` | editor | High when article adds original value | Add information-gain requirement |
| Existing knowledge | Persona note, sales notes, or query modifiers | strategist | Medium until supported by evidence | Name what the reader already knows |
| Decision risk | [[Brief Risk Notes]] and source sensitivity | editor | Low when owner is missing | Add approval or caveat |
| Next action | Product, process, or editorial workflow context | brief owner | High when action is observable | Pick one outcome verb |

## Acceptance Procedure For The Statement

1. Write the reader job as "A [reader] needs to [task] so they can [decision or outcome]."
2. Name the query surface and any AI or zero-click caveat without turning it into the goal.
3. Add the evidence source that justifies the task and mark weak evidence as advisory.
4. Check that every proposed H2 would help the reader complete the stated task.
5. Reject the statement if it could fit any article in the cluster without changing a word.

## Reader Job Conversion Example

Keyword: "AI blog outline tool." Weak job: "Readers want an AI blog outline tool." Stronger job: "A content strategist needs to compare outline tools so they can choose whether to automate brief drafting or keep manual evidence review." Source IDs: `g-helpful-content`, `nng-editorial-heuristics`.

The AI surface caveat stays outside the job sentence: the article may discuss AI answer exposure, but the reader's task is tool selection and evidence control. Source IDs: `g-ai-features`, `g-ai-opt-guide`.

## Job Statement Failure Modes

- The "reader" is a keyword segment, not a person with a task. Source ID: `g-helpful-content`.
- Two audiences require different outcomes inside one sentence. Source ID: `nng-editorial-heuristics`.
- The success condition says "rank" instead of choose, compare, diagnose, or implement. Source ID: `g-helpful-content`.
- AI citation exposure becomes the reader's goal rather than a channel caveat. Source ID: `g-ai-features`.

## Brief Consumer Wiring

[[Content Brief Output Contract]] consumes the approved reader job. Inputs provided: reader, task verb, decision outcome, query surface, caveat, and confidence cue. Expected output: the brief's audience and article promise match that job.

[[SERP Outline Output Contract]] consumes the same job for the H1 and intro check. Expected output: every H2 supports the job rather than adding generic topical coverage.

## Sources

- `g-helpful-content`
- `nng-editorial-heuristics`
- `g-ai-features`
- `g-ai-opt-guide`
- `sparktoro-zero-click-2026`

## Downstream Use

Send the approved statement to [[Search Intent Classification]] for intent labeling and to [[Heading Hierarchy Rules]] for section design. Keep the sentence in [[Brief To Draft Handoff]] so the writer cannot drift into generic coverage.
