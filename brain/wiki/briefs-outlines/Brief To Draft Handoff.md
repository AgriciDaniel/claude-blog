---
type: spoke
title: "Brief To Draft Handoff"
domain: "Blog Briefs"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [briefs-outlines, serp-briefs, active]
---

# Brief To Draft Handoff

## Brief To Draft Handoff Control Point

This note turns a completed brief into drafting instructions. It is the transfer layer between planning and writing: the drafter receives the reader job, approved outline, mandatory evidence, caveats, voice constraints, internal links, and rejection conditions. The handoff should be specific enough that the first draft does not invent sources or smooth away uncertainty.

Use [[Brief Source Pack]] for approved evidence, [[Brief Risk Notes]] for unresolved warnings, and [[Heading Hierarchy Rules]] for outline shape. Source IDs travel with the claims. `gh-flow-framework` supports disciplined handoff between evidence, instructions, and output. `g-helpful-content` anchors useful original value, `g-ai-opt-guide` keeps AI-facing wording inside Google's Search guidance, and `nng-editorial-heuristics` supports clear reviewer feedback for the drafter.

### What The Drafter Receives

The drafter receives approved claims, answer targets, section roles, examples to avoid, required caveats, and source IDs. They do not receive permission to add new factual claims without routing them back to the evidence gate.

### What Stays With Reviewer

Approval calls, YMYL sensitivity, first-party data gaps, and confidence labels remain with the reviewer until the draft is ready for QA. If a risk is still open, the handoff must say whether writing can proceed with a caveat or must pause.

## Constraint Transfer Table

| Handoff field | Owner | Required source or note | Writer instruction | Stop condition |
| --- | --- | --- | --- | --- |
| Reader job | brief owner | [[Reader Job Statement]] | Open with the reader problem, not an SEO abstraction | Missing success condition |
| Approved evidence | source steward | [[Brief Source Pack]] plus source IDs | Cite only the supplied claim-source pairs | Source ID absent from a factual claim |
| AI feature wording | SEO lead | `g-ai-opt-guide`; dated llms.txt clarification | Say "eligible to be understood and previewed", not "guaranteed to appear" | AI inclusion promise |
| Click context | analyst | Source from [[Brief Source Pack]]; [[Dual Optimization]] | Keep market data caveated and separate from property metrics | Market average used as site forecast |
| Quality bar | editor | `g-helpful-content` | Add original value and satisfy the named reader task | Thin summary of existing SERPs |
| Risk caveats | approver | [[Brief Risk Notes]] | Preserve caveat text until reviewer removes it | Caveat deleted without approval |
| Internal-link duty | strategist | Approved topic map or [[Semantic Topic Clusters]] | Place links where they extend the reader's next task | Link list added without context |
| Freshness instruction | source steward | [[Brief Source Pack]] refresh cue | Keep dated guidance near time-sensitive claims | Current claim lacks date basis |
| Prohibited claim list | editor | [[Evidence Block Requirements]] verdicts | Name claims the writer must not revive | Removed claim reappears in draft |

## Handoff Procedure

1. Confirm [[Outline QA Checklist]] has no blocker rows open.
2. Paste the reader job, approved H2/H3 outline, required claims, and source IDs into the draft request.
3. Add the caveats that cannot be softened, especially around AI features, zero-click context, and missing property data.
4. Assign a reviewer for any claim marked advisory, contested, or practitioner.
5. Reject the draft request if it asks the writer to infer facts from competitor pages or live SERP appearance.

## Rejection Conditions

Do not send the brief to drafting when the source pack is generic, when a heading asks for unsupported advice, when the reader job is only a keyword phrase, or when the requested angle would overstate AI citation control. Send those issues back to [[Search Intent Classification]], [[Evidence Block Requirements]], or [[Brief Risk Notes]].

## Handoff Repair Scenario

A draft request says: "Write a post that gets cited by AI Mode and include the latest zero-click numbers." The handoff blocks that wording because Google AI inclusion cannot be promised, and market behavior must remain contextual. Source IDs: `g-ai-opt-guide`, `sparktoro-zero-click-2026`.

The repaired request gives the writer an answer-first intro, three approved claims, two internal-link zones, and a caveat saying AI-facing sections describe passage clarity and preview eligibility only. The writer also receives a "do not add" list for llms.txt and tool-score guarantees. Source IDs: `g-helpful-content`, `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search`, `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice`.

## Handoff Failure Points

- The writer gets section titles but no section job. Source ID: `nng-editorial-heuristics`.
- A caveat is placed in comments instead of the task body. Source ID: `gh-flow-framework`.
- New statistics appear after the source pack is frozen. Source ID: `g-helpful-content`.
- Internal links arrive as SEO targets, not reader continuations. Source ID: `g-helpful-content`.

## Draft Contract Wiring

[[Blog Write Article Contract]] consumes the final handoff packet. Inputs provided: reader job, frozen outline, approved claim-source pairs, caveats, internal-link intent, voice constraints, and stop conditions. Expected output: a draft package with source IDs beside current claims and owner-routed blockers.

[[SERP Outline Output Contract]] supplies the hierarchy into this note. Expected output: no writer task begins until duplicate section jobs, unsupported evidence slots, and unresolved risks are named.

## Sources

- `gh-flow-framework`
- `g-helpful-content`
- `g-ai-opt-guide`
- `nng-editorial-heuristics`
- `g-update-2026-06-15-llms-txt-clarified-as-unused-by-google-search` for prohibited writer instructions
- `g-update-2026-06-05-guidance-on-third-party-seo-tools-services-and-advice` for handoff caveats about tools
- `sparktoro-zero-click-2026`
