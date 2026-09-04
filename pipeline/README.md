# pipeline/ — the 1440 Intelligence Platform pipeline

Python package `intel`. Stages per the build brief (`1440_CLAUDE_CODE_BUILD_BRIEF.md` §6):
scan → parse → freshness → blocklist/dedup → score → verify → write → audit → render → send → log.
Everything is written to the shared Postgres database (schema in `db/versions/`).

## Local setup

```bash
pip install -e "pipeline[dev,render]"
export DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/intel
alembic -c db/alembic.ini upgrade head
pytest pipeline/tests            # no DATABASE_URL? tests bootstrap a temp Postgres from local binaries
ruff check --config pipeline/pyproject.toml pipeline db
```

## Configuration

All knobs are environment variables read by `intel/config.py` (`Settings`). Secrets never have defaults.

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | local postgres | SQLAlchemy URL |
| `ANTHROPIC_API_KEY` | — | required for scan / write / verify |
| `SCAN_MODEL` / `WRITER_MODEL` / `VERIFY_MODEL` | sonnet-5 / sonnet-5 / opus-5 | per-stage models (§4) |
| `MD_THRESHOLD` | 70 | minimum score to produce a brief (§6.4) |
| `FRESHNESS_DAYS_TRACK1` / `FRESHNESS_DAYS_ALUMNI` | 14 / 90 | trigger windows (§6.2) |
| `DEDUP_WINDOW_DAYS` | 30 | surfaced_log lookback (§6.3) |
| `EXECUTION_MODE` | shadow | `production` (MD on distribution) / `shadow` (operator only) / `dry_run` |
| `OPERATOR_EMAIL` / `MD_EMAIL` | — | distribution (§7) |
| `GRAPH_TENANT_ID` / `GRAPH_CLIENT_ID` / `GRAPH_CLIENT_SECRET` / `GRAPH_SENDER` | — | Microsoft Graph sendMail |

## Structural guarantees (in the database, not in prompts)

- `surfaced_log` is unique on `(company_norm, trigger_reason_norm)` — the dedup rule (§3.2).
- `briefs.brief_number` is a Postgres sequence — never reused, even after a rollback.
- At most one non-blocked brief per `run_date` (partial unique index) — idempotent days (§9.8).
- `sends` is unique on `(brief_id, recipient, kind)` — a brief is never sent twice (§7).
- `company_norm` (`intel/normalise.py`) maps "Lime" and "Lime (Neutron Holdings)" to one key (§9.3).
