# YouTube Video Embed Reference

## Why YouTube Embeds Matter

Video can improve engagement and extraction when it is relevant, current, and
high quality. Treat vendor correlation studies as directional, not as ranking
requirements. Key data points:

- **0.737 correlation** with AI visibility, the strongest single signal (Ahrefs 75K-brand study)
- Video citations in AI Overviews up **414%** year-over-year (NP Digital Q1 2025, 10K+ AIO analysis)
- How-to video citations up **651%**, visual demo citations up **592%** (NP Digital)
- YouTube is cited **200x more** than any other video platform by AI systems

Strongly prefer relevant YouTube embeds when a suitable video exists. Skip video
when available videos are stale, low quality, off-topic, or would distract from
the article.

---

## Video Quality Criteria

### Minimum Standards

| Criterion | Minimum | Preferred |
|-----------|---------|-----------|
| Views | >1,000 | >10,000 |
| Like ratio | >90% | >95% |
| Recency | <3 years | <18 months |
| Channel subscribers | >1,000 | >10,000 |
| Duration | >3 minutes | 5-15 minutes |
| Captions | Present | Accurate/manual |
| Relevance | Title keyword match | Title + description match |

### Quality Scoring Formula (0-100)

| Factor | Weight | Scoring Method |
|--------|--------|---------------|
| Relevance (title/description keyword match) | 35 pts | Exact keyword in title = 35, partial = 20, description only = 10 |
| View count (log scale) | 20 pts | log10(views) / log10(10M) * 20, capped at 20 |
| Recency (months since publish) | 20 pts | max(0, 20 - (months_old * 0.8)) |
| Channel authority (subscribers, log scale) | 15 pts | log10(subs) / log10(1M) * 15, capped at 15 |
| Engagement (like ratio) | 10 pts | (like_ratio - 0.80) / 0.20 * 10, capped at 10 |

**Minimum score threshold: 50/100.** Videos scoring below 50 should be skipped.

---

## Embed Placement Strategy

| Position | Video Purpose | When |
|----------|--------------|------|
| After introduction (before first H2 body) | Overview / explainer | Always place 1st video here |
| Mid-article (after 2nd or 3rd H2) | Tutorial / demo / how-to | If video shows a process |
| Before FAQ or conclusion | Summary or expert opinion | Optional 3rd video |

### Placement Rules

- **2-3 videos per post** (never more than 3)
- Minimum **500 words** between video embeds
- Never place a video immediately before or after a chart
- Videos **complement** text; they never replace written content

---

## Embed Code Patterns

Before rendering any embed, validate `VIDEO_ID` against YouTube's ID pattern and
escape title, channel, and description fields with `html.escape(value, quote=True)`.
Reject untrusted `javascript:`, `data:`, and `file:` URLs.

### MDX / Next.js (camelCase, srcDoc lazy loading)

```jsx
<figure className="video-embed" style={{margin: '2.5rem 0', textAlign: 'center'}}>
  <div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', maxWidth: '100%', borderRadius: '12px'}}>
    <iframe
      srcDoc="<style>*{padding:0;margin:0;overflow:hidden}html,body{height:100%}img,span{position:absolute;width:100%;top:0;bottom:0;margin:auto}span{height:1.5em;text-align:center;font:48px/1.5 sans-serif;color:white;text-shadow:0 0 0.5em black}</style><a href='https://www.youtube.com/embed/VIDEO_ID?autoplay=1'><img src='https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg' alt='VIDEO_TITLE_ESC'><span>&#x25BA;</span></a>"
      style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none'}}
      loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      sandbox="allow-scripts allow-same-origin allow-presentation"
      referrerPolicy="strict-origin-when-cross-origin"
      allowFullScreen
      title="VIDEO_TITLE_ESC"
      aria-label="YouTube video: VIDEO_TITLE_ESC"
    />
  </div>
  <noscript>
    <p><strong>Video:</strong> <a href="https://www.youtube.com/watch?v=VIDEO_ID">VIDEO_TITLE_ESC</a> by CHANNEL_NAME_ESC. DESCRIPTION_EXCERPT_ESC</p>
  </noscript>
</figure>
```

### HTML / WordPress (standard attributes, srcdoc lazy loading)

```html
<figure class="video-embed" style="margin: 2.5rem 0; text-align: center;">
  <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; border-radius: 12px;">
    <iframe
      srcdoc="<style>*{padding:0;margin:0;overflow:hidden}html,body{height:100%}img,span{position:absolute;width:100%;top:0;bottom:0;margin:auto}span{height:1.5em;text-align:center;font:48px/1.5 sans-serif;color:white;text-shadow:0 0 0.5em black}</style><a href='https://www.youtube.com/embed/VIDEO_ID?autoplay=1'><img src='https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg' alt='VIDEO_TITLE_ESC'><span>&#x25BA;</span></a>"
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
      loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      sandbox="allow-scripts allow-same-origin allow-presentation"
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen
      title="VIDEO_TITLE_ESC"
      aria-label="YouTube video: VIDEO_TITLE_ESC">
    </iframe>
  </div>
  <noscript>
    <p><strong>Video:</strong> <a href="https://www.youtube.com/watch?v=VIDEO_ID">VIDEO_TITLE_ESC</a> by CHANNEL_NAME_ESC. DESCRIPTION_EXCERPT_ESC</p>
  </noscript>
</figure>
```

### Standard Markdown (thumbnail link fallback)

```markdown
[![VIDEO_TITLE](https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
*Video: [VIDEO_TITLE](https://www.youtube.com/watch?v=VIDEO_ID) by CHANNEL_NAME*
```

### Hugo

Use the built-in shortcode (do not use raw HTML embeds):

```
{{</* youtube VIDEO_ID */>}}
```

### Next.js Config Note

For MDX projects using YouTube thumbnails, add to `next.config.ts` remotePatterns:

```typescript
{ protocol: 'https', hostname: 'img.youtube.com' }
```

---

## VideoObject JSON-LD Schema

Add a VideoObject to the page `@graph` for each embedded video. Use the stable
`@id` pattern with a video index suffix.

```json
{
  "@type": "VideoObject",
  "@id": "{siteUrl}/blog/{slug}#video-{index}",
  "name": "Video title",
  "description": "Video description excerpt (first 200 chars)",
  "thumbnailUrl": "https://img.youtube.com/vi/{videoId}/hqdefault.jpg",
  "uploadDate": "YYYY-MM-DDTHH:MM:SSZ",
  "contentUrl": "https://www.youtube.com/watch?v={videoId}",
  "embedUrl": "https://www.youtube.com/embed/{videoId}",
  "duration": "PT{M}M{S}S",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": 0
  }
}
```

Replace `{index}` with 1, 2, or 3 matching embed order. Replace
`userInteractionCount` with the numeric view count when available. Include
`duration` in ISO 8601 format (e.g., `PT12M30S` for 12 minutes 30 seconds).

---

## Noscript Fallback for AI Crawlers

Standard crawlers such as GPTBot, PerplexityBot, and ClaudeBot should be assumed
not to execute JavaScript, so YouTube iframes may be invisible to them. The `<noscript>` block
provides a text fallback containing:

- Video title as anchor text linking to YouTube
- Channel name for source attribution
- Description excerpt for topical context

This ensures AI systems can discover and reference the video content even without
rendering the embed. Every video embed must include a noscript fallback.

---

## Graceful Degradation

| Scenario | Behavior |
|----------|----------|
| No GOOGLE_AI_API_KEY available | Use WebSearch `site:youtube.com [topic] [year]` to find videos |
| No suitable videos found | Skip silently, continue blog generation without video |
| API rate limit exceeded | Use cached/previously found videos, or skip |
| Video removed after embedding | Noscript text provides graceful fallback with title and link |
| Embed blocked by privacy settings | srcdoc pattern shows thumbnail placeholder until clicked |
| Reader has JavaScript disabled | Noscript block renders video title, channel, and description |
