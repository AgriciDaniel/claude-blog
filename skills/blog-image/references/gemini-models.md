# Gemini Image Generation Models - Nano Banana

> Last updated: 2026-07-08
> Aligned with Google's July 2026 model availability state. Check live pricing
> and project limits before quoting cost or throughput.

## Available Models

### gemini-3.1-flash-image (Recommended - Speed + Quality)
| Property | Value |
|----------|-------|
| **Model ID** | `gemini-3.1-flash-image` |
| **Tier** | Nano Banana 2 (Flash) |
| **Speed** | Fast - optimized for high-volume use |
| **Aspect Ratios** | All 14 ratios (see table below) |
| **Max Resolution** | Up to 4096×4096 (4K tier) |
| **Features** | Google Search grounding (web + image), thinking levels, image-only output, extreme aspect ratios, 512px drafts |
| **Rate Limits** | Check live project limits in AI Studio and the rate limits page |
| **Output Tokens** | 1K: 1,120, 2K: 1,680, 4K: 2,520 |
| **Cost (1K)** | ~$0.067/image |
| **Best For** | Most blog images, rapid iteration, batch generation |

### gemini-3.1-flash-lite-image (Low Latency)
| Property | Value |
|----------|-------|
| **Model ID** | `gemini-3.1-flash-lite-image` |
| **Tier** | Nano Banana Lite |
| **Speed** | Lowest latency image model |
| **Aspect Ratios** | Standard 14-ratio set in the direct API |
| **Max Resolution** | 1K optimized |
| **Features** | Image generation and editing for high-volume workflows |
| **Rate Limits** | Check current project limits in AI Studio |
| **Output Tokens** | 1K: 1,120 |
| **Cost (1K)** | ~$0.0336/image |
| **Best For** | Low-latency drafts, lightweight edits, high-volume 1K work |

**MCP caveat:** The pinned `@ycse/nanobanana-mcp@1.1.1` package may not accept
this stable model ID. Use direct API or upgrade the MCP package before selecting
Lite from Claude Code.

### gemini-3-pro-image (Highest Quality - Text + Detail)
| Property | Value |
|----------|-------|
| **Model ID** | `gemini-3-pro-image` |
| **Tier** | Nano Banana Pro |
| **Speed** | Slower - uses reasoning before generating (generates interim images internally) |
| **Aspect Ratios** | All 14 ratios |
| **Max Resolution** | Up to 4096×4096 (4K tier) |
| **Features** | Strong text rendering with quoted text, 14 reference images, C2PA Content Credentials |
| **Rate Limits** | Check live project limits in AI Studio and the rate limits page |
| **Output Tokens** | 1K/2K: 1,120, 4K: 2,000 |
| **Cost (1K/2K)** | ~$0.134/image |
| **Best For** | Hero images with text overlays, highest quality final assets, branded content |

**Note:** The preview image ID `gemini-3-pro-image-preview` shut down on 2026-06-25. Use `gemini-3-pro-image`.

### gemini-2.5-flash-image (Stable Fallback)
| Property | Value |
|----------|-------|
| **Model ID** | `gemini-2.5-flash-image` |
| **Tier** | Nano Banana Original (stable) |
| **Speed** | Fast |
| **Aspect Ratios** | Standard ratios vary by API surface, verify in current docs |
| **Max Resolution** | Up to 1024×1024 (1K tier) |
| **Rate Limits** | Check live project limits in AI Studio and the rate limits page |
| **Cost (1K)** | ~$0.039/image |
| **Best For** | Budget-conscious workflows, proven quality, stable fallback |

### Imagen 4 (Deprecated Dedicated Image Models)
| Property | Fast | Standard | Ultra |
|----------|------|----------|-------|
| **Model IDs** | `imagen-4.0-fast-generate-001` | `imagen-4.0-generate-001` | `imagen-4.0-ultra-generate-001` |
| **Pricing** | $0.02/image | $0.04/image | $0.06/image |
| **Speed** | Fastest | Medium | Slowest |
| **Best For** | Batch generation, drafts | General-purpose blog images | Maximum detail, print |

**Status:** Deprecated on 2026-06-15; shutdown scheduled for 2026-08-17. Use `gemini-3.1-flash-image` for current standard image generation, or `gemini-3-pro-image` for highest quality.

**Notes:** Imagen 4 models are dedicated image generators (not multimodal LLMs). They lack conversational editing and should not be used for new workflows.

## Deprecated Models (DO NOT USE)

### gemini-3.1-flash-image-preview
- **Status:** Deprecated on 2026-05-28 and shut down on 2026-06-25. Use `gemini-3.1-flash-image`.

### gemini-3-pro-image-preview
- **Status:** Deprecated on 2026-05-28 and shut down on 2026-06-25. Use `gemini-3-pro-image`.

### gemini-2.5-flash-image-preview
- **Status:** Shut down - use the stable `gemini-2.5-flash-image` variant

### gemini-2.0-flash-exp
- **Status:** Deprecated, shutdown June 1, 2026. Use `gemini-2.5-flash-image`

### Legacy models (Gemini 2.0 Flash and earlier)
- **Status:** Shut down June 1, 2026. Migrate to `gemini-3.1-flash-image` or `gemini-3-pro-image`.

## Model Selection for Blog Content

| Blog Use Case | Recommended Model | Why |
|---------------|-------------------|-----|
| Quick draft / iteration | NB2 Flash (512px) | Fastest, cheapest, good enough for review |
| Standard blog images | NB2 Flash (1K-2K) | Best speed/quality ratio |
| Hero images with text | NB Pro | Strong text rendering and reasoning mode |
| Final hero / OG at 4K | NB2 Flash or Pro (4K) | Both support 4K output |
| High-volume 1K drafts | NB Lite | Lowest latency and lowest 1K image price |
| Budget batch generation | Original (2.5 Flash) | $0.039/img, proven quality |

## Aspect Ratios

All 14 supported ratios. Availability varies by model:

| Ratio | Orientation | Blog Use Cases | NB2 Flash | Pro | Original |
|-------|-------------|---------------|:---------:|:---:|:--------:|
| `1:1` | Square | Social posts, thumbnails | ✅ | ✅ | Verify |
| `16:9` | Landscape | Blog headers, OG images | ✅ | ✅ | Verify |
| `9:16` | Portrait | Stories, Reels, mobile | ✅ | ✅ | Verify |
| `4:3` | Landscape | Product shots, inline | ✅ | ✅ | Verify |
| `3:4` | Portrait | Book covers, portrait | ✅ | ✅ | Verify |
| `2:3` | Portrait | Pinterest pins, posters | ✅ | ✅ | Verify |
| `3:2` | Landscape | DSLR standard, prints | ✅ | ✅ | Verify |
| `4:5` | Portrait | Instagram portrait | ✅ | ✅ | Verify |
| `5:4` | Landscape | Large format | ✅ | ✅ | Verify |
| `1:4` | Tall strip | Vertical banners | ✅ | ✅ | Verify |
| `4:1` | Wide strip | Section dividers, headers | ✅ | ✅ | Verify |
| `1:8` | Extreme tall | Narrow strips | ✅ | ✅ | Verify |
| `8:1` | Extreme wide | Ultra-wide banners | ✅ | ✅ | Verify |
| `21:9` | Ultra-wide | Cinematic headers | ✅ | ✅ | Verify |

## Resolution Tiers

| `imageSize` | Pixel Range | Model Availability | Cost Multiplier | Blog Use |
|-------------|-------------|-------------------|:---------------:|----------|
| `512` | Up to 512×512 | All models | 0.5× | Drafts, quick iteration |
| `1K` (default) | Up to 1024×1024 | All models | 1× | Standard web/social |
| `2K` | Up to 2048×2048 | NB2 Flash, Pro | 2× | Quality inline images |
| `4K` | Up to 4096×4096 | NB2 Flash, Pro | 4× | Print, hero images, final assets |

**Notes:**
- Actual pixel dimensions depend on aspect ratio (e.g., 4K at 16:9 = 4096×2304)
- Default is `1K` if `imageSize` is not specified
- Known bug: `imageSize` sometimes ignored through LiteLLM proxy and in image-to-image workflows

## Rate Limits

Rate limits vary by model, billing tier, region, and project. Check the live
limits table before promising throughput: https://ai.google.dev/gemini-api/docs/rate-limits

| Tier | RPM | RPD | How to Get |
|------|-----|-----|-----------|
| Tier 1 (Pay-as-you-go) | 150-300 | 1,500-10,000 | Enable billing on Google Cloud project |
| Tier 2 ($250+ spend) | 1,000+ | Unlimited | Cumulative $250+ API spend |

**Important:** The old NB2 and Pro preview image IDs are shut down. Free tier
availability for image generation may require billing to be enabled.

## Pricing Guidance

Check live pricing before quoting image costs:
https://ai.google.dev/gemini-api/docs/pricing

| Model | Resolution | Cost per Image | Notes |
|-------|-----------|---------------|-------|
| NB Lite | 1K | ~$0.0336 | Direct API, 1K optimized |
| NB2 Flash | 1K | ~$0.067 | Standard |
| NB2 Flash | 2K | ~$0.101 | Higher resolution |
| NB2 Flash | 4K | ~$0.151 | Highest Flash tier |
| Pro | 1K/2K | ~$0.134 | Premium quality |
| Pro | 4K | ~$0.24 | Premium 4K |
| Original (2.5) | 1K | ~$0.039 | Budget option |
| Imagen 4 Fast | - | $0.02 | Deprecated, shutdown 2026-08-17 |
| Imagen 4 Standard | - | $0.04 | Deprecated, shutdown 2026-08-17 |
| Imagen 4 Ultra | - | $0.06 | Deprecated, shutdown 2026-08-17 |
| Batch API | Any | 50% discount | Asynchronous, higher latency |

**Cost optimization:** Use 512px for drafts (cheapest), 1K for standard blog images, reserve 2K-4K for hero images and final assets.

Pricing source: https://ai.google.dev/gemini-api/docs/pricing

## Multi-Image Input

| Feature | Limit | Notes |
|---------|-------|-------|
| Object references | Up to 6 | Style, composition, visual matching |
| Character references | Up to 5 | Assign names to preserve features |
| Total references | Up to 14 | Combined across types |
| Max input image size | 7 MB | Per image |

Useful for brand-consistent blog imagery: provide brand style references to maintain visual identity across generated images.

## Safety Filters - Dual Layer Architecture

### Layer 1: Input Filters (Configurable)
Standard harm category filtering via `safetySettings` API parameter. Covers hate speech, harassment, sexually explicit, and dangerous content.

### Layer 2: Output Filters (NON-CONFIGURABLE)
Server-side analysis of the **generated image itself**. Cannot be disabled through any API parameter.
- Returns `finishReason: "IMAGE_SAFETY"` (distinct from `"SAFETY"`)
- Known to be overly cautious - Google acknowledged "filters became way more cautious than we intended"
- Benign prompts like "dog" or "bowl of cereal" have been blocked
- Celebrity blocking tightened significantly with NB2

| `finishReason` | Meaning | Layer | Retryable? |
|----------------|---------|:-----:|:----------:|
| `STOP` | Successful generation | - | N/A |
| `IMAGE_SAFETY` | Output blocked by Layer 2 | 2 | Rephrase prompt |
| `PROHIBITED_CONTENT` | Content policy violation | 1 | No - topic blocked |
| `SAFETY` | General safety block | 1 | Rephrase prompt |
| `RECITATION` | Detected copyrighted content | 2 | Rephrase prompt |

**No workaround exists for Layer 2 blocks beyond rephrasing the prompt.**

## Content Credentials

- **SynthID watermarks** are always embedded (invisible, machine-readable). Survives rescaling, compression, and most edits - cannot be disabled
- **C2PA Content Credentials** are embedded on Nano Banana Pro images from Gemini App, Vertex AI, and Google Ads

## Blog Image Post-Processing

| Step | Target | Tool |
|------|--------|------|
| Generate | 2K resolution | Gemini API |
| Convert | WebP or AVIF, check current browser baseline before relying on either format alone | ImageMagick or Sharp |
| Fallback | JPEG or PNG fallback for channels with unknown support | ImageMagick |
| Hero size | 1920x1080 (16:9) or 1200x630 (OG) | Resize |
| Inline size | < 200KB compressed | Quality adjustment |
| Hero size | < 500KB compressed | Quality adjustment |
| Metadata | Remove private EXIF only after verifying SynthID and C2PA behavior | `c2patool`, ImageMagick |

## Key Limitations
- No native transparent backgrounds (workaround: prompt green background, then chromakey removal)
- Text rendering quality varies - keep text under 25 characters for best results
- Safety filters may block benign prompts - use auto-rephrase workflow
- Session context resets between Claude Code conversations
- `imageSize` and thinking level depend on MCP package version support
- No video generation (use Veo 3.1 for image-to-video workflows)
