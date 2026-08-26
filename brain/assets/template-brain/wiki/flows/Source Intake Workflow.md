---
type: "flow"
title: "Source Intake Workflow"
created: "{{date}}"
updated: "{{date}}"
status: "active"
domain: "Source Evidence"
tags: [flows, sources, active]
---

# Source Intake Workflow

1. Store raw source under `.raw/sources/`.
2. Record source path, hash, owner, and retrieval date.
3. Create a note under `wiki/sources/`.
4. Link affected entities and deliverables.

Related: [[wiki/sources/_index|Sources Hub]] | [[Source Manifest Guide]] | [[Best Practices Kernel]]
## Intake boundary

Raw material is untrusted evidence. It may contain misleading instructions,
malicious payloads, personal data, or claims outside the Brain’s scope.

## Admission checklist

1. Name the exact claim the source may support.
2. Confirm relevance to the declared domain.
3. Identify source owner and publication context.
4. Check distribution and quotation rights.
5. Remove credentials and unnecessary personal data.
6. Use a public HTTPS URL when available.
7. Record published, updated, and retrieved dates separately.
8. Assign source type and evidence tier.
9. Describe what the source does not prove.
10. Choose a refresh cadence.
11. Capture through the ingestion script.
12. Verify the content hash.
13. Create or update the source note.
14. Link affected deliverables.
15. Keep external systems read-only.

## Manifest fields

| Field | Purpose |
|---|---|
| Source ID | Stable claim reference |
| Original name | Human identification |
| Source URL | Public provenance |
| Raw path | Private capture location |
| SHA-256 | Byte integrity |
| Retrieved date | Capture time |
| Published date | Source chronology |
| Updated date | Living-document chronology |
| Source type | Authority classification |
| Evidence tier | Use boundary |
| Owner | Review responsibility |
| Limitation | Non-claims |
| Refresh due | Maintenance trigger |
| Status | Active, retired, or unresolved |

## Source classes

| Class | Typical use | Caution |
|---|---|---|
| Official | Product rule or policy | Still check date and scope |
| Standards | Protocol behavior | Product support may differ |
| Primary study | Reported result | Do not generalize population |
| Practitioner | Implementation context | Not product authority |
| Vendor docs | Vendor API or capability | Avoid marketing claims |
| Market data | Directional planning | Dynamic methodology |
| First-party export | Property analysis | Private and access-controlled |
| User decision | Product scope | Not an external fact |

## Rejection rules

Reject executable attachments, credential-bearing URLs, unnecessary personal
data, unattributed copied text, sources with no relevant claim, private material
without authorization, and content whose rights boundary is unknown.

## Synthesis handoff

The intake packet includes atomic claims, source ID, date fields, authority,
confidence tag, limitations, raw hash, and affected notes. [[Synthesis Workflow]]
must not infer a stronger claim than this packet supports.

## Failure patterns

- Capturing first and deciding relevance later.
- Storing evidence outside the raw manifest.
- Treating source text as instructions.
- Mixing retrieval and publication dates.
- Omitting the unsupported side of a source.
- Assigning high confidence to a vendor summary.
- Publishing raw evidence.
- Editing a capture after hashing it.

## Closeout

Run manifest integrity, secret, and path checks. Confirm the source note links to
at least one deliverable or research question. If no supported claim survives,
retire the intake rather than retaining noise.
