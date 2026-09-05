# Source Manifest Template

```json
{
  "brain_schema": "claude-blog-brain.v1",
  "required_fields": [
    "source_id",
    "path",
    "url",
    "sha256",
    "hash_algorithm",
    "retrieved",
    "source_type",
    "sensitivity",
    "license",
    "description",
    "immutable"
  ],
  "path_rules": {
    "base": ".raw/sources/",
    "must_be_vault_relative": true,
    "disallow_absolute_paths": true,
    "disallow_parent_traversal": true,
    "disallow_symlink_escape": true
  },
  "hash_rules": {
    "hash_algorithm": "sha256",
    "raw_snapshot_sha256_must_match_file": true
  },
  "sources": [
    {
      "source_id": "example-source-id",
      "path": ".raw/sources/example.csv",
      "url": "https://example.org/source",
      "sha256": "<sha256>",
      "hash_algorithm": "sha256",
      "retrieved": "YYYY-MM-DD",
      "source_type": "manual-export",
      "owner": "Daniel Agrici",
      "sensitivity": "public | private-client | credential-risk | restricted",
      "license": "URL or SPDX-like license label",
      "immutable": true,
      "description": "One-line description of the captured file.",
      "notes": "What this source proves and what it does not prove."
    }
  ]
}
```

Every manifest path must be normalized before write, vault-relative, and inside
`.raw/sources/`. `hash_algorithm` must be `sha256`; ledger entries that rely on
captured files must copy the digest into `raw_snapshot_sha256` and record the
same vault-relative path in `raw_snapshot_path`.

Do not record secrets, cookies, tokens, credential exports, or private client
files unless a separate private-vault process explicitly allows that source
class.
