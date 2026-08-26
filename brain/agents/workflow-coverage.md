# Claude Blog Workflow Coverage

This matrix maps the claude-blog workflow surface to owned curator agents. It is advisory until the audit gate passes. It is also the curator coverage contract: each workflow names an owner and support reviewer, cites current source evidence, records claim confidence, and remains read-only toward external systems.

| Workflow | Primary owner | Support |
|---|---|---|
| `/blog write` | `blog-writing-curator` | `blog-quality-curator` |
| `/blog rewrite` | `blog-writing-curator` | `blog-monitoring-curator` |
| `/blog update` | `blog-monitoring-curator` | `blog-writing-curator` |
| `/blog analyze` | `blog-quality-curator` | `blog-data-curator` |
| `/blog audit` | `blog-quality-curator` | `blog-schema-curator` |
| `/blog factcheck` | `blog-quality-curator` | `blog-eeat-curator` |
| `/blog brief` | `blog-strategy-curator` | `blog-data-curator` |
| `/blog outline` | `blog-strategy-curator` | `blog-writing-curator` |
| `/blog calendar` | `blog-strategy-curator` | `blog-distribution-curator` |
| `/blog strategy` | `blog-strategy-curator` | `blog-cluster-curator` |
| `/blog seo-check` | `blog-quality-curator` | `blog-monitoring-curator` |
| `/blog schema` | `blog-schema-curator` | `blog-quality-curator` |
| `/blog geo` | `blog-geo-curator` | `blog-schema-curator` |
| `/blog google` | `blog-monitoring-curator` | `blog-data-curator` |
| `/blog taxonomy` | `blog-cluster-curator` | `blog-strategy-curator` |
| `/blog cluster` | `blog-cluster-curator` | `blog-strategy-curator` |
| `/blog cannibalization` | `blog-cluster-curator` | `blog-data-curator` |
| `/blog multilingual` | `blog-multilingual-curator` | `blog-strategy-curator` |
| `/blog translate` | `blog-multilingual-curator` | `blog-writing-curator` |
| `/blog localize` | `blog-multilingual-curator` | `blog-persona-curator` |
| `/blog locale-audit` | `blog-multilingual-curator` | `blog-quality-curator` |
| `/blog persona` | `blog-persona-curator` | `blog-writing-curator` |
| `/blog discourse` | `blog-persona-curator` | `blog-distribution-curator` |
| `/blog repurpose` | `blog-distribution-curator` | `blog-writing-curator` |
| `/blog flow` | `blog-flow-curator` | `blog-quality-curator` |

Shared rule: every owner cites dated sources, keeps work advisory and read-only, and runs `python3 scripts/audit_brain.py --json` before claiming release readiness.
