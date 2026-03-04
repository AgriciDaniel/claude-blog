# Tutorial: The `gemini-blog` 7-Phase Workflow

This tutorial breaks down the entire lifecycle of how the `gemini-blog` engine operates, from your first idea to a fully optimized, published post.

The engine uses a combination of an Orchestrator (`blog/GEMINI.md`), 12 specific templates, 4 subagents, and Python safety metrics to ensure your content ranks on Google and is cited by AI engines like ChatGPT.

---

## Phase 1: Strategy & Ideation
**Commands to use:** `/blog strategy <niche>`, `/blog calendar`

* **What happens:** You provide a niche or general topic.
* **Behind the scenes:** The engine loads `google-landscape-2026.md` and `geo-optimization.md` to ensure the strategy aligns with the latest Search and AI algorithms.
* **The output:** It groups topics into semantic "clusters" and builds an editorial calendar, focusing on a 60/30/10 content mix and plotting out decay detection.

## Phase 2: Outlining & Briefing
**Commands to use:** `/blog brief <topic>`, `/blog outline <topic>`

* **What happens:** The **Research Agent** (`blog-researcher`) is spawned. It uses WebSearch and WebFetch tools to scrape current SERPs, identifying competitive gaps.
* **Behind the scenes:** The system auto-selects 1 of 12 internal templates (e.g., `listicle.md`, `case-study.md`, `pillar-page.md`) based on the target search intent.
* **The output:** You receive a skeletal structure requiring H2s to be phrased as questions (target: 60-70% question-based subheadings).

## Phase 3: Content Generation (Writing/Rewriting)
**Commands to use:** `/blog write <topic>`, `/blog rewrite <file>`

* **What happens:** The heavy lifting begins.
* **Behind the scenes:** 
  1. **Researcher Agent** runs first, scraping Tier 1-3 sources (e.g., .gov, .edu, reputable news) to gather 8-12 hard statistics and sourcing 3-5 images via Pixabay/Unsplash (verifying the URLs return HTTP 200).
  2. The **Built-in `blog-chart` skill** is invoked under the hood to generate visually engaging, dark-mode SVG charts (e.g., donut, lollipop) mapped to the data.
  3. The **Writer Agent** (`blog-writer`) takes over with strict Quality Gates:
     - **Answer-First Formatting:** Every H2 *must* open with a 40-60 word paragraph containing a direct answer and a cited statistic.
     - **Paragraph Discipline:** Hard limits of max 150 words per paragraph, ~15-20 words per sentence.
     - **Information Markers:** Injects `[ORIGINAL DATA]` and `[PERSONAL EXPERIENCE]` tags to signal unique value.
     - **AI Evasion:** Deliberately mixes sentence lengths, avoids heavily abused LLM phrases, and self-checks readability scores.
* **The output:** A complete draft with a "TL;DR Box" and "Citation Capsules" optimized for AI web crawlers to instantly extract answers.

## Phase 4: On-Page Optimization
**Commands to use:** `/blog seo-check <file>`

* **What happens:** The **SEO Agent** (`blog-seo`) conducts a validation pass on the final draft.
* **Behind the scenes:** It checks title length (50-60 chars), meta descriptions (150-160 chars, must include a stat), and asserts there are no skipped heading levels (H1 -> H2 -> H3).
* **The output:** A checklist ensuring target keywords are distributed naturally without stuffing.

## Phase 5: Verification & Scoring
**Commands to use:** `/blog analyze <file>`, `/blog audit [directory]`

* **What happens:** The **Reviewer Agent** OR the **Python Script** (`analyze_blog.py`) is invoked to audit the post.
* **Behind the scenes:** It triggers the **5-Category, 100-Point Quality Rubric**:
  - Content Quality (30 pts)
  - SEO Optimization (25 pts)
  - E-E-A-T Signals (15 pts)
  - Technical Elements (15 pts)
  - AI Citation Readiness (15 pts)
* **The output:** If the score is below 60, the post is flagged for a "Rewrite". If >80, it is flagged as "Strong" or "Exceptional".

## Phase 6: Technical Injection
**Commands to use:** `/blog schema <file>`, `/blog geo <file>`

* **What happens:** The system creates structural data for web crawlers (like Googlebot, ClaudeBot, Google-Extended).
* **Behind the scenes:** It uses HTML/JSON-LD insertion to embed structured `BlogPosting`, `Person` (author trust for E-E-A-T), and `FAQSchema` markup.
* **The output:** Rich schema directly embedded into your detected platform (MDX, Hugo, WordPress, etc.).

## Phase 7: Off-Site Distribution
**Commands to use:** `/blog repurpose <file>`

* **What happens:** The finished article is passed back to the writer/marketer tools.
* **The output:** The content is chopped up into Twitter threads, LinkedIn thought-leadership posts, Reddit submissions, or YouTube scripts--completing the lifecycle and driving traffic back to your blog.

---

## Using the Extension in Gemini CLI

To install and run the `gemini-blog` extension:

1. **Install the Extension:**
   Navigate to the project root and run the installation command. When prompted, confirm that you trust the folder:
   ```bash
   cd gemini-blog
   gemini extensions install .
   ```
   *(Note: You can verify the successful loading of all skills and agents via `gemini extensions list`, which should show the 4 agents without any "Invalid tool name" errors).*

2. **Execute a Workflow in the CLI:**
   You can run the engine interactively or pass commands via a standard shell. For example, you can safely pipe a request to the analysis skill using YOLO (auto-approve) mode and SGE standard outputs:
   ```bash
   echo "analyze the blog post at ./sample-post.md using the blog-analyze skill and give me the quality score" | gemini -y
   ```
   The engine will spin up the necessary components, apply the quality rubric (including SGE optimization logic), and return a highly detailed grading report representing true end-to-end task fulfillment.

