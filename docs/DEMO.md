# claude-blog v2.2.0: Demo Runbook

End-to-end demo flow that exercises every wired integration: YouTube
embedding (blog-google), keyword research (DataForSEO MCP), AI image
generation (banana / blog-image via nanobanana-mcp), inline SVG charts
(blog-chart), animated SVGs (svg-animate).

> **Security note**: this demo uses the env-expansion + sourceable-
> credentials pattern that closes audit VULN-001/003. `.mcp.json` and
> `.env.local` are both `chmod 0600` and gitignored. Per-skill
> credentials live in `~/.config/claude-seo/google-api.json` (also
> mode 0600). See [SECURITY.md](../.github/SECURITY.md) for the full hardening
> checklist.

---

## Pre-flight (run once per shell session)

The MCP servers in `.mcp.json` reference shell env vars. They are
populated by sourcing the gitignored `.env.local`. Restart Claude Code
after sourcing so the MCP subprocess inherits the values.

```bash
cd ~/claude-blog
source .env.local
echo "GOOGLE_AI_API_KEY length: ${#GOOGLE_AI_API_KEY}"     # should print 39
echo "DATAFORSEO_USERNAME set:  ${DATAFORSEO_USERNAME:+yes}"  # should print yes
# Then restart Claude Code so MCP servers pick up the env
```

For a persistent setup (across shell sessions), add the same `export`
lines to `~/.bashrc` instead: but be aware they will be visible to
every program you launch from that shell.

---

## What's wired (verified clean)

| Component | Skill / Script | Status |
|---|---|---|
| Google Search Console + URL Inspection | `blog-google google_auth --check` | Tier 1 detected |
| PageSpeed Insights + CrUX + CrUX History | `blog-google pagespeed_check / crux_history` | Tier 1 detected |
| YouTube search + video deep-dive | `blog-google youtube_search` | API key live |
| GA4 organic traffic | `blog-google ga4_report` | Needs `ga4_property_id` in google-api.json |
| nanobanana image gen (Creative Director) | `/banana` skill, `/blog image` | MCP wired, restart needed |
| DataForSEO live SERP, keywords, backlinks, AI visibility | `seo-dataforseo` skill (in claude-seo) | MCP wired, restart needed |
| Inline SVG charts (dark-mode) | `blog-chart` internal capability + `/svg-chart` skill | Pure Python, works now |
| Animated SVGs (SMIL) | `/svg-animate` skill | Pure SVG, works now |
| Topic-cluster execution | `/blog cluster` | Hub-and-spoke pattern |
| Multilingual publishing | `/blog multilingual --languages de,fr,es` | Spawns translator agent |

---

## Verification (no API calls, runnable now)

```bash
# 1. nanobanana structural validation (8/8 should pass)
python3 skills/blog-image/scripts/validate_image_setup.py

# 2. Google API tier detection
python3 skills/blog-google/scripts/google_auth.py --tier --json

# 3. Plugin validate
claude plugin validate .

# 4. Full test suite
python -m pytest tests/ -q

# 5. Sample local SVG chart
ls -la demo-output/demo-chart.svg demo-output/demo-animated.svg
```

---

## Demo Flow A: full blog post with all features (recommended)

Use this in a live session to exercise every wired integration.
Each step is one slash command. Estimated total time: 8-12 min.

```
1. /blog brief "AI search citations: how to win in ChatGPT and Perplexity"
   -> Generates a brief with audience, intent, competitive angles.
      (No external API yet; pure LLM work.)

2. /seo dataforseo keywords "AI search citations" --limit 30
   -> Live keyword data (volume, difficulty, intent).
      Costs DataForSEO credits.

3. /seo dataforseo serp "how to get cited in ChatGPT"
   -> Live SERP including AI Overviews.
      Costs DataForSEO credits.

4. /blog google youtube search "AI search citations 2025" --max-results 5
   -> Candidate YouTube videos with editorial suitability data.
      Use a video only when it is relevant, accurate, useful, and eligible.
      Free quota.

5. /blog write "AI search citations" --brief
   -> Writes the full post. During the write, it will:
      - invoke the internal blog-chart capability to generate SVG charts inline
      - call /blog image (nanobanana) to generate the cover + hero
      - embed YouTube videos via srcdoc lazy-load (~5KB)
      - add content-consistent JSON-LD; FAQPage only when visible questions warrant it
      - strengthen evidence-backed explanations and supported original material

6. /blog seo-check <output_path>
   -> Validates title, meta, headings, schema, alt text.

7. /blog geo <output_path>
   -> AI citation readiness audit (passage citability, year anchors,
      source tier weighting).

8. /blog analyze <output_path>
   -> 5-category 100-point quality score.
```

---

## Demo Flow B: single-feature demos (when you want to highlight one thing)

### B1. "Cover image from a topic"

```
/banana generate "a clean editorial header for a blog post about
                  AI search citations, photorealistic, soft natural
                  light, 16:9 aspect ratio, suitable as a 1200x630
                  Open Graph image"
```

Output: file path under `~/Documents/nanobanana_generated/`. Banana
acts as Creative Director and constructs the 5-component prompt;
the skill auto-loads `references/gemini-models.md` and
`references/prompt-engineering.md` per its MANDATORY rule.

### B2. "Inline SVG chart from data"

```
/svg-chart bar from-data
[paste data]
ChatGPT,35
Claude,22
Perplexity,18
Gemini,15
Copilot,10
```

Within `/blog write` or `/blog rewrite`, the same data can be rendered by the
internal `blog-chart` capability.

### B3. "Animated SVG explaining a concept"

```
/svg-animate "loading spinner for a topic-cluster build with
              progress bar and pulsing dots, 3-second loop,
              dark mode"
```

### B4. "Live SERP for a query"

```
/seo dataforseo serp-youtube "claude code skill"
/seo dataforseo serp "blog SEO 2026"
/seo dataforseo intent "best ai citation tool"
```

### B5. "Backlink intelligence"

```
/seo dataforseo backlinks ahrefs.com --limit 50
/seo dataforseo competitors search.brave.com
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `${GOOGLE_AI_API_KEY}` shows as literal in MCP env | Claude Code launched before `source .env.local` | `source .env.local` then restart Claude Code |
| `dataforseo` MCP tools not available | Same as above OR npm package needs to be downloaded | Wait 30s on first call (npx fetches the package) |
| "MCP not configured" from `/blog image` | MCP didn't load this session | Check `.mcp.json` exists, then restart Claude Code |
| `pagespeed_check` says "API key invalid" | Key revoked OR rate limit | Check the key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| DataForSEO returns 401 | Wrong username/password OR account inactive | Check the credentials at [app.dataforseo.com](https://app.dataforseo.com) |
| YouTube search returns empty | Free YouTube Data API quota exhausted | Wait until quota reset (midnight Pacific) |

---

## Rotating credentials

```bash
# 1. Edit .env.local with the new values
$EDITOR .env.local

# 2. Re-source + restart Claude Code
source .env.local && exec claude code   # or however you launch it

# 3. For per-skill Google config (used by blog-google scripts directly):
$EDITOR ~/.config/claude-seo/google-api.json    # mode 0600

# 4. For permanent rotation (across all shells):
# remove the old `export GOOGLE_AI_API_KEY=...` from ~/.bashrc
# add the new one
```

To remove the credentials entirely:

```bash
shred -u .env.local                              # secure delete
shred -u ~/.config/claude-seo/google-api.json
# .mcp.json itself only has env-expansion placeholders, nothing to shred
```

The `uninstall.{sh,ps1}` scripts (post-audit fix VULN-805) also purge
`~/.config/claude-seo/{oauth-token,google-api}.json` automatically.

---

## What was wired in this session

- `.mcp.json` (mode 0600, gitignored): added `dataforseo` server
  alongside existing `nanobanana-mcp`. Both pinned (`@1.1.1` and
  `@2.8.10`). Both env-expansion only, no literal keys.
- `.env.local` (mode 0600, gitignored): the literal credentials live
  here. Source it before launching Claude Code.
- `~/.config/claude-seo/google-api.json` (mode 0600, user-private):
  contains the `api_key` for blog-google's scripts (which read it
  directly, not via MCP).
- `demo-output/demo-chart.svg`: sample static SVG bar chart.
- `demo-output/demo-animated.svg`: sample animated SVG (SMIL).
- `.gitignore`: added `demo-output/` so demo artifacts don't pollute
  git status.

No tracked files modified. No commits. The demo stays local.
