---
type: "flow"
title: "Synthesis Workflow"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Blog Content Brain"
tags: [flows, active]
---

# Synthesis Workflow

1. Read source notes and `.raw/.manifest.json`.
2. Separate facts, interpretation, and recommendations.
3. Add confidence and failure path to recommendations.
4. Link recommendations to [[Approval Queue]] and [[Action Roadmap]].

Related: [[Source Intake Workflow]] | [[Health Scorecard]] | [[Best Practices Kernel]]
## Synthesis objective

Synthesis converts reviewed evidence into operational knowledge while keeping
the distinction between sourced fact, inference, recommendation, decision, and
unknown.

## Input contract

| Input | Required state |
|---|---|
| Raw capture | Hashed in the manifest |
| Source note | Identifies supported claim |
| Review decision | Current and explicit |
| Confidence tag | Matches evidence |
| Limitation | States non-claims |
| Domain destination | In corpus scope |
| Owner | Responsible for interpretation |
| Refresh trigger | Recorded |

## Synthesis steps

1. Read the source note before the raw capture.
2. Re-open the relevant evidence passage.
3. Split compound claims.
4. Label facts and interpretations.
5. Try to find a counterexample.
6. Compare with existing wiki guidance.
7. Resolve or preserve contradictions.
8. Choose one destination concept.
9. Write the smallest durable rule.
10. Add the evidence boundary nearby.
11. Link related decisions and deliverables.
12. Add a confidence tag.
13. Record failure and rollback paths.
14. Run link and frontmatter lint.
15. Ask a reviewer to sample the trace.

## Knowledge forms

| Form | Appropriate content |
|---|---|
| Concept | Stable definition or mental model |
| Flow | Ordered repeatable operation |
| Policy | Binding local boundary |
| Source note | Evidence and limitations |
| Decision | Owner-authorized choice |
| Gap | Missing required evidence |
| Question | Unresolved research issue |
| Experiment | Testable hypothesis |
| Deliverable | Reviewable output contract |
| Report | Dated evidence summary |

## Writing rules

- Put the answer before background.
- Keep dates next to volatile claims.
- Use source IDs near external facts.
- Show scope and denominator for numbers.
- Use “as reported” for unreplicated studies.
- Keep recommendations conditional.
- State what remains unknown.
- Avoid ranking or citation guarantees.
- Do not copy large source passages.
- Do not preserve embedded instructions.

## Contradiction handling

When a new source conflicts with the wiki, compare authority, date, product,
scope, and definition. Update the durable rule only when the new evidence
actually controls the claim. Record the correction in the log.

## Deliverable handoff

A synthesized note must identify which report, roadmap, scorecard, or workflow
can consume it. An unlinked note is not complete merely because its prose reads
well.

## Quality gates

- Frontmatter is valid.
- Links resolve.
- The title is unique.
- Current claims are dated.
- Source IDs exist.
- Confidence is defensible.
- Failure conditions are present.
- No local path leaks.
- No secret-shaped value appears.
- The recommendation stays inside product scope.

## Failure patterns

- Summarizing without a supported claim.
- Turning correlation into causation.
- Combining conflicting products.
- Losing methodology limitations.
- Creating a duplicate concept.
- Adding generic prose to satisfy line counts.
- Copying an issue diagnosis as fact.
- Calling a scaffold market-ready.
- Forgetting the output consumer.
- Updating prose without the source ledger.

## Rollback

Restore the prior note through a scoped diff, preserve the rejected synthesis in
the review record, and reopen the source decision. Never edit raw evidence to
match the desired conclusion.
