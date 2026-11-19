# KimpaVita Press

Cloudflare Worker for `kimpavita.diela.org`.

## Components

- Public newsroom and article archive
- D1-backed articles, corrections, and publication log
- JSON Feed at `/feed.json`
- Health check at `/api/health`
- Protected publication endpoint at `POST /api/publish`

The live Worker uses the `DB` D1 binding and a secret `PUBLISH_TOKEN`.
