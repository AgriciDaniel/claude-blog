# Blog Write: Drafting Reference

Detail moved out of `blog-write/SKILL.md` to keep the entrypoint short. Load it
when drafting. Markers shown here (`[INTERNAL-LINK: ...]`, `[IMAGE: ...]`,
`[CHART: ...]`) are draft-only: the orchestrator resolves every one before the
render (step 2 of the canonical delivery sequence), and the delivery gates block
any marker that remains.

## Outline skeleton (Phase 3)

Create a structured outline before writing. If a template was loaded in Phase 1.5,
adapt this skeleton to match the template's section structure:

```
# [Title as Question - Include Primary Keyword]

## Introduction (100-150 words)
- Open with the reader's problem, a useful finding, a concrete example, or an
  optional verified statistic when evidence makes that the strongest hook
- Problem/opportunity statement
- What the reader will learn

> **Key Takeaways**
> - [Core finding with statistic and source]
> - [Second key insight or recommendation]
> - [Third actionable takeaway]
> (Concise bullets sized to the material when a summary helps this content type)

## H2: [Intent-Matched Heading]
- Clear section point with verified support where needed
- Supporting evidence
- [Image placement]
- Practical advice
- [EVIDENCE-BACKED EXPLANATION placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- [Chart: type + data description]
- Analysis and implications
- [EVIDENCE-BACKED EXPLANATION placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- Real-world example or case study
- [Image placement]
- [EVIDENCE-BACKED EXPLANATION placeholder]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- [Chart: type + data description]
- Step-by-step guidance
- [EVIDENCE-BACKED EXPLANATION placeholder]
- [INTERNAL-LINK: anchor text → target description]

## H2: [Intent-Matched Heading]
- Answer-first paragraph
- Forward-looking analysis

## [CTA Section or Inline Placement]
- See `${CLAUDE_SKILL_DIR}/../blog/references/cta-placement.md` for placement rules by content type
- Place CTA after value delivery, not at arbitrary positions
- Single focused CTA per post (a focused CTA is a design choice, not a measured uplift)
- [CTA: contextual call-to-action matching article topic]

## Optional FAQ Section (only when real reader questions warrant it)
- [INTERNAL-LINK: anchor text → detailed content]

## Conclusion (100-150 words)
- Key takeaways (bulleted)
- Call to action
- [INTERNAL-LINK: anchor text → next logical content]
```

Present the outline to the user for approval before writing.


## 5d. Information Gain Markers

Use information-gain markers as optional drafting annotations when the article
contains genuinely original data, transparent first-hand evidence, or
distinctive sourced synthesis. The evidence itself helps readers; the marker is
not a search-engine signal and earns no points by its presence.

Tag each with a comment or visible marker:

- `[ORIGINAL DATA]` - Proprietary surveys, experiments, A/B test results, case
  study metrics the author collected first-hand
- `[PERSONAL EXPERIENCE]` - First-hand observations, lessons learned from direct
  involvement, "when we tried X, Y happened" narratives
- `[UNIQUE INSIGHT]` - Analysis others haven't made, contrarian perspectives
  backed by data, novel connections between existing research

Placement:
- Weave into the body text naturally
- Use as inline comments: `<!-- [ORIGINAL DATA] -->` before the relevant paragraph
- Or as visible callouts if the format supports it:
  ```markdown
  > **Our finding:** [original observation backed by specific data]
  ```
- Use only as many as the supported original material warrants.

## 5e. Evidence-Backed Explanations

For important reusable claims, create a self-contained, evidence-backed
explanation sized to the material.

Guidance:
- Self-contained and understandable in isolation
- Contains a specific claim plus verified support when the claim needs it
- Written in a declarative, quotable style
- Placed within the H2 section body (not as a separate block)

Example:
```markdown
[Verified source title], a [method or sample description] published on [date],
found [specific metric] for [audience or market] ([Source name](https://example.com/full-report),
retrieved YYYY-MM-DD). In practical terms, connect the evidence to one action
the reader should take before making a claim or changing a workflow.
```

Do not pad explanations to a fixed length or add them solely to earn readiness
points.

## 5f. Internal Linking Zones

Mark internal linking opportunities throughout the article using placeholder
notation. The user (or a follow-up pass) will resolve these to actual URLs.

Zone placement:
- **Introduction** - Link to related pillar content or topic hub
- **Each H2 section** - Link to supporting articles, deeper dives, related tools
- **FAQ section** - Link answers to detailed content that expands on the answer
- **Conclusion** - Link to the next logical piece of content the reader should consume

Format:
```markdown
[INTERNAL-LINK: anchor text → target description]
```

Example:
```markdown
For a deeper dive into keyword clustering, see our
[INTERNAL-LINK: complete guide to keyword clustering → pillar page on keyword research methodology].
```

Target 5-10 internal link zones per 2,000-word post. Use descriptive anchor text
(never "click here" or "read more"). See `${CLAUDE_SKILL_DIR}/../blog/references/internal-linking.md` for
anchor text rules and linking strategy.
