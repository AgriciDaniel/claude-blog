# TODO - claude-blog Roadmap

## Phase 2 (Next)
- [ ] AI Citation Probability Scoring (0-100 per post for ChatGPT/Perplexity/AI Overview citation likelihood)
- [ ] Writing Style Learning (`/blog style learn` - analyze 5-10 posts to extract author voice profile)
- [ ] Content Decay Detection (`/blog decay` - GSC integration to flag 20%+ QoQ decline)
- [ ] Pre-commit hooks for quality gates (block commits with score < 70)

## Phase 3 (Future)
- [ ] MCP integrations (Ahrefs, Semrush)
- [ ] Automated A/B title testing via analytics integration
- [ ] Content performance dashboard (aggregate scores, traffic, citations)
- [ ] `blog-sxo` skill (Florian Schmitz's SXO methodology, content-side persona scoring; deferred from v1.7.0 pending DataForSEO decoupling)
- [ ] `blog-drift` skill (clean-room baseline + diff for blog content over time; original submission was rejected for hardcoded API key)
- [ ] `docs/COMMANDS.md` sections for the 6 v1.7.0 commands (`cluster`, `multilingual`, `translate`, `localize`, `locale-audit`, `flow`)
- [ ] `skills/blog-cluster/templates/cluster-map.html` reference template (skill currently generates from spec each invocation)

## Completed
- [x] CI/CD workflows (`.github/workflows/ci.yml` added in v1.3.0)
- [x] Google Search Console and PageSpeed Insights (blog-google sub-skill, v1.6.5)
- [x] Plugin marketplace submission (marketplace.json, v1.6.2)
- [x] Image generation via AI (blog-image sub-skill with Gemini, v1.4.0)
- [x] Podcast/audio repurposing (blog-audio sub-skill with Gemini TTS, v1.6.0)
- [x] Multi-language content support (i18n, hreflang generation): `blog-multilingual` + `blog-translate` + `blog-localize` + `blog-locale-audit` (v1.7.0, by Chris Mueller)
- [x] FLOW framework integration (`blog-flow` + `scripts/sync_flow.py`, v1.7.0)
- [x] Semantic topic-cluster planning + execution (`blog-cluster`, v1.7.0, winner of Pro Hub Challenge by Lutfiya Miller)
- [x] Mechanical security guardrails (`tests/test_security_guardrails.py`, v1.7.0)
