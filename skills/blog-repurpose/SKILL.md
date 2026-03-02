---
name: blog-repurpose
description: >
  Repurpose blog posts for social media, email, YouTube, Reddit, and LinkedIn.
  Generates Twitter/X threads, LinkedIn articles, YouTube scripts, Reddit
  discussion posts, email newsletter excerpts. Adapts tone for each platform.
  Use when user says "repurpose", "blog repurpose", "share blog", "social media",
  "twitter thread", "linkedin post", "youtube script", "reddit post".
allowed-tools:
  - read_file
  - write_file
  - grep_search
  - glob
---

# Blog Repurpose -- Cross-Platform Content Adaptation

Transforms blog posts into platform-optimized content for social media, email,
video, and community channels. Each output adapts tone, format, and length to
match platform conventions and audience expectations.

## Workflow

### Step 1: Read & Analyze

Read the blog post and extract the core content elements:

- **Title** — Original blog post title
- **Key insights** (5-7) — The most important takeaways, each as a standalone statement
- **Statistics** — All sourced data points with attribution
- **Quotes** — Any notable quotations or expert statements
- **Main argument** — The central thesis in 1-2 sentences
- **TL;DR** — A 2-3 sentence summary that delivers standalone value
- **Target audience** — Who the blog was written for
- **Topic category** — For subreddit and hashtag selection

### Step 2: Ask User

Prompt the user to select which platforms to generate content for:

1. Twitter/X thread
2. LinkedIn article
3. YouTube video script
4. Reddit discussion post
5. Email newsletter excerpt
6. All of the above

If the user specifies a platform directly (e.g., "repurpose for Twitter"),
skip this step and generate for that platform only.

### Step 3: Twitter/X Thread

Generate a complete thread optimized for Twitter/X engagement:

**Hook tweet** (tweet 1):
- Open with a curiosity gap or bold statistic
- Must be under 280 characters
- Should make someone stop scrolling
- Pattern: "[Surprising stat or contrarian take]. Here's what [audience] needs to know:"

**Insight tweets** (tweets 2-6):
- One key point per tweet, each delivering standalone value
- Include a statistic with source where possible
- Use line breaks for readability
- Each tweet should work even if read in isolation

**Closing tweet** (final):
- Summarize the main takeaway in one sentence
- Include a clear CTA linking to the full post
- Add relevant hashtags (maximum 2 per tweet)
- Pattern: "Read the full breakdown: [link]\n\n#hashtag1 #hashtag2"

**Thread formatting rules:**
- Number tweets as 1/, 2/, etc. for clarity
- No tweet exceeds 280 characters
- Thread length: 7-9 tweets total
- Tone: conversational, direct, insight-dense

### Step 4: LinkedIn Article

Adapt the blog for LinkedIn's professional audience and format:

**Length:** 800-1,200 words (shorter than the blog post)

**Opening** (first 2-3 lines visible before "See more"):
- Start with a personal story, observation, or contrarian take
- This is the hook — it must compel clicking "See more"
- Never start with "I'm excited to share..." or similar cliches

**Body structure:**
- Use LinkedIn-native formatting: bold text for emphasis, single-line paragraphs,
  generous line breaks between points
- Numbered lists for key takeaways
- Short paragraphs (1-3 sentences each)
- Include 2-3 key statistics with sources
- More personal and opinion-led than the original blog

**Closing:**
- End with an engagement question that invites comments
- Pattern: "What's your experience with [topic]? I'd love to hear in the comments."
- Do NOT include external links in the body (LinkedIn deprioritizes them)
- Add the blog link in the first comment instead (note this in the output)

**Tone:** Professional but conversational. First-person perspective. Share
what you learned or observed, not just what the data says.

### Step 5: YouTube Script

Generate a complete video script structured for retention:

**Hook** (0-15 seconds):
- Bold statement or surprising question drawn from the blog's strongest insight
- Pattern: "Did you know that [shocking stat]? Today I'm going to show you [promise]."
- Must grab attention before viewers click away

**Intro** (15-60 seconds):
- What viewers will learn (3 bullet points)
- Why it matters right now
- Brief credibility statement
- "[SHOW TITLE CARD]"

**Main content** (3-5 talking points):
- Derived from the blog's H2 sections
- Each section: key point, supporting data, practical example
- Include visual cues throughout:
  - `[SHOW CHART: description]` — for data visualizations
  - `[CUT TO SCREENCAST]` — for demonstrations
  - `[B-ROLL: description]` — for visual variety
  - `[TEXT ON SCREEN: key stat]` — for emphasis
- Transition phrases between sections

**CTA** (final 15-30 seconds):
- Subscribe prompt with reason
- Link to full blog post in video description
- Tease next related video topic

**Script metadata:**
- Estimated duration based on word count (~150 words per minute of speech)
- Suggested title (under 60 chars, keyword-rich)
- Suggested thumbnail concept (text + visual)
- Description with timestamps, blog link, and key takeaways

### Step 6: Reddit Post

Reframe the blog content as an authentic community discussion:

**Subreddit suggestions:**
- Recommend 2-3 relevant subreddits based on the blog topic
- Consider subreddit size, rules, and posting conventions
- Check if the subreddit allows links or prefers text posts

**Post format:**
- Title: Frame as a question or observation, not a blog promotion
  - Good: "After analyzing 500 campaigns, here's what actually drives ROI"
  - Bad: "Check out my new blog post about marketing ROI"
- Lead with a question or interesting observation
- Share key findings as if reporting results to peers
- Use Reddit markdown formatting (headers, bullet points, bold)
- Include 3-5 key data points with sources
- End with a discussion prompt: "Has anyone else seen similar results?"

**Self-promotion compliance:**
- Follow the 10% rule: self-promotional content should be max 10% of posts
- Never use clickbait or misleading titles
- Provide genuine value in the post itself — readers should benefit without
  clicking through
- Include the blog link naturally at the end: "Full analysis with charts: [link]"

**Tone:** Peer-to-peer, humble, discussion-oriented. Never salesy.

### Step 7: Email Newsletter Excerpt

Generate a concise newsletter section optimized for email engagement:

**Subject line:**
- 40-60 characters
- Curiosity-driven or value-driven (not clickbait)
- Pattern options:
  - Curiosity: "The [topic] metric nobody tracks (but should)"
  - Value: "[N] [topic] insights from [source/study]"
  - Urgency: "[Topic] changed this month. Here's what to do."

**Preview text:**
- 40-90 characters that complement (not repeat) the subject line
- Appears after subject in inbox — treat as a second headline

**Body:**
- **TL;DR** (2-3 sentences): Standalone summary with the key takeaway
- **3 key takeaways** (bullet points): Each with a statistic and source
- **CTA**: Clear link to the full blog post
  - Button text: "Read the full analysis" or similar action-oriented phrase

**Total length:** 150-200 words. Every word must earn its place.

**Formatting:**
- Short paragraphs (1-2 sentences)
- Bold key phrases for scanners
- Single CTA (do not compete with multiple links)

### Step 8: Save

Save all generated outputs to the `repurposed/` directory with platform-specific
filenames:

```
repurposed/
  {slug}-twitter-thread.md
  {slug}-linkedin-article.md
  {slug}-youtube-script.md
  {slug}-reddit-post.md
  {slug}-email-newsletter.md
```

If the `repurposed/` directory does not exist, create it.

Present a summary after saving:

```
## Repurposed Content: [Blog Title]

### Generated Outputs
- Twitter/X thread: repurposed/{slug}-twitter-thread.md (X tweets)
- LinkedIn article: repurposed/{slug}-linkedin-article.md (~X words)
- YouTube script: repurposed/{slug}-youtube-script.md (~X min estimated)
- Reddit post: repurposed/{slug}-reddit-post.md (X subreddits suggested)
- Email excerpt: repurposed/{slug}-email-newsletter.md (~X words)

### Quick Stats
- Key insights extracted: X
- Statistics reused: X across Y platforms
- Total content pieces: X

### Next Steps
- Review and customize each piece for your brand voice
- Schedule posts using your preferred social media tool
- For Twitter: post thread during peak hours (9-11am or 1-3pm local time)
- For LinkedIn: post Tuesday-Thursday for highest engagement
- For Reddit: post during US morning hours (8-10am EST)
```
