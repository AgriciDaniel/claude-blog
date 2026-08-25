# YouTube Video Embed Reference

## Why YouTube Embeds Matter

Video can help readers when a demonstration, walkthrough, or expert explanation
adds information the article cannot communicate as effectively in text or
images. Vendor datasets report associations between video mentions and measured
visibility, but those observations are non-causal, time-bound, and not ranking
or readiness bonuses.

Embed a video only when it is relevant, accurate, accessible, and useful. Skip
video when available options are stale, low quality, off-topic, duplicative, or
distracting.

---

## Video Quality Criteria

### Suitability Review

| Criterion | Review Question |
|-----------|-----------------|
| Relevance | Does the video directly support the section's reader task? |
| Accuracy | Are material claims current and verifiable? |
| Added value | Does it demonstrate or explain something beyond the surrounding text? |
| Accessibility | Are accurate captions or a useful transcript available? |
| Source transparency | Is the creator identifiable and are conflicts disclosed? |
| User experience | Is the embed performant, privacy-conscious, and non-disruptive? |

Views, likes, channel size, age, and duration may provide context, but none is a
universal quality threshold or citation-readiness score.

---

## Embed Placement Strategy

| Position | Video Purpose | When |
|----------|--------------|------|
| After introduction (before first H2 body) | Overview / explainer | Only if it adds immediate context |
| Mid-article (after 2nd or 3rd H2) | Tutorial / demo / how-to | If video shows a process |
| Before FAQ or conclusion | Summary or expert opinion | Optional 3rd video |

### Placement Rules

- Use only as many videos as the reader task warrants
- Space embeds according to surrounding content and page usability, not a word quota
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
