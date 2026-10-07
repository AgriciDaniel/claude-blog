# Gemini TTS Voice Catalog

30 prebuilt voices for Google Gemini TTS. All voices support 80+ languages
with automatic language detection.

## Full Voice Table

| Voice | Tone | Best For |
|-------|------|----------|
| Zephyr | Bright | Energetic intros, lifestyle content |
| Puck | Upbeat | Podcast host, casual blogs |
| Charon | Informative | Article narration (default), technical content |
| Kore | Firm | Expert/authority voice, dialogue guest |
| Fenrir | Excitable | Product launches, news highlights |
| Leda | Youthful | Youth-oriented content, tutorials |
| Orus | Firm | Business, formal content |
| Aoede | Breezy | Lifestyle, wellness, travel |
| Callirrhoe | Easy-going | Casual blogs, personal essays |
| Autonoe | Bright | Marketing, upbeat summaries |
| Enceladus | Breathy | Intimate storytelling, ASMR-adjacent |
| Iapetus | Clear | Technical documentation, clarity-first |
| Umbriel | Easy-going | Relaxed tutorials, guides |
| Algieba | Smooth | Professional narration, case studies |
| Despina | Smooth | Polished delivery, executive summaries |
| Erinome | Clear | Educational content, explainers |
| Algenib | Gravelly | Character voice, dramatic reading |
| Rasalgethi | Informative | News analysis, data-driven content |
| Laomedeia | Upbeat | Co-host voice, interview-style |
| Achernar | Soft | Gentle delivery, mindfulness content |
| Alnilam | Firm | Authoritative statements, conclusions |
| Schedar | Even | Neutral delivery, balanced reporting |
| Gacrux | Mature | Thought leadership, industry analysis |
| Pulcherrima | Forward | Direct, opinion pieces |
| Achird | Friendly | How-to guides, tutorials (recommended) |
| Zubenelgenubi | Casual | Conversational blogs, Reddit-style |
| Vindemiatrix | Gentle | Health, wellness, sensitive topics |
| Sadachbia | Lively | Listicles, roundups, energetic content |
| Sadaltager | Knowledgeable | Deep dives, pillar pages |
| Sulafat | Warm | Welcome messages, community content |

## Recommended by Blog Type

| Blog Type | Single Voice | Why |
|-----------|-------------|-----|
| How-to guide | Achird (Friendly) | Approachable, clear instruction delivery |
| Technical tutorial | Iapetus (Clear) | Precision and clarity for code/data |
| News analysis | Rasalgethi (Informative) | Authoritative without being dry |
| Thought leadership | Gacrux (Mature) | Gravitas for opinion and prediction |
| Listicle | Sadachbia (Lively) | Keeps energy up across list items |
| Case study | Algieba (Smooth) | Professional, results-focused delivery |
| Product review | Charon (Informative) | Balanced, trustworthy assessment |
| Pillar page | Sadaltager (Knowledgeable) | Sustained depth over long content |
| Lifestyle/wellness | Aoede (Breezy) | Light, inviting, relaxed pace |
| FAQ/knowledge base | Erinome (Clear) | Direct answers, no filler |

## Dialogue Mode Pairings

Recommended voice combinations for two-speaker podcast/dialogue format:

| Pair | Host | Guest/Expert | Style |
|------|------|-------------|-------|
| **Default** | Puck (Upbeat) | Kore (Firm) | Energetic host + authoritative expert |
| Professional | Achird (Friendly) | Charon (Informative) | Warm interviewer + knowledgeable guest |
| Casual | Zubenelgenubi (Casual) | Callirrhoe (Easy-going) | Relaxed conversation, both laid-back |
| Technical | Laomedeia (Upbeat) | Iapetus (Clear) | Curious host + precise technical expert |
| News | Schedar (Even) | Rasalgethi (Informative) | Neutral anchor + informed analyst |

## Model Support

Google's Gemini TTS supported-model list changes. As of 2026-10-07, use the
current Gemini 3.8 TTS models for new work and preserve older local aliases only
for compatibility:

| Model | ID | Single speaker | Multispeaker | Note |
|-------|----|----------------|--------------|------|
| Gemini 3.8 Flash TTS | `gemini-3.8-flash-tts` | Yes | Yes | Current general-purpose TTS model |
| Gemini 3.8 Flash Lite TTS | `gemini-3.8-flash-lite-tts` | Yes | Yes | Current lower-cost TTS model |
| Gemini 3.1 Flash TTS Preview | `gemini-3.1-flash-tts-preview` | Yes | Yes | Legacy model; migrate new work to 3.8 |
| Gemini 2.5 Flash Preview TTS | `gemini-2.5-flash-preview-tts` | Yes | Yes | Local `legacy-flash25` alias |
| Gemini 2.5 Pro Preview TTS | `gemini-2.5-pro-preview-tts` | Yes | Yes | Local `pro` and `legacy-pro25` aliases |

**Runtime note:** `flash` and `flash31` retain the 3.1 preview mapping.
`flash38` and `flash-lite38` use the Interactions API and validate unary WAV
output before normalizing it for the existing audio pipeline. Dialogue requires
explicit `Speaker1:` and `Speaker2:` labels. Offline SDK and parsing checks do
not establish authenticated model availability or generated voice quality.

## Language Notes

- All 30 voices support 80+ languages via automatic detection
- Pass text in any supported language: no language parameter needed
- Voice characteristics (Bright, Firm, etc.) carry across languages
- For best results with non-English text, test voice-language combinations
- BCP-47 language codes are auto-detected from input text

## Style Control

Gemini TTS does not support SSML. Control style via natural language in the text
and, on 3.1 TTS, supported audio tags:

Natural language controls:
- For emphasis: use naturally emphatic phrasing
- For pauses: use punctuation (periods, ellipses, commas)
- For pace: shorter sentences = faster pace, longer = slower
- For tone: word choice drives delivery (urgent words = urgent delivery)

Audio tag examples for 3.1 TTS:
- `[whispers]` for quiet delivery
- `[laughs]` for a light laugh
- `[sighs]` for a sigh

Keep tags sparse and test the output, because unsupported tags may be spoken
literally by older models.

For 3.8, the transcript is verbatim. Sustained delivery instructions belong in
structured `speech_metadata.style` rather than the transcript. This helper
currently exposes voice and speaker configuration, not a style flag; keep
stage directions out of 3.8 input.
