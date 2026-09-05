# Template: How-To Guide

**Template Name:** How-To Guide (Step-by-Step Tutorial)
**Target Word Count:** 2,000-2,500 words
**Description:** A structured, actionable tutorial that walks readers through a specific process from start to finish. Each step is concrete, visual, and builds on the previous one. Designed to rank for "how to" queries and earn featured snippets.

## When to Use This Template

- **Content Goals:** Drive organic traffic from instructional queries, establish topical authority, earn featured snippets for step-based queries
- **Search Intent:** Informational / Transactional hybrid: the reader has a specific problem and wants a clear solution *right now*
- **Best For:** Process explanations, software tutorials, setup guides, configuration walkthroughs, skill-building content
- **Avoid When:** The topic lacks a clear sequential process or has fewer than 3 meaningful steps

---

## Section-by-Section Structure

---

### Title (H1)

**Format:** "How to [Achieve X]: A [Year] Step-by-Step Guide"

**Examples:**
- "How to Set Up a CI/CD Pipeline: A 2026 Step-by-Step Guide"
- "How to Migrate from WordPress to Next.js: A 2026 Step-by-Step Guide"

**Rules:**
- Include the primary keyword naturally
- Include the year for freshness signals
- Keep under 60 characters if possible

---

### Introduction (150-200 words)

[ANSWER-FIRST] Open with the single most compelling statistic or fact that validates *why* this process matters. Not a vague claim: a specific number.

**Structure:**
1. **Problem statement** (1-2 sentences): What pain point does the reader have?
2. **Agitation** (1-2 sentences): What happens if they don't solve it? What's the cost of inaction?
3. **Promise** (1 sentence): What will they be able to do after following this guide?
4. **Credibility anchor** (1 sentence): Why should they trust this guide specifically?

[STAT: Industry statistic that quantifies the problem this guide solves]

[INFO-GAIN: personal experience] Include an anecdote only when the author
supplies what happened, the context, and supporting evidence. Otherwise use a
sourced problem example without first-person framing.

**Example opening:**
> "[VERIFIED PROBLEM EVIDENCE]. This guide explains [PROCESS] for [AUDIENCE]
> and shows how to verify [SUCCESS CONDITION]. Add first-hand results only when
> the author supplies the methodology, evidence, and outcome."

[INTERNAL-LINK] Link to a related foundational concept post (e.g., "If you're new to [topic], start with our [Beginner's Guide to X]").

---

### Prerequisites / Before You Begin (100-150 words)

**Format:** Bulleted checklist under an H2 heading.

**Include:**
- Required tools/software (with versions)
- Required accounts or access
- Assumed knowledge level (be specific: "You should be comfortable with [X]")
- Estimated time to complete
- Difficulty level (Beginner / Intermediate / Advanced)

[IMAGE] Screenshot or diagram showing the tools/environment the reader should have ready before starting.

**Example:**
> **What you'll need:**
> - Current active LTS version of Node.js installed ([how to install](/link))
> - A GitHub account with repo access
> - Basic familiarity with the terminal
> - **Time:** ~45 minutes
> - **Difficulty:** Intermediate

---

### Step 1: [Action Verb] + [Specific Object] (200-300 words)

[ANSWER-FIRST] Open with what the reader will have accomplished by the end of this step: the micro-outcome.

**Structure for EVERY step section:**
1. **Micro-outcome statement** (1 sentence): "By the end of this step, you'll have [specific result]."
2. **Context** (1-2 sentences): Why this step matters in the overall process.
3. **Instructions** (numbered sub-steps): Concrete actions. Use code blocks, exact UI paths, or specific settings.
4. **Verification** (1-2 sentences): How the reader confirms this step worked.

[IMAGE] Screenshot showing the expected state after completing this step.

[INFO-GAIN: specific configuration or setting] Share a verified non-obvious
detail from supplied evidence or a cited source. Do not invent undocumented
behavior.

**Formatting rules:**
- Use H2 for the step heading: `## Step 1: Install and Configure the CLI`
- Use numbered sub-lists for individual actions within the step
- Use code blocks for any commands, file contents, or configuration
- Bold the single most important instruction in each step

---

### Step 2: [Action Verb] + [Specific Object] (200-300 words)

[Follow the same structure as Step 1]

[IMAGE] Screenshot of expected state after this step.

[STAT: Performance or efficiency metric related to this step, if applicable]

---

### Step 3: [Action Verb] + [Specific Object] (200-300 words)

[Follow the same structure as Step 1]

[IMAGE] Screenshot of expected state after this step.

[VISUAL: flowchart] If the process branches or has decision points at this stage, include a flowchart showing the paths.

---

### Step 4: [Action Verb] + [Specific Object] (200-300 words)

[Follow the same structure as Step 1]

[IMAGE] Screenshot of expected state after this step.

[INFO-GAIN: troubleshooting tip] Use a supplied first-hand problem and solution
only when evidence is available; otherwise provide a sourced troubleshooting
case without personal framing.

---

### Step 5: [Action Verb] + [Specific Object] (200-300 words)

[Follow the same structure as Step 1]

[IMAGE] Screenshot of expected state after this step.

---

### Step 6: [Action Verb] + [Specific Object] (200-300 words)

[Follow the same structure as Step 1]

[IMAGE] Screenshot showing the final completed state.

[VISUAL: before-after] Side-by-side comparison showing before (Step 1) and after (Step 6) state.

**Note:** Not every guide needs exactly 6 steps. Use 4-8 steps depending on the complexity of the process. Each step should represent a meaningful, testable milestone: not a trivial action.

---

### Common Mistakes to Avoid (150-200 words)

[ANSWER-FIRST] Open with a verified frequent mistake and its consequence. Use a
statistic only when supplied by a source that supports the specific claim.

**Format:** 3-5 mistakes, each as a bolded sub-heading with 2-3 sentences of explanation.

**Structure for each mistake:**
1. **The mistake** (bold): What people do wrong
2. **Why it happens** (1 sentence): The underlying cause or misconception
3. **The fix** (1 sentence): What to do instead

[INFO-GAIN: original observation] Include a direct-experience mistake only
when the author supplies the context, evidence, and result. Otherwise use a
verified source or omit the marker.

[STAT: Failure rate or error frequency for the most common mistake]

**Example:**
> **1. Skipping environment variable validation**
> [VERIFIED DESCRIPTION OF THE FAILURE MODE]. Explain the validation step and
> expected result using the actual environment and source evidence. Do not add a
> percentage or "in our experience" claim unless supplied and documented.

---

### Results / What Success Looks Like (100-150 words)

[ANSWER-FIRST] Open with the specific, measurable outcome: "If everything went correctly, you should now see [X]."

**Include:**
- What the reader should see/have now (concrete, verifiable)
- Key metrics that indicate success (load time, response code, test pass rate, etc.)
- One "stretch goal" or next-level enhancement they can pursue

[IMAGE] Screenshot of the final successful result.

[VISUAL: metrics-dashboard] If applicable, show a performance or status dashboard screenshot.

[INTERNAL-LINK] Link to an advanced guide or next-step post: "Now that you've set up [X], learn how to [optimize/scale/extend it]."

---

### Optional Reader Questions (count by reader need)

[FAQ: Include this section only when genuine reader questions add material not
already covered by the steps.]

**Format:** Each question as an H3 with a complete, direct answer. Let
complexity determine answer length.

**Question selection criteria:** Use only questions supported by reader
research, such as a meaningful alternative, unresolved troubleshooting case,
scaling concern, cost, time, or prerequisite.

[STAT when useful: include a verified statistic only when it materially
improves an answer.]

**Example:**

#### How long does it take to set up a CI/CD pipeline?

[2-4 sentence answer with a specific time range and what variables affect it.]

#### Can I use [Alternative Tool] instead?

[2-4 sentence answer comparing the alternative, with a clear recommendation.]

#### What should I do if Step [N] fails?

[2-4 sentence answer with specific troubleshooting steps.]

#### How do I scale this for a larger team?

[2-4 sentence answer with concrete next steps.]

#### Is [Tool/Service] free?

[2-4 sentence answer with pricing details and free tier limitations.]

---

### Conclusion with CTA (50-100 words)

**Structure:**
1. **Recap** (1 sentence): Summarize what they accomplished.
2. **Reinforce value** (1 sentence): Restate the benefit with the key metric.
3. **CTA** (1-2 sentences): Clear next action: share the post, subscribe, try a related guide, leave a comment with their results.

[INTERNAL-LINK] Link to 2-3 related posts for continued reading.

---

## Template Checklist

Before publishing, verify:

- [ ] Title includes primary keyword and current year
- [ ] Introduction establishes the reader task; any statistic is material and verified
- [ ] Every step has a clear micro-outcome, numbered sub-steps, and verification
- [ ] Every step has a supporting screenshot or visual
- [ ] Any [INFO-GAIN] elements contain supported original experience or data
- [ ] Any [STAT] markers are filled with material, verified statistics
- [ ] Any original observations include supplied methodology, evidence, and results
- [ ] Optional FAQ answers genuine reader questions directly
- [ ] All [INTERNAL-LINK] zones have contextual links to related content
- [ ] Length is sufficient for the task without padding; planning ranges are optional
- [ ] All code blocks are syntax-highlighted and tested
- [ ] Meta description is accurate, page-specific, and consistent with visible content
