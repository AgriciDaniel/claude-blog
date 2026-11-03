# Gemini TTS Models: Dated Facts

Checked 2026-10-12 against Google's pricing, speech-generation and deprecations
pages. Re-read those pages before quoting a number, and update this file when
they change. `SKILL.md` keeps only the consent rules and commands.

## Models

| Alias | Model ID | Languages | Notes |
|-------|----------|-----------|-------|
| `flash38` | `gemini-3.8-flash-tts` | over 130 | Stable general-purpose model; default for new work |
| `flash-lite38` | `gemini-3.8-flash-lite-tts` | over 100 | Cheaper stable model; a few languages (for example Finnish and Thai) are Flash-only |

## Pricing (audio output, 25 tokens per second of audio)

Source: https://ai.google.dev/gemini-api/docs/pricing

| Model | Rate through 2026-12-31 | About per 10 seconds |
|-------|-------------------------|----------------------|
| `gemini-3.8-flash-tts` | $9.00 per 1M audio tokens | $0.00225 |
| `gemini-3.8-flash-lite-tts` | $6.00 per 1M audio tokens | $0.0015 |

Higher rates are listed from 2027-01-01. The script's cost estimate uses the
reviewed 2026 rates through December 31 and the published 2027 rates from
January 1. It is an estimate, not a billing quote.

## Legacy aliases

`flash`, `flash31`, `pro`, `legacy-flash25` and `legacy-pro25` map to
`gemini-3.1-flash-tts-preview`, `gemini-2.5-pro-preview-tts` and
`gemini-2.5-flash-preview-tts`. Google's deprecations page lists their earliest
shutdown as 2026-11-17. Do not use them for new work.
