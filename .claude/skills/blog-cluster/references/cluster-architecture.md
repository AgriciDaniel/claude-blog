# Cluster Architecture: Hub-and-Spoke Linking & Schema

> Reference document for `blog-cluster`. Loaded on demand during Plan Phase
> Step 3 and during scorecard generation.

## Why hub and spoke?

Google's algorithm rewards **topical authority**, which means proving deep
coverage of an entire subject area. The hub-and-spoke pattern is the
structural shape that demonstrates this authority to both search engines and
AI citation systems.

```
                    ┌──────────────────┐
                    │   PILLAR PAGE    │
                    │  (hub, 2,500w+)  │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼──────────────────┐
           │                 │                  │
    ┌──────▼──────┐   ┌──────▼─────┐   ┌────────▼────┐
    │ Cluster A   │   │ Cluster B  │   │ Cluster C   │
    │ (2-4 posts) │   │ (2-4 posts)│   │ (2-4 posts) │
    └──────┬──────┘   └──────┬─────┘   └────────┬────┘
           │                 │                  │
      ┌────┼────┐       ┌────┴────┐         ┌───┴───┐
     A1  A2   A3      B1        B2        C1      C2
        (Spokes, 1,200 to 1,800 words each)
```

For deeper background on link architecture and anchor distribution rules
shared across all claude-blog skills, see `skills/blog/references/internal-linking.md`.
This document focuses on the cluster-specific overlay.

## Pillar (hub) anatomy

| Attribute | Requirement |
|-----------|-------------|
| Word count | 2,500 to 4,000 |
| Template | `pillar-page` |
| Primary keyword | Broadest, highest-volume keyword in the cluster |
| Coverage | Touches every sub-topic covered by spokes (one section per spoke minimum) |
| Depth | Broad but substantive; each section can stand alone |
| Outgoing links | One contextual link to every spoke |
| Incoming links | One contextual link from every spoke |
| Internal-link density | One link to every spoke, plus only as many existing-site links as fit naturally |
| Schema | `Article` plus `BreadcrumbList` plus `ItemList` (the spokes) |

The pillar is written first during execution so that every spoke can link to
a real filename instead of a placeholder.

## Spoke (supporting post) anatomy

| Attribute | Requirement |
|-----------|-------------|
| Word count | 1,200 to 1,800 |
| Template | Auto-selected by intent (table below) |
| Primary keyword | One specific long-tail keyword unique to this spoke |
| Coverage | Deep dive into one specific aspect of the cluster |
| Outgoing links | Pillar (mandatory) + 2 to 3 same-cluster siblings + 0 to 1 cross-cluster |
| Incoming links | Pillar (mandatory) + 1 to 2 same-cluster siblings |
| Internal-link density | 5 to 7 internal links total |
| Schema | `Article` (with `isPartOf` referencing the pillar) plus `BreadcrumbList` |

### Template selection by intent

| Intent and signal | Template |
|-------------------|----------|
| Informational + "how to" | `how-to-guide` |
| Informational + "what is" | `faq-knowledge` |
| Informational + deep topic | shorter pillar pattern (1,500 to 2,000) |
| Commercial + "best" / "top" | `listicle` |
| Commercial + "X vs Y" | `comparison` |
| Commercial + "review" | `product-review` |
| Research + data | `data-research` |
| Tutorial + code or tools | `tutorial` |
| Industry opinion | `thought-leadership` |
| Expert quotes | `roundup` |

## Internal-link injection rules (cluster-specific)

Mandatory links per spoke:

1. **Spoke to pillar** (one link minimum)
   - Anchor: pillar primary keyword (natural variation allowed)
   - Position: within the first 3 paragraphs and again in the conclusion
   - Example: `For a complete walkthrough, see our [AI marketing guide](pillar.md).`
2. **Pillar to each spoke**
   - Anchor: spoke's primary keyword
   - Position: in the relevant section of the pillar body
3. **Sibling spokes (same cluster)**
   - 2 to 3 cross-links per spoke within the cluster
   - Anchor: target spoke's primary keyword (use natural variation)
   - Position: contextually relevant paragraphs

Optional links:

4. **Cross-cluster** (one per spoke maximum)
   - Only when topically relevant
   - Strengthens the overall cluster web without diluting topical focus

### Anchor text strategy (overrides only the cluster context; site-wide rules from `skills/blog/references/internal-linking.md` still apply)

Within a single cluster, vary anchors to avoid repetition. Distribution
target across all internal links produced by `blog-cluster`:

| Anchor type | Target share | Example for primary keyword "ai marketing for small business" |
|-------------|--------------|----------------------------------------------------------------|
| Exact match | 5 to 10 percent | "ai marketing for small business" |
| Partial match | 25 to 35 percent | "ai marketing tactics for small businesses", "small business AI marketing playbook" |
| Branded or descriptive | 20 to 30 percent | "our complete guide", "the case study we ran" |
| Semantic or related | 30 to 40 percent | "AI tools that fit a lean budget", "automating outreach with AI" |

Hard rule: never reuse the same exact anchor text for the same destination
across more than one source post.

### Link-density targets

| Post type | Min outgoing | Min incoming | Max total internal |
|-----------|--------------|--------------|--------------------|
| Pillar | One per spoke | One per spoke | Dynamic: at least `spoke_count`, plus existing-site links only when useful |
| Spoke | 3 (pillar + 2 siblings) | 2 (pillar + 1 sibling) | 7 |

## Schema markup strategy

Schema generation is delegated to `/blog schema` after the cluster is
written. This document specifies the schema *shape* the cluster requires.

### Pillar page schema

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "<pillar title>",
  "description": "<meta description>",
  "isPartOf": {
    "@type": "WebPage",
    "name": "<site name>"
  },
  "about": {
    "@type": "Thing",
    "name": "<seed keyword>"
  },
  "hasPart": [
    {"@type": "Article", "headline": "<spoke title>", "url": "<spoke url>"}
  ]
}
```

Pair with an `ItemList` enumerating the spokes:

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "<cluster name>",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "url": "<spoke url>", "name": "<spoke title>"}
  ]
}
```

### Spoke schema

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "<spoke title>",
  "isPartOf": {
    "@type": "Article",
    "headline": "<pillar title>",
    "url": "<pillar url>"
  }
}
```

### BreadcrumbList (every post)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Blog", "item": "<blog url>"},
    {"@type": "ListItem", "position": 2, "name": "<Pillar Title>", "item": "<pillar url>"},
    {"@type": "ListItem", "position": 3, "name": "<Post Title>", "item": "<post url>"}
  ]
}
```

## Cannibalization prevention

Verify before execution:

1. No two posts share the same primary keyword.
2. No two posts target keywords with greater than 70 percent SERP overlap.
3. H1 and title tag are unique across all cluster posts.
4. Meta descriptions do not repeat the same keyword phrase verbatim.

If a violation is detected during planning, the planner must adjust before
execution. Run `/blog cannibalization` after execution as an independent
audit pass.
