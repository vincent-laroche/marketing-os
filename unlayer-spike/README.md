# unlayer-spike

Phase 1/2 verification for the Unlayer drag-and-drop build (#138). Zero dependencies —
plain Node, no install step.

Secrets are read from `~/.env` at runtime by `env.mjs`; nothing here stores or logs a
credential. Requires `UNLAYER_PAT_TOKEN`. Project `289096`.

| Script | Purpose |
|---|---|
| `verify-api.mjs` | Confirms the Cloud API v3 endpoints the build depends on |
| `fetch-schema.mjs` | Downloads the design-JSON schema to `design-schema.json` |
| `fidelity-test.mjs` | **Kill gate.** Six Atelier Zero modules through the exporter, checked for verbatim survival |
| `liquid-test.mjs` | **Kill gate.** Shopify Liquid through the exporter, checked for escaping/encoding damage |

```
node verify-api.mjs && node fetch-schema.mjs && node fidelity-test.mjs && node liquid-test.mjs
```

Both gates passed 2026-09-05. Results recorded on #138.

Note: `templates/export/html` requires `?projectId=` — it returns
`BAD_REQUEST / Missing projectId parameter` without it, even with a valid PAT.
