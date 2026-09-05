---
type: deliverable
title: "SERP Outline Output Contract"
domain: "Blog Briefs"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, serp-outline, outline-contract, active]
---

# SERP Outline Output Contract

## Lightweight Outline Boundary

The SERP outline is the bridge between an approved brief and a draft. It must return an H2/H3 hierarchy, section jobs, rough word-count bands, internal-link zones, and evidence placement. It is lighter than a content brief and stricter than a brainstorm because every section has a job. Source interpretation routes through [[SERP-Informed Briefs and Outlines]].

### Inputs Unique To Outline Mode

The outline needs the approved reader job, primary intent, required claims, internal-link candidates, article type, and any must-avoid claims. `g-helpful-content` supports the direct usefulness requirement, and `g-qrg-full` is used when outline sections need trust or reputation checks.

### Decisions The Outline Must Not Decide

The outline must not add new statistics, promise AI citation, or resolve disputed market context. `sparktoro-zero-click-2026` may justify an answer-first structure only as market context, while `g-ai-opt-guide` keeps AI notes inside Google's stated Search guidance and [[AI Citation Mechanics]] handles caveats.

## Section Job Hierarchy

Each H2 should carry one reader task and one editorial job: answer, compare, demonstrate, caveat, or convert. H3s should unpack that job without creating filler subsections. Internal links belong in sections where they help the reader continue a task.

## SERP Outline Output Contract Acceptance Table

| Outline element | Required value | Check performed | Ready state | Blocker example |
|---|---|---|---|---|
| H1 and intro job | Target query and direct answer promise | Compare to approved brief | H1 matches intent without stuffing | H1 changes the topic |
| H2 sequence | Ordered section jobs | Review reader flow | Each H2 has a distinct task | Two H2s serve the same purpose |
| H3 support | Subtasks and examples | Scan for filler | H3s deepen a parent section | Generic FAQs added for length |
| Word-count band | Range per major section | Compare to answer complexity | Long sections have evidence need | Word count is arbitrary |
| Internal-link zone | Target page and anchor reason | Check topic map | Link supports next reader action | Link is promotional only |
| Evidence slot | Source ID and claim type | Researcher review | Claim can be sourced in draft | Claim lacks approved source |

## Handoff Path To Drafting

1. Freeze the outline after duplicate section jobs are removed.
2. Place source IDs beside the sections where they will be used.
3. Mark any unresolved source or internal-link gap before the writer starts.

## Source IDs Used

Outline work cites `g-helpful-content`, `g-ai-opt-guide`, `g-qrg-full`, and `sparktoro-zero-click-2026`.
