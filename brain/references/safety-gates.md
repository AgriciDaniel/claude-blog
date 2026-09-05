# Safety Gates

V1 is read-only and advisory unless a future release explicitly adds approved,
reversible mutation.

## Refusal Rules

- No ranking or traffic guarantee; content outcomes are probabilistic and never certain
- No credentials, tokens, API keys, or private client content in repo artifacts
- No mutation of a CMS, GSC, GA4, or publishing platform; the brain is advisory and read-only
- No recommendation without a dated source, confidence level, and rollback note
- No deprecated advice (HowTo schema, retired FAQ rich results, FID) presented as current
- No fabricated or unsourced statistics and no generic, unsupported, or low-quality generated filler presented as fact

## Safety Risks

- Stale Google algorithm, E-E-A-T, or schema-deprecation requirements presented as current
- Fabricated, unsourced, or low-quality generated statistics written into published content
- Private client content, draft URLs, or credentials leaking into raw inputs or reports
- Overconfident content recommendations from thin or single-source inputs
- Generated reports leaking local filesystem paths

## Release-Blocking Gates

- Current trustworthy sources are missing.
- Raw source provenance is missing.
- Deliverables contain unsupported claims.
- Credentials or private client data are present.
- A mutation path exists without approval and rollback.
