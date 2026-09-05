# TODO - claude-blog Roadmap

## Phase 2 (Next)
- [x] AI Citation Readiness Heuristic (non-calibrated 0-100 editorial views for ChatGPT, Perplexity, and AI Overview; v1.10.0, truthfulness refresh v2.1.0)

## Phase 3 (Future)
- [ ] MCP integrations (Ahrefs, Semrush)
- [ ] Automated A/B title testing via analytics integration
- [ ] Content performance dashboard (aggregate scores, traffic, citations)
- [ ] `blog-sxo` skill (Florian Schmitz's SXO methodology, content-side persona scoring; deferred from v1.7.0 pending DataForSEO decoupling)
- [ ] `blog-drift` skill (clean-room baseline + diff for blog content over time; original submission was rejected for hardcoded API key)
- [ ] `docs/COMMANDS.md` sections for the 6 v1.7.0 commands (`cluster`, `multilingual`, `translate`, `localize`, `locale-audit`, `flow`)
- [ ] `skills/blog-cluster/templates/cluster-map.html` reference template (skill currently generates from spec each invocation)

## Completed
- [x] Writing Style Learning (`/blog style learn`, v1.10.0)
- [x] Content Decay Detection (`/blog decay`, v1.10.0)
- [x] Pre-commit quality gate with the default score threshold of 70 (`scripts/quality_gate.py`, v1.10.0)
- [x] CI/CD workflows (`.github/workflows/ci.yml` added in v1.3.0)
- [x] Google Search Console and PageSpeed Insights (blog-google sub-skill, v1.6.5)
- [x] Plugin marketplace submission (marketplace.json, v1.6.2)
- [x] Image generation via AI (blog-image sub-skill with Gemini, v1.4.0)
- [x] Podcast/audio repurposing (blog-audio sub-skill with Gemini TTS, v1.6.0)
- [x] Multi-language content support (i18n, hreflang generation): `blog-multilingual` + `blog-translate` + `blog-localize` + `blog-locale-audit` (v1.7.0, by Chris Mueller)
- [x] FLOW framework integration (`blog-flow` + `scripts/sync_flow.py`, v1.7.0)
- [x] Semantic topic-cluster planning + execution (`blog-cluster`, v1.7.0, winner of Pro Hub Challenge by Lutfiya Miller)
- [x] Mechanical security guardrails (`tests/test_security_guardrails.py`, v1.7.0)
