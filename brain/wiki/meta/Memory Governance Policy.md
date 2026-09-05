---
type: policy
title: "Memory Governance Policy"
status: active
created: 2026-08-25
updated: 2026-08-25
tags: [meta, memory, policy]
domain: "Blog Content Brain"
confidence: verified
related:
  - "[[CONVENTIONS]]"
  - "[[hot|Hot]]"
  - "[[log]]"
  - "[[Corpus Scope Policy]]"
  - "[[Provenance Trace Policy]]"
  - "[[Evidence Gap Register]]"
  - "[[Context Compaction Routine]]"
  - "[[Uncertainty Eval Policy]]"
source_urls:
  - "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
---

# Memory Governance Policy

## Purpose

Memory in this Brain is a maintained knowledge surface. It must preserve decisions and evidence without converting a transient observation, an assistant guess, or a stale source into an evergreen rule.

## Operating contract

A durable memory statement must identify its owner, evidence path, review state, and confidence tag. The system may summarize evidence, but it may not manufacture missing decisions. [[hot|Hot]] is current working state, [[log]] is append-only history, and evergreen notes are reviewed operating knowledge.

## Memory classes

| Class | Lifetime | Required proof | Mutation rule |
|---|---|---|---|
| Session observation | Current task | Direct local evidence | Do not promote automatically |
| Working hypothesis | Until tested | Named uncertainty | Keep advisory |
| User decision | Until superseded | Explicit decision record | Preserve wording and scope |
| Source-backed fact | Through refresh date | Ledger ID and review | Recheck on drift |
| Operating rule | Until contract changes | Policy or test | Update with rationale |
| Incident record | Historical | Timestamped evidence | Append correction, do not erase |
| External status | Short-lived | Current primary source | Include retrieval date |
| Preference | Until changed | Direct user statement | Avoid broad inference |

## Promotion gate

1. Identify the candidate statement.
2. Separate fact, inference, suspicion, and decision.
3. Locate direct evidence.
4. Check for a conflicting later record.
5. Assign an owner and confidence tag.
6. Choose a destination note.
7. Add provenance links.
8. Record the change in [[log]].
9. Update [[hot|Hot]] only if it affects current work.
10. Schedule review when the evidence is volatile.

## Prohibited promotions

- A tool result presented as user intent.
- A pull request description presented as implemented behavior.
- A passing static test presented as browser or production proof.
- A third-party statistic generalized to every site.
- A stale page presented as current guidance.
- An assistant recommendation presented as an owner decision.
- A failed experiment omitted from history.
- A secret or personal identifier retained for convenience.

## Correction rule

Correct an inaccurate evergreen note in place, preserve the reason in [[log]], and link the superseding evidence. Do not preserve false information merely because earlier work relied on it. Do not rewrite historical incident text unless the correction is clearly labeled.

## Compaction

Use [[Context Compaction Routine]] when task context becomes too large. The compacted handoff must retain scope, completed evidence, unresolved blockers, changed files, verification state, and authorization boundaries. It must not claim a skipped gate passed.

## Audit questions

Can every durable statement be traced? Is its confidence tag still defensible? Does a later source refute it? Is temporary work leaking into evergreen memory? Are external facts dated? Are user decisions distinguishable from recommendations?
## Memory review record

For every promoted memory, record the previous statement, new statement,
evidence, owner, confidence tag, review date, and supersession condition.

| Drift signal | Response |
|---|---|
| Source updated | Recheck claim |
| User decision changed | Supersede rule |
| Test behavior changed | Re-run contract |
| Product renamed | Repair references |
| External status expired | Lower confidence |
| Contradiction found | Preserve conflict |

A memory review closes only when downstream notes no longer repeat the outdated
statement. Search the full corpus before calling a correction complete.
