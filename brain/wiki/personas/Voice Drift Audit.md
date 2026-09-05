---
type: spoke
title: "Voice Drift Audit"
domain: "Blog Voice"
status: active
created: 2026-07-06
updated: 2026-07-09
tags: [personas, voice-style, active]
---

# Voice Drift Audit

## Voice Drift Audit Sampling Job

Voice Drift Audit detects when drafts, clusters, or distributed assets move away from approved voice, persona needs, source discipline, or risk posture. It is a sample-based review, not a rewrite pass. The output is a drift finding with evidence, severity, owner, and rebaseline decision.

### Drift Types This Spoke Owns

Use `g-helpful-content` to test reader usefulness, `g-qrg-full` for trust and topic purpose, `g-update-2025-01-23-qrg-update-jan-2025` for filler, copied, or low-value AI-generated content warnings, and `g-update-2025-09-11-qrg-update-sept-2025` when AI Overview examples or expanded YMYL treatment affect review. `g-spam-policies` helps when drift resembles scaled content abuse rather than ordinary tone variance.

### Human Review For Systemic Drift

Escalate if drift appears across a template, a cluster, a locale, or a distribution channel. A single awkward sentence goes to [[Readability Review]]; repeated overclaiming goes to [[Banned Claims And Phrases]]; riskier tone goes to [[YMYL Tone Guardrails]].

## Voice Drift Audit Signal Table

| Signal | Evidence | Threshold | Owner | Next action |
|---|---|---|---|---|
| Persona mismatch | Draft examples differ from [[Audience Persona Template]] | Two or more sections misfit | Editor | Recut examples and intro |
| Source dilution | Caveats, dates, or source IDs disappear | Any material claim affected | Factchecker | Block until source restored |
| Voice sameness | Multiple posts repeat the same generic phrasing | Cluster sample shows pattern | Content lead | Rebaseline voice samples |
| Low-value scaling | Many pages paraphrase without added reader value | Template or batch signal | SEO lead | Check `g-spam-policies` and pause batch |
| Channel creep | Social or email asset strengthens the article claim | One live asset with material drift | Distribution lead | Recheck [[Distribution Voice Adaptation]] |
| Locale drift | Localized page changes certainty or institution | Any sensitive sentence affected | Locale owner | Reopen [[Locale Voice Adaptation]] |
| Metric inflation | Advisory score becomes performance forecast | Any report or CTA affected | Analyst | Route to [[Banned Claims And Phrases]] |

### Signal, Evidence, Threshold, Owner, And Next Action

The finding should quote or summarize the local problem, identify the controlling note, and name the smallest correction. Do not use drift as a reason to rewrite stable, source-accurate passages just because they are less polished.

## Cluster Sample Audit

Sample: five posts from a schema cluster and three related social assets.

Finding: four posts say "rich-result opportunity" after a source update removed the relevant feature.

Decision: mark source dilution and terminology drift, then pause new derivative assets.

Source basis: `g-spam-policies` covers scaled low-value patterns, while `g-helpful-content` keeps the review focused on reader value.

The audit does not rewrite every sentence; it opens one source-controlled correction path.

If the problem repeats across templates, the owner rebaselines [[Brand Voice Inventory]] before more drafts use the pattern.

If a localized page changed the claim, the finding goes to [[Localization Adaptation Checklist]] with the exact sentence.

## Drift Audit Failure Modes

- The reviewer flags personal taste instead of a source, persona, or risk mismatch.
- Sampling only published articles misses social assets where the stronger claim appears.
- Rebaseline happens before the team agrees that current samples are actually obsolete.
- A low-value batch problem is treated as a single awkward paragraph.
- Locale drift is hidden because translated pages are not included in the sample.
- The audit records severity but not the smallest responsible owner.

## Audit Output Wiring

Primary consumer: [[Style Learning Voice Profile]].

Inputs supplied: drift signal, sample set, quoted issue, severity, controlling note, and rebaseline recommendation.

Output expected back: approved sample change, rejected drift claim, or measurable profile update.

Score consumer: [[Blog Analyzer Score Report]] uses material source or persona drift as advisory findings.

## Voice Drift Audit Rebaseline Check

Rebaseline only after the approved source notes change or after reviewers agree that the current voice inventory no longer fits the audience. Store the new sample in [[Brand Voice Inventory]] before applying it.
