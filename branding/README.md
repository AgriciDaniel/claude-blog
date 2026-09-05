# claude-blog brand system

Source-of-truth visual assets for the `claude-blog` skill suite. Same brand
system as `claude-ads` and `claude-seo` v2.x: OS-window-framed dark CRT
terminal with BRAND-ORANGE accent palette unified across all three products.

## Canonical artifacts (the 5 SVGs)

| File | Purpose |
|---|---|
| `../assets/cover-blog.svg` | Final cover asset for the README hero |
| `../assets/diagrams/01-architecture-B.svg` | System architecture. L-to-R orchestrator pipeline |
| `../assets/diagrams/02-pipeline-B.svg` | Final delivery pipeline diagram |
| `../assets/diagrams/03-sub-skill-map-A.svg` | Final sub-skill map diagram |
| `../assets/diagrams/04-framework-B.svg` | FLOW radial wheel: find, leverage, optimize, win + 30 prompts |

The roadmap and unselected A/B/C variants were pruned in v1.11.0. The
remaining SVGs are hand-finalized external assets.

## Preview

Open `final.html` in a browser to see the cover + 4 locked diagrams composed
together with OS-window framing and filename labels:

```bash
xdg-open branding/final.html   # Linux
open branding/final.html       # macOS
start branding/final.html      # Windows
```

## Regeneration

`scripts/generate_diagrams.py` is retired as of v1.11.0. It is kept only as
a fail-fast stub so it cannot clobber the finalized external SVGs.

```bash
python3 branding/scripts/generate_diagrams.py
```

The command prints a retirement notice and exits non-zero.

## How to use the cover in markdown

```html
<img src="assets/cover-blog.svg"
     alt="claude-blog: The Content Operating System"
     width="100%">
```

The SVG is self-contained. No external font fetches at render time. Uses
the Inter and JetBrains Mono font stack with system-monospace fallbacks.

## How to use the diagrams in markdown

```html
<img src="assets/diagrams/03-sub-skill-map-A.svg"
     alt="claude-blog sub-skill ecosystem: orchestrator hub + 8 categories"
     width="100%">
```

Each diagram has an OS-window header with the diagram title and traffic
light buttons. The corner-mark text in the lower-right names the variant
(e.g. "03 . SUB-SKILL ECOSYSTEM . B") for traceability.

## Cross-product brand consistency

The system is shared with `claude-ads` and `claude-seo`. All three products
use the same:

- Canvas color: `#1F1B16` (deep coffee)
- Accent ramp: BRAND-ORANGE `#D97757`
- Typography: JetBrains Mono for terminal text + labels, Inter for body
- OS-window chrome: dark title bar with three traffic light buttons
- Diagram corner-mark pattern: `NN . SERIES NAME . VARIANT`
- Animation budget: static assets in v1.11.0 (cover and diagrams carry no motion)

What differs per product:

- Final asset content reflects each product's surface area and roadmap
- Cover wordmark text and tagline
- Command palette contents on the cover

## Animation budget

The cover carries any motion in the visual set. The 4 architecture and
framework diagrams are static. Reading text benefits from zero competing
motion.

## Provenance

This brand system was first established in `AgriciDaniel/claude-ads`
`branding/` and `AgriciDaniel/claude-seo` `branding/` v2.x. The
`claude-blog` adaptation uses the shared `BRAND-ORANGE` palette (not a
per-product accent), matching the v2.x cross-product convention.

The earlier per-product purple SVG kit (committed in `b7fa616`) was
sunset in this revision in favor of the unified brand-orange system.
