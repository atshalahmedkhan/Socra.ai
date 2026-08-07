# Scripts

Repository-level helper scripts.

| Script | Purpose |
| --- | --- |
| `check-env.sh` | Verify a `.env` file defines every key in `.env.example`. |

```bash
chmod +x scripts/check-env.sh
scripts/check-env.sh backend/.env
```

Model-specific benchmark and verification scripts have moved to
`model/benchmarks/scripts/`. The legacy static-site config generator has moved
to `legacy/scripts/`.
