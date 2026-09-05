---
type: deliverable
title: "Blog Chart Specification"
domain: "Blog Media"
status: active
created: 2026-07-09
updated: 2026-07-09
tags: [deliverables, charts, media, active]
---

# Blog Chart Specification

## Blog Chart Specification Distinct Job

This specification governs chart requests for blog posts. A chart must make a claim easier to inspect, not decorate an unsupported point. The output can be an accessible inline SVG, a data table, or an MDX-ready component spec. It connects to [[Images Audio and Charts]] for media rules and [[Blog Schema Stack]] when image or article schema needs to describe the asset.

### Inputs Specific To Blog Chart Specification

The requester must provide the article section, data source, date range, chart purpose, target reader, required comparison, caption text, alt-text direction, and whether the chart must be converted to MDX. `g-helpful-content` keeps the visual tied to reader value. `nng-editorial-heuristics` is used as editorial usability guidance, not as SEO proof.

### Decisions Blog Chart Specification Must Record

Record chart type, source provenance, license or usage basis, accessibility approach, mobile behavior, caption wording, schema relationship, and review owner. `g-google-images` informs image quality and alt text, while `schema-full` helps describe visual entities when markup is appropriate.

## Blog Chart Specification Deliverable Contract Table

| Asset requirement | Evidence needed | Accessibility check | Placement rule | Review result |
|---|---|---|---|---|
| Data provenance | Source ID, retrieval date, data owner | Caption names source and time span | Near the claim it supports | pass, revise, or block |
| Chart type | Reason for bar, line, table, or scatter | Shape does not carry the only meaning | After the explanatory sentence | pass, revise, or block |
| Inline SVG | Title, desc, labels, fallback table | Keyboard and screen-reader labels present | No tiny text on mobile | pass, revise, or block |
| MDX conversion | Component name and props | Text alternatives survive conversion | Same article section | pass, revise, or block |
| Schema relationship | ImageObject or article asset note | Markup describes visible asset | Only when page shows the chart | pass, revise, or block |

## Operating Procedure For Accessible Charts

1. Start with the claim and source before selecting a visual form.
2. Choose the simplest chart that lets the reader compare the values accurately.
3. Add caption, alt text, and fallback table before design polish.
4. Block publication if the data source, license, or claim scope is unresolved.

## Source IDs Used

Chart specifications use `g-helpful-content`, `nng-editorial-heuristics`, `schema-full`, and `g-google-images`.
