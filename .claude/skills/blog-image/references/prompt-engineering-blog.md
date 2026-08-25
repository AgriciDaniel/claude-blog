# Prompt Engineering Reference - Blog Image Generation

> Load on-demand when constructing complex prompts for blog images.
> Adapted from Banana Claude's prompt engineering system for blog-specific use cases.
> Aligned with Google's March 2026 "Ultimate Prompting Guide" for Gemini image generation.

## The 6-Component Reasoning Brief

Every image prompt should contain these components, written as natural
narrative paragraphs - NEVER as comma-separated keyword lists.

### 1. Subject
The main focus of the image. Describe with physical specificity.

**Good:** "A weathered Japanese ceramicist in his 70s, deep sun-etched
wrinkles mapping decades of kiln work, calloused hands cradling a
freshly thrown tea bowl with an irregular, organic rim"

**Bad:** "old man, ceramic, bowl"

### 2. Action
What is happening. Movement, pose, gesture, state of being.

**Good:** "leaning forward with intense concentration, gently smoothing
the rim with a wet thumb, a thin trail of slip running down his wrist"

**Bad:** "making pottery"

### 3. Context
Environment, setting, temporal and spatial details.

**Good:** "inside a traditional wood-fired anagama kiln workshop,
stacked shelves of drying pots visible in the soft background, late
afternoon light filtering through rice paper screens"

**Bad:** "workshop, afternoon"

### 4. Composition
Camera angle, shot type, framing, spatial relationships.

**Good:** "intimate close-up shot from slightly below eye level,
shallow depth of field isolating the hands and bowl against the
soft bokeh of the workshop behind"

**Bad:** "close up"

### 5. Lighting
Light source, quality, direction, temperature, shadows.

**Good:** "warm directional light from a single high window camera-left,
creating gentle Rembrandt lighting on the face with a soft triangle
of light on the shadow-side cheek, deep warm shadows in the workshop"

**Bad:** "natural lighting"

### 6. Style
Art medium, aesthetic reference, technical photographic details.

**Good:** "captured with a Sony A7R IV, 85mm f/1.4 GM lens, Kodak Portra
400 color grading with lifted shadows and muted earth tones, reminiscent
of Dorothea Lange's documentary portraiture"

**Bad:** "photorealistic, 8K, masterpiece"

## Blog Image Types

Map blog use cases to domain modes and aspect ratios:

| Image Type | Aspect Ratio | Domain Mode | Prompt Focus |
|------------|-------------|-------------|-------------|
| Hero/Cover | 16:9 | Editorial or Landscape | Wide composition, mood-setting, topic-relevant |
| OG/Social Card | 16:9 (1200x630) | Editorial or Infographic | Clean, readable at small sizes, topic icon |
| Inline Illustration | 16:9 or 4:3 | Varies by topic | Supports adjacent H2 content, contextual |
| Inline Product Shot | 4:3 or 1:1 | Product | Clean background, product focus |
| Section Divider | 21:9, then crop | Abstract or Landscape | Wide strip, atmospheric, non-distracting |

## Blog-Specific Prompt Templates

### Hero/Cover Image
```
A [photorealistic/editorial] wide establishing shot of [topic-relevant scene],
[action or state that conveys the article's core message]. Set in [environment
with specifics that match blog topic]. [Wide, balanced composition with rule of
thirds]. [Dramatic or inviting lighting] creating [mood that matches article tone].
[Style reference appropriate to blog niche]. Aspect ratio 16:9, suitable as a
blog hero image at 1200x630 or 1920x1080.
```

### Inline Illustration
```
A [style] [shot type] of [specific element from the blog section], [illustrating
the concept of the adjacent heading]. [Contextual environment]. [Clear, well-lit
composition that works at medium size]. [Color palette complementing blog design].
```

### Social/OG Card Image
```
A [clean, high-contrast] [format] showing [key visual concept of the article],
[simplified for recognition at thumbnail size]. [Minimal background, strong focal
point]. [Bold lighting that reads well at small sizes]. Text-free, designed for
social sharing preview at 1200x630.
```

## Domain Mode Libraries (Blog-Relevant)

### Editorial Mode
Best for: Blog headers, feature images, lifestyle content, storytelling.
**Publication refs:** National Geographic, Kinfolk, The Atlantic, Wired
**Styling notes:** layered textures, clean compositions, atmospheric depth
**Locations:** contextual to blog topic - offices, workshops, nature, urban
**Mood:** authoritative, inviting, professional

### Product Mode
Best for: E-commerce blogs, product reviews, comparison articles, tech posts.
**Surfaces:** polished marble, brushed concrete, raw linen, acrylic riser, gradient sweep
**Lighting:** softbox diffused, hard key with fill card, rim separation, tent lighting
**Angles:** 45-degree hero, flat lay, three-quarter, straight-on
**Style refs:** Apple product photography, Aesop minimal, clean and modern

### Landscape Mode
Best for: Environmental backgrounds, travel blogs, atmospheric hero sections.
**Depth layers:** foreground interest, midground subject, background atmosphere
**Atmospherics:** fog, mist, haze, volumetric light rays, dust particles
**Time of day:** blue hour (pre-dawn), golden hour, magic hour (post-sunset)
**Weather:** dramatic storm clouds, clearing after rain, sun-dappled

### UI/Web Mode
Best for: Tech blog icons, feature illustrations, app screenshots, diagrams.
**Styles:** flat vector, isometric 3D, line art, glassmorphism, material design
**Colors:** specify exact hex or descriptive palette (e.g., "cool blues #2563EB to #1E40AF")
**Sizing:** design at 2x for retina, specify exact pixel dimensions needed
**Backgrounds:** transparent (request solid white then post-process), gradient, solid color

### Infographic Mode
Best for: Data-driven posts, process explanations, comparison visuals.
**Layout:** modular sections, clear visual hierarchy, bento grid, flow top-to-bottom
**Text:** use quotes for exact text, descriptive font style, specify size hierarchy
**Data viz:** bar charts, pie charts, flow diagrams, timelines, comparison tables
**Colors:** high-contrast, accessible palette, consistent with blog brand

### Abstract Mode
Best for: Pattern backgrounds, section dividers, decorative headers, mood pieces.
**Geometry:** fractals, voronoi tessellation, spirals, organic flow, crystalline
**Textures:** marble veining, fluid dynamics, smoke wisps, ink diffusion, watercolor bleed
**Color palettes:** analogous harmony, complementary clash, monochromatic gradient
**Styles:** generative art, procedural, macro photography of materials

## Search-Grounded Generation (NB2 Feature)

For blog images that need real-world accuracy (current products, real locations,
data-driven infographics), use Google Search grounding with this 3-part formula:

```
[Source/Search request] + [Analytical task] + [Visual translation]
```

**Example:** "Search for the top 5 AI coding tools by GitHub stars in 2026, analyze their relative popularity, then generate a clean infographic comparison chart in a modern dark theme."

Requires `googleSearch` enabled in a direct API call or an MCP package version
that explicitly exposes search-grounded image generation. Verify support before
promising grounded output.

## Advanced Techniques

### Text-First Hack
For images with text, establish the concept conversationally FIRST ("I need a header with 'AI Search 2026'"), then generate. Always enclose text in quotation marks. The model anchors on text mentioned early in the conversation.

### Camera Hardware Naming
Name real camera hardware for precise aesthetics: "Sony A7III, 85mm f/1.4 lens" locks precise bokeh better than "shallow depth of field with bokeh".

### Character Consistency (Multi-turn)
Use `gemini_chat` and maintain descriptive anchors:
- First turn: Generate character with exhaustive physical description
- Following turns: Reference "the same character" + repeat 2-3 key identifiers
- Key identifiers: hair color/style, distinctive clothing, facial feature

### Text Rendering Tips
- Quote exact text: `with the text "OPEN DAILY" in bold condensed sans-serif`
- **25 characters or less** - practical limit for reliable rendering
- **2-3 distinct phrases max** - more text fragments degrade quality
- Describe font characteristics, not font names
- Specify placement: "centered at the top third", "along the bottom edge"
- High contrast: light text on dark, or vice versa

### Positive Framing (No Negative Prompts)
Gemini does NOT support negative prompts. Rephrase exclusions:
- Instead of "no blur" → "sharp, in-focus, tack-sharp detail"
- Instead of "no people" → "empty, deserted, uninhabited"
- Instead of "no text" → "clean, uncluttered, text-free"

## Creative Director Prompting (Advanced)

For premium blog hero images, specify all 4 professional dimensions:

### 1. Lighting Direction
- Studio: softbox at 45 degrees, rim light for separation
- Dramatic: single hard light with deep shadows
- Natural: golden hour, overcast diffusion, window light
- Flat: even illumination for product/editorial clarity

### 2. Camera & Lens Control
- Specify hardware: "shot on Sony A7IV with 85mm f/1.4"
- Focal length affects perspective: 24mm (wide, dramatic) vs 85mm (compressed, flattering)
- Depth of field: f/1.4 (dreamy bokeh) vs f/8 (sharp throughout)
- Distance: close-up (texture detail) vs establishing (context)

### 3. Film Stock & Color Grading
- Nostalgic: Kodak Portra 400 (warm skin tones, soft pastels)
- Modern: Fuji Pro 400H (cooler tones, clean shadows)
- Cinematic: teal-and-orange grading, crushed blacks
- Clean: neutral white balance, minimal grading

### 4. Material & Texture Definition
- Specify surfaces: "brushed aluminum", "rough linen", "polished marble"
- Fabric: "crisp cotton", "worn denim", "sheer silk"
- Environmental: "morning dew on glass", "rain-streaked concrete"
- Detail level influences realism and visual interest

## Common Prompt Mistakes

1. **Keyword stuffing** - "8K, masterpiece, best quality" adds nothing to Gemini
2. **Tag lists instead of prose** - Gemini wants narrative, not "red car, sunset, cinematic"
3. **Missing lighting** - Single biggest quality differentiator; always specify
4. **No composition direction** - Results in generic centered framing
5. **Ignoring aspect ratio** - Always call `set_aspect_ratio` before generating
6. **Overlong prompts** - Diminishing returns past ~200 words; be precise
7. **Text > 25 chars** - Rendering degrades; use text-first hack for accuracy
8. **Not iterating** - Use `gemini_chat` for refinement instead of re-generating
