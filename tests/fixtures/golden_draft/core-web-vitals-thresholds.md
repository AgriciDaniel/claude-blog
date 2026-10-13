---
title: Core Web Vitals Thresholds Explained
description: A page passes Core Web Vitals when LCP is 2.5 seconds or less, INP is 200 milliseconds or less, and CLS is 0.1 or less at the 75th percentile of real visits.
date: 2026-10-10
author: Alex Rivera
canonical: https://example.com/blog/core-web-vitals-thresholds/
slug: core-web-vitals-thresholds
site_name: Example Engineering Blog
lang: en
og_image_alt: Abstract teal gradient banner for an article about Core Web Vitals thresholds
tags:
  - Web performance
  - Core Web Vitals
  - SEO
---

A page passes Core Web Vitals when, at the 75th percentile of real visits, its Largest Contentful Paint is 2.5 seconds or less, its Interaction to Next Paint is 200 milliseconds or less, and its Cumulative Layout Shift is 0.1 or less. Miss any one of the three and the page does not pass. Everything else in this article explains how those numbers are measured, why the percentile matters, and what to change when one of them fails.

## Key takeaways

- Three metrics decide the result: LCP for loading, INP for responsiveness, CLS for visual stability.
- Each metric has a "good" boundary and a "poor" boundary, with a "needs improvement" band between them.
- The verdict comes from field data at the 75th percentile, not from a single lab run.
- Lab tools are for debugging. Field data from real users is the scorecard.
- Fix the slowest metric first, because a page is judged on its weakest result.

## What the three metrics measure

Core Web Vitals is a small set of user-centered measurements that Google and the Chrome team publish as shared vocabulary for page experience. Each metric answers one question a visitor would ask: did the page show up quickly, did it respond when I touched it, and did it stay still while I read.

**Largest Contentful Paint (LCP)** reports how long the largest image, video poster, or block of text in the viewport takes to render, measured from the moment the visitor starts the navigation. It is the closest single number to "when did the page look ready". The [web.dev LCP guide](https://web.dev/articles/lcp) lists which elements qualify, including images, poster images on video elements, elements with a background image loaded through a URL, and block-level text.

**Interaction to Next Paint (INP)** observes the latency of clicks, taps, and key presses across the whole visit and reports a value close to the worst one. Each interaction is measured from the input event until the browser can paint the next frame. INP replaced First Input Delay as a Core Web Vital on March 12, 2024, and it is a harder test, because First Input Delay only looked at the delay before the first interaction began.

**Cumulative Layout Shift (CLS)** adds up unexpected movement of visible content. A shift counts when an element moves without the visitor causing it, such as an image that loads late and pushes the paragraph below it down the screen. Shifts that begin within 500 milliseconds of a user input are excluded, since the visitor expected something to change.

## The thresholds in one table

Google documents a "good" boundary and a "poor" boundary for each metric. Anything between the two is "needs improvement". The values below come from the [web.dev Core Web Vitals overview](https://web.dev/articles/vitals) and the [Search Central page experience documentation](https://developers.google.com/search/docs/appearance/core-web-vitals).

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| Largest Contentful Paint | 2.5 s or less | 2.5 s to 4.0 s | Over 4.0 s |
| Interaction to Next Paint | 200 ms or less | 200 ms to 500 ms | Over 500 ms |
| Cumulative Layout Shift | 0.1 or less | 0.1 to 0.25 | Over 0.25 |

The figure below plots the same boundaries as a share of each metric's poor boundary, so loading time, latency, and a unitless shift score can sit on one scale. The teal segment is the good range, the amber segment is the middle band, and the red segment starts where the poor range begins.

<figure>
<svg viewBox="0 0 640 260" role="img" aria-label="Bar chart of the good, needs improvement and poor ranges for LCP, INP and CLS, scaled so each poor boundary sits at the same position">
<text x="20" y="28" font-size="14" fill="currentColor">Share of the poor boundary used by each range</text>
<text x="20" y="78" font-size="13" fill="currentColor">LCP</text>
<rect x="80" y="60" width="300" height="26" fill="#0f766e"></rect>
<rect x="380" y="60" width="180" height="26" fill="#d97706"></rect>
<rect x="560" y="60" width="60" height="26" fill="#b91c1c"></rect>
<text x="80" y="106" font-size="12" fill="currentColor">Good: up to 2.5 s</text>
<text x="560" y="106" font-size="12" fill="currentColor" text-anchor="end">Poor: over 4.0 s</text>
<text x="20" y="148" font-size="13" fill="currentColor">INP</text>
<rect x="80" y="130" width="192" height="26" fill="#0f766e"></rect>
<rect x="272" y="130" width="288" height="26" fill="#d97706"></rect>
<rect x="560" y="130" width="60" height="26" fill="#b91c1c"></rect>
<text x="80" y="176" font-size="12" fill="currentColor">Good: up to 200 ms</text>
<text x="560" y="176" font-size="12" fill="currentColor" text-anchor="end">Poor: over 500 ms</text>
<text x="20" y="218" font-size="13" fill="currentColor">CLS</text>
<rect x="80" y="200" width="192" height="26" fill="#0f766e"></rect>
<rect x="272" y="200" width="288" height="26" fill="#d97706"></rect>
<rect x="560" y="200" width="60" height="26" fill="#b91c1c"></rect>
<text x="80" y="246" font-size="12" fill="currentColor">Good: up to 0.1</text>
<text x="560" y="246" font-size="12" fill="currentColor" text-anchor="end">Poor: over 0.25</text>
</svg>
<figcaption>Good, needs improvement and poor ranges for the three Core Web Vitals, drawn from the documented thresholds. Source: web.dev, Core Web Vitals overview.</figcaption>
</figure>

## Why the 75th percentile decides the verdict

A single page load is a poor basis for a verdict. A visitor on a fast laptop with a warm cache and a visitor on a mid-range phone over a congested mobile network experience different pages from the same URL. Google therefore evaluates each metric across many real visits and takes the value at the 75th percentile. If you sorted all page loads from best to worst, the page load three quarters of the way down the list is the one that counts.

The practical effect is that a page must be good for most visitors. If 30 percent of your traffic arrives on slow devices and those visits record an LCP of 5 seconds, the 75th percentile will land in the poor range even when the other 70 percent of visits are fast.

The evaluation is also segmented. Mobile and desktop are assessed separately, so a page can pass on desktop and fail on mobile. Because most sites receive a majority of mobile traffic, the mobile result is usually the one that deserves attention first.

### Where the field data comes from

The Chrome User Experience Report, usually shortened to CrUX, collects anonymized measurements from opted-in Chrome users. The public dataset aggregates them over a rolling 28-day window, which has two consequences. A fix you ship today takes weeks to fully show up, and a regression you ship today will not immediately appear either. Use lab tools for same-day feedback.

PageSpeed Insights shows both views side by side. The top section is CrUX field data for the URL, or for the whole origin when the URL has too little traffic. The Lighthouse section below it is a single simulated lab run. When the two disagree, trust the field data for the verdict and use the lab run to investigate causes. The [Chrome UX Report documentation](https://developer.chrome.com/docs/crux) describes the dataset and its eligibility rules.

## Fixing LCP: find the slow phase first

The most useful LCP fact for debugging is that the metric breaks into four sequential parts: time to first byte, resource load delay, resource load duration, and element render delay. A page with a 4 second LCP has one dominant phase, and the fix depends on which phase that is.

- **Slow time to first byte.** The server, a redirect chain, or a missing cache is delaying everything. Compress the redirect chain, cache the HTML where the content allows it, and serve from a location near the audience.
- **High resource load delay.** The browser discovered the LCP image late, usually because it is set through CSS or injected by a script. Put the image in the HTML as a normal image element so the preload scanner finds it, and raise its fetch priority (see [preloading the hero image](related/preload-hero.html)).
- **Long resource load duration.** The file is too large. Serve a correctly sized modern format and avoid shipping a desktop-width image to a phone.
- **Long element render delay.** The resource arrived but something blocks painting, such as a render-blocking stylesheet or a script that hides content until it runs.

A common mistake is to lazy-load the hero image, which defers the very element that LCP measures. Keep the first screen eager and lazy-load only what sits below the fold.

## Fixing INP: shorten the work between input and paint

INP is the metric most sites fail after switching from First Input Delay, because it reflects the whole life of an interaction. The [web.dev INP guide](https://web.dev/articles/inp) splits each interaction into input delay, processing time, and presentation delay. Input delay grows when the main thread is busy with other work as the visitor taps. Processing time is your event handlers. Presentation delay is the time to style, lay out, and paint the result.

Three habits reduce most INP problems:

1. **Break up long tasks.** Any task holding the main thread for more than about 50 milliseconds can delay an interaction. Yield to the browser between chunks of work so pending input can run.
2. **Do less in the handler.** Update the visible state first and defer analytics calls, storage writes, and non-urgent computation until after the next paint.
3. **Reduce rendering cost.** Large DOM trees and expensive style recalculations make every interaction slower. Remove unused elements and avoid animating layout properties.

Because INP is reported close to the worst interaction, a single slow menu or heavy filter control can set the score for the entire page. Test the interactions visitors actually use, not just the first one.

## Fixing CLS: reserve space before content arrives

Layout shift almost always has one of four causes: images and embeds without dimensions, late-loading fonts that change text size, content injected above existing content, and animations that move elements through layout. The [web.dev CLS guide](https://web.dev/articles/cls) covers each one.

The most reliable fixes are mechanical:

- Set `width` and `height` attributes, or an `aspect-ratio`, on every image, video, and iframe so the browser reserves the space.
- Reserve a fixed slot for ads, consent banners, and embeds, even when the content is not ready.
- Use `font-display` with a fallback font that closely matches the metrics of the web font.
- Animate with `transform` and `opacity`, which do not trigger layout, instead of `top`, `margin`, or `height`.

Layout shift is calculated over session windows. A window groups shifts that happen within one second of each other, capped at five seconds in total, and the reported CLS is the largest window rather than the sum of the whole visit.

## How Core Web Vitals relate to search

Google Search Central states that its ranking systems seek to reward content that provides a good page experience, and that Core Web Vitals are part of how it measures this. The same documentation is equally clear on the limit of the effect: a good page experience does not override content relevance. A page that answers the query well can still rank with weaker vitals, and a fast page with thin content will not outrank a better answer.

The sensible reading is that vitals are a quality floor, not a substitute for useful content. They are also worth fixing for reasons independent of search, because a faster, steadier page simply serves visitors better.

## A practical workflow

A short loop keeps the work focused:

1. Open the Core Web Vitals report in Search Console, or the PageSpeed Insights field section, and note which metric fails for which device group.
2. Pick the URL group with the most traffic and the worst result. Fixing one template often fixes hundreds of URLs.
3. Reproduce the problem in the lab with throttling that resembles the slow end of your audience, then profile the failing phase.
4. Ship one change at a time so the cause of any improvement is clear.
5. Wait for the 28-day window to roll before declaring success, and keep a lab regression test in your build.

Keep a short log of which change moved which metric, because the next regression will look a lot like the last one. Related reading on the same site covers [measuring interaction latency in practice](related/measuring-inp.html) and [a checklist for image delivery](related/image-delivery-checklist.html).

## Frequently asked questions

### Do I need to pass all three metrics?

Yes. A page passes Core Web Vitals only when all three metrics are in the good range at the 75th percentile for that device group. Two out of three is a fail.

### Why does PageSpeed Insights show a good score but Search Console reports a problem?

The Lighthouse performance score comes from one simulated lab run, while Search Console uses field data from real visitors over 28 days. They measure different things. Lighthouse also cannot measure INP directly, since a lab run has no real interactions, and uses Total Blocking Time as a loose proxy.

### How long until a fix shows up?

Because CrUX reports a rolling 28-day window, expect gradual improvement over roughly four weeks. Lab tools show the effect the same day.

### Does a low-traffic page get a score?

Often not. CrUX needs enough eligible visits before it publishes a result for a URL, and otherwise PageSpeed Insights falls back to origin-level data that describes the whole site.

### Which metric should I fix first?

Start with the failing metric furthest from its good boundary on mobile, preferably one tied to a shared template, since one change then improves many URLs.

## Sources

- [Core Web Vitals overview, web.dev](https://web.dev/articles/vitals): metric definitions and the good, needs improvement, and poor thresholds.
- [Understanding page experience in Google Search results, Google Search Central](https://developers.google.com/search/docs/appearance/core-web-vitals): how Core Web Vitals relate to Search, and the statement that page experience does not override relevance.
- [Largest Contentful Paint, web.dev](https://web.dev/articles/lcp): qualifying elements and the four LCP phases.
- [Interaction to Next Paint, web.dev](https://web.dev/articles/inp): interaction phases and the March 2024 change from First Input Delay.
- [Cumulative Layout Shift, web.dev](https://web.dev/articles/cls): session windows and the input exclusion.
- [Chrome UX Report, Chrome for Developers](https://developer.chrome.com/docs/crux): the field dataset and its 28-day window.

All sources were last checked on 2026-10-10.

## About the author

Alex Rivera is a web performance engineer who has spent several years profiling production sites for loading, responsiveness, and layout stability. Alex writes about measurement methods for the Example Engineering Blog and can be reached through the [author page](related/author.html) or the [contact page](related/contact.html). Sourcing and correction rules are in the [editorial policy](related/editorial-policy.html).
