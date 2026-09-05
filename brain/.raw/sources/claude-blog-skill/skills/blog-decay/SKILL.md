---
name: blog-decay
description: Detect content decay from Google Search Console exports by comparing current and previous page performance, flagging quarter-over-quarter traffic drops, dropped pages, and refresh, consolidate, prune, or query-shift actions. Use when the user says "/blog decay", "content decay", "traffic drop", "QoQ decline", "GSC decay", or "refresh declining posts".
argument-hint: "<current-gsc.json> <previous-gsc.json> [threshold] [metric]"
user-invokable: true
license: MIT
---

# Blog Decay

Use `/blog decay` to find pages whose Google Search Console performance has
declined quarter-over-quarter. The command compares a current-period export
against a previous-period export, flags pages with a 20% or larger decline by
default, and recommends the next content action.

## Default Offline Workflow

Run the local analyzer against two GSC page exports:

```bash
python3 scripts/content_decay.py current.json previous.json
```

Useful options:

```bash
python3 scripts/content_decay.py current.json previous.json --threshold 0.30
python3 scripts/content_decay.py current.json previous.json --metric impressions
python3 scripts/content_decay.py current.json previous.json --format markdown --output decay-report.md
```

The script accepts JSON lists of page rows with `page` or `url`, `clicks`, and
`impressions`. It also accepts the object shape returned by `blog-google` when
the rows are under a top-level `rows` key.

## Optional Live GSC Export

For live data, use `/blog google gsc` or the underlying `blog-google` command
to create each period export, then run the offline analyzer:

```bash
python3 skills/blog-google/scripts/run.py gsc_query --property sc-domain:example.com --dimensions page --start-date YYYY-MM-DD --end-date YYYY-MM-DD --json > gsc-current.json
python3 skills/blog-google/scripts/run.py gsc_query --property sc-domain:example.com --dimensions page --start-date YYYY-MM-DD --end-date YYYY-MM-DD --json > gsc-previous.json
python3 scripts/content_decay.py gsc-current.json gsc-previous.json --format markdown
```

Use adjacent periods of similar length for short-term checks. For seasonality,
also run a year-over-year comparison using the same date length, filters, search
type, device, country, and property. When possible, inspect up to 16 months of
GSC history before diagnosing a traffic drop.

## Decay Model

The default metric is `clicks`. Also review impressions, CTR, average position,
query and page pairs, device, country, and search appearance deltas before
choosing an action.

Severity:

| Decline | Severity |
| --- | --- |
| 20% to 39.9% | warning |
| 40% to 59.9% | high |
| 60% or more | critical |

Dropped pages are previous-period pages missing from the current export only
after confirming identical filters, sufficient row limits, matching dimensions,
and URL inspection. Otherwise mark them as `needs_validation`, not
`dropped_out`.

## Recommended Actions

Use the action as the first triage path only after checking indexation,
canonical status, query loss, internal links, backlinks, seasonality, and
business value:

| Action | Use when |
| --- | --- |
| refresh/update content | The page still has demand and likely needs freshness, title, internal link, or section updates. |
| investigate query shift | Clicks fell while impressions held up, suggesting CTR, rank, SERP, or query mix changes. |
| consolidate/redirect | The page dropped out or the loss is severe enough that merging into a stronger URL may recover value faster. |
| prune | The page had very low prior demand and may not justify rewrite effort. |

## Cross-references

Use `blog-google` to collect Search Console exports when live credentials are
available. Use `blog-rewrite` after decay detection when the recommended action
is refresh/update content and the page is worth improving.
