# Chart Input Schema (`chart.json`)

Input for `scripts/generate_chart_svg.py`, the deterministic chart generator.
This file documents what the script reads today; the script is the authority if
the two ever differ. All text is escaped by the script, and only `http` and
`https` source URLs become links.

Run it from the trusted skills root, with `--root` set to the folder that holds
the input and receives the output (the script refuses input or output paths that
escape `--root`, and refuses symlinks; relative paths resolve under `--root`,
which defaults to the current directory):

```bash
BLOG_SKILLS_DIR="${CLAUDE_BLOG_SKILLS_DIR:-<resolved skill dir>/..}"
case "$BLOG_SKILLS_DIR" in /*) ;; *) echo "ERROR: skills dir must be absolute" >&2; exit 1 ;; esac
python3 "$BLOG_SKILLS_DIR/blog-chart/scripts/generate_chart_svg.py" \
  --root "$D" --input chart-signups.json --output chart-signups.html --format html --json
```

`--format` is `html` (default) or `mdx` (camelCased JSX attributes). Without
`--output` the markup is returned in the `--json` result under `content`. The
`--json` status object has `status` (`success` or `error`), `type`, `bytes`, and
`output` or `content`; on failure it has `error`.

## Top-level fields

| Field | Required | Meaning |
|---|---|---|
| `type` | No (default `horizontal_bar`) | One of `horizontal_bar`, `grouped_bar`, `donut`, `line`, `lollipop`, `area`, `radar`. Aliases: `bar` and `horizontal bar` for `horizontal_bar`, `grouped bar` for `grouped_bar`. Case-insensitive; hyphens count as underscores. Anything else is an error |
| `title` | Recommended (default `Chart`) | Drawn in the chart and used for `<title>` |
| `subtitle` | No | Muted line under the title |
| `id` | **Set it on every chart** | Slug used to build `<id>-title` and `<id>-desc` (the `aria-labelledby` targets). If omitted it falls back to a slug of `title` |
| `description` | No | Screen-reader text for `<desc>`. Default is generated from the data and source |
| `source` | Recommended | A string, or an object `{ "title": "...", "date": "...", "url": "https://..." }`. Drawn in the SVG footer and the `<figcaption>`; `url` becomes a link only when it is `http` or `https` |
| `data` | Yes, except grouped with `series` | See below |
| `series` | Grouped only | See below |

## Unique ids when a page has several charts

The script does not check ids across files. Two charts with the same `id`, or
the same `title` and no `id`, produce duplicate `id="...-title"` and
`id="...-desc"` attributes on one page, and a screen reader then reads the wrong
label. Give every chart on a page a distinct `id` (for example `chart-1-signups`,
`chart-2-lcp`) and never reuse an `id` across charts in the same article. When
embedding hand-built SVG, follow the same rule.

## `data` for single-series types

Used by `horizontal_bar`, `lollipop`, `donut`, `line`, `area` and `radar`: a
non-empty array of objects.

```json
{
  "type": "horizontal_bar",
  "id": "chart-1-signups",
  "title": "Quarterly Signups by Product",
  "subtitle": "Q3 2026",
  "source": { "title": "Example Analytics Report", "date": "2026-09-30", "url": "https://example.com/report" },
  "data": [
    { "label": "Product A", "value": 420 },
    { "label": "Product B", "value": 315 },
    { "label": "Product C", "value": 180 }
  ]
}
```

- `label`: required, non-empty string.
- `value`: finite number, **zero or greater** (negative values are an error).
- Order is drawn as given. `line` and `area` treat the array as a time or
  category sequence left to right. `radar` places each item on its own axis and
  scales to the largest value (use 5 to 7 axes). `donut` shows shares of the sum
  and prints the total in the center.
- Each chart scales to its own maximum, so a bar and a lollipop of the same data
  look alike in proportion; keep units consistent within one chart.

## `grouped_bar`

Either form is accepted. Prefer `series`.

```json
{
  "type": "grouped_bar",
  "id": "chart-2-lcp",
  "title": "LCP before and after (seconds)",
  "source": "Internal test, 2026",
  "series": [
    { "name": "Before", "data": [{ "label": "Home", "value": 3.1 }, { "label": "Post", "value": 2.8 }] },
    { "name": "After",  "data": [{ "label": "Home", "value": 2.2 }, { "label": "Post", "value": 1.9 }] }
  ]
}
```

Row form, same result:

```json
{ "type": "grouped_bar", "id": "chart-2-lcp", "title": "LCP before and after (seconds)",
  "data": [
    { "label": "Home", "values": { "Before": 3.1, "After": 2.2 } },
    { "label": "Post", "values": { "Before": 2.8, "After": 1.9 } }
  ] }
```

Every series needs a non-empty `name` and a non-empty `data` array; every row
needs a non-empty `values` object. A chart with too many groups for the fixed
560 by 380 canvas fails with "too dense"; split it or drop categories.

## Output

A `<figure class="blog-chart">` containing a transparent inline SVG
(`viewBox="0 0 560 380"`, `role="img"`, `aria-labelledby`, `<title>`, `<desc>`)
and a `<figcaption>` with the source. Colors come from a fixed palette, text uses
`currentColor`, and muted text uses `--chart-muted` for contrast in light and
dark mode. Place the markup inside the article where the claim it supports sits.

## Choosing and repeating types

Prefer variety when the data differ. Repeat a type when the charts compare like
with like (two before/after grouped bars, a series of per-metric line charts) so
readers can compare them directly. Do not switch a chart type only to avoid a
repeat.
