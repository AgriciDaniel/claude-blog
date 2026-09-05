---
name: blog-style
description: Learn author writing style from 5 to 10 existing blog posts and generate a voice profile for /blog style learn, VOICE.md, blog-persona, and blog-write when users ask to infer tone, analyze author voice, learn style, or build a writing baseline.
argument-hint: "learn <paths>"
user-invokable: true
license: MIT
---

# Blog Style - Writing Style Learning

Learn an author voice profile from existing posts, then use it as a baseline for
VOICE.md, blog-persona, and blog-write. The profile captures measurable style
signals so future drafts can preserve the author's cadence, vocabulary, and
tone.

## Commands

| Command | Purpose |
|---------|---------|
| `/blog style learn <paths>` | Analyze sample posts and generate a voice profile |

## Learn Workflow

Use 5 to 10 representative posts from the same author, brand, or editorial
voice. Accept individual markdown files, MDX files, text files, or a directory
containing posts.

Run the local learner:

```bash
python3 scripts/style_learn.py <paths> --format markdown
```

For machine-readable output:

```bash
python3 scripts/style_learn.py <paths> --format json --output voice-profile.json
```

For a VOICE.md-ready block:

```bash
python3 scripts/style_learn.py <paths> --format markdown --output VOICE.md
```

If fewer than the requested minimum sample count is supplied, warn and continue.
The default minimum is 5 posts.

## Profile Fields

The learner aggregates the existing blog analyzer across each sample post:

- Sentence length mean and median
- Sentence length burstiness as corpus variance
- Vocabulary richness as type-token ratio
- Transition-word sentence rate
- Passive-voice sentence rate
- AI trigger words per 1,000 words as a baseline to preserve or avoid
- Paragraph-length distribution
- First-person usage rate
- Heading-as-question ratio
- Signature phrases from top 2-gram and 3-gram content phrases with stopwords removed
- Tone descriptors derived from the measured metrics

## Consuming the Profile

Drop the markdown block into project `VOICE.md` when the goal is durable
project context. Blog-write can use the style baselines as drafting targets:

- Keep average sentence length near the learned mean.
- Match the learned sentence variation unless the user asks for a tighter or
  looser cadence.
- Preserve signature phrases only when they fit the topic naturally.
- Treat the AI trigger baseline as a ceiling when the author rarely uses those
  terms.
- Use the first-person and heading-question rates to decide how personal and
  question-led the draft should feel.

Feed the JSON output into blog-persona when a structured persona should be
created or updated. Map the learned values to persona sentence length, passive
voice, readability, vocabulary, and tone settings.

## Error Handling

- **Too few posts**: Continue and warn that the profile may be less stable.
- **Missing paths**: Skip missing paths and include a warning in the profile.
- **Unsupported files**: Skip unsupported file types and include a warning.
- **Empty samples**: Return zeroed metrics rather than crashing.
