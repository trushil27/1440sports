# 1440 Intelligence Platform — operator runbook

The code lives in this repo (`pipeline/`, `api/`, `web/`, `db/`); the spec it implements is
`1440_CLAUDE_CODE_BUILD_BRIEF.md`. This runbook is the shortest path from the repo to a
running shadow-mode system, then cut-over. Nothing here stores a secret — every credential
goes into the hosting platform's variable store.

## 0. What exists

| Part | Where | Runs on |
|---|---|---|
| Pipeline (scan → verify → write → audit → render → send) | `pipeline/intel/`, entry `python -m intel.schedule` | Railway cron (fallback: GitHub Actions `daily-run.yml`) |
| Database + migrations | `db/` (Alembic) | Railway Postgres |
| API | `api/intel_api/`, entry `uvicorn intel_api.app:get_app --factory` | Railway service |
| Web app (PWA) | `web/` | Vercel |
| Reference data seeds | `pipeline/intel/seeds/` — `python -m intel.seed` | run after migrations |
| History backfill | `pipeline/intel/backfill.py` — `python -m intel.backfill` | run once |

## 1. Variables (no defaults for secrets)

Pipeline + API share one environment:

```
DATABASE_URL=postgresql+psycopg://…            # Railway Postgres
ANTHROPIC_API_KEY=…                            # scan (sonnet-5), write (sonnet-5), verify (opus-5)
SCAN_MODEL / WRITER_MODEL / VERIFY_MODEL        # optional overrides
EXECUTION_MODE=shadow                           # shadow until M8; then production
OPERATOR_EMAIL=trushil.jani@1440sports.com
MD_EMAIL=ricky.paugh@1440sports.com             # only used in production mode
MD_THRESHOLD=70                                 # brief-production threshold (§6.4)
GRAPH_TENANT_ID / GRAPH_CLIENT_ID / GRAPH_CLIENT_SECRET / GRAPH_SENDER   # Mail.Send app permission (§11.2)
GRAPH_REFRESH_TOKEN                             # only if IT will not grant app consent (delegated fallback)
PDF_STORAGE_DIR=/data/briefs                    # a Railway volume until object storage is wired
APP_BASE_URL=https://intel.1440sports.com       # link target in emails
# API only
APP_SECRET_KEY=<long random>                    # signs sessions, magic links, WebAuthn challenges
APP_USERS=trushil.jani@1440sports.com:operator:Trushil,ricky.paugh@1440sports.com:md:Ricky
APP_RP_ID=intel.1440sports.com                  # WebAuthn relying party = the web app host
APP_ORIGIN=https://intel.1440sports.com
API_BASE_URL=https://intel.1440sports.com       # the web app proxies /auth and /api to the API
APP_COOKIE_SECURE=true
```

## 2. First deploy (M1–M5 acceptance)

1. **Railway**: create a project from this repo with `railway.json` (root `Dockerfile` — if the
   build log mentions Railpack, set Settings → Build → Builder to *Dockerfile*; cron
   `30 4,5 * * *` — both UTC firings; the job itself keeps only the 05:30 Europe/London one).
   Add a Postgres plugin and a volume mounted at `PDF_STORAGE_DIR`. Set the variables above
   (Railway's `postgresql://` `DATABASE_URL` is accepted as-is; the code pins the psycopg driver).
   The container entrypoint runs `alembic upgrade head` and `python -m intel.seed` on every
   start, so a healthy deploy log begins `[entrypoint] applying migrations` →
   `Running upgrade -> 0001 … 0003` → seed counts → `[entrypoint] starting`.
2. **Graph consent**: Entra app registration → API permissions → Microsoft Graph → *Application* →
   `Mail.Send` → grant admin consent; Exchange Application Access Policy scoped to
   `GRAPH_SENDER`. (See `scheduling/SCHEDULE_SETUP.md` for the click path.)
   **No tenant admin available?** Use delegated auth on the sender's own mailbox instead —
   same app registration, same code path:
   - API permissions: remove the *Application* `Mail.Send` row; add *Delegated*
     `Mail.Send`, `Mail.ReadWrite` (draft-then-send + outreach drafts) and `offline_access`.
   - Authentication → *Allow public client flows* = **Yes** (enables the device-code sign-in).
   - Sign in once with the device-code flow and keep the refresh token:
     ```
     curl -X POST https://login.microsoftonline.com/<tenant>/oauth2/v2.0/devicecode \
       -d "client_id=<client id>" \
       -d "scope=https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Mail.ReadWrite offline_access"
     # open the verification_uri, enter user_code, sign in as GRAPH_SENDER, then:
     curl -X POST https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token \
       -d "grant_type=urn:ietf:params:oauth:grant-type:device_code" \
       -d "client_id=<client id>" -d "device_code=<device_code from the first reply>"
     ```
   - Set `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_SENDER` and `GRAPH_REFRESH_TOKEN`
     (the `refresh_token` from the second reply). Leave `GRAPH_CLIENT_SECRET` unset for a
     public client. Mail goes out from `GRAPH_SENDER`'s mailbox via `/me`.
   - The token stays valid while it is used (daily); if a [RUN FAILED] email ever shows
     `invalid_grant`, repeat the two commands and update `GRAPH_REFRESH_TOKEN`.
3. **Smoke run** (any time of day): `python -m intel.schedule --force --no-wait` on the Railway
   service. In shadow mode the operator receives the [SHADOW]/[REVIEW]/[NO SIGNAL] email; the MD
   receives nothing.
4. **Shadow mode** = three consecutive 06:00 deliveries to the operator with no fabrication and no
   duplicate. Check `/ops` (runs, candidate reasons, review queue) each morning.

## 3. Backfill (M6)

Run once against the Railway database:

```
python -m intel.backfill                      # n8n Daily Signals log (128) + this repo's 35 briefs
python -m intel.backfill --pdfs /data/drops   # optional: Outlook/Railway PDFs named <YYYY-MM-DD>_<company>.pdf
python -m intel.backfill --restart-sequence 121   # first free n8n-continuation number (last known: 120)
```

Historical briefs are numbered negatively and marked "historical, unverified"; their original
labels (e.g. `N° 017`) are shown in the app. Re-verification of a historical brief is a manual
operator action (People → Re-verify) and only ever moves a claim from unverified to verified.

## 4. Web app (M7)

Vercel project from `web/` with `NEXT_PUBLIC_API_BASE_URL` set to the API service URL at build
time (the app proxies `/auth/*` and `/api/*` so cookies stay first-party). Sign-in: the first
time, request a link (only the two allow-listed addresses ever get one), then add Face ID /
Touch ID on the `/enrol` step; afterwards it is passkey only, 90-day session.

## 5. Cut-over (M8) — checklist

- [ ] ≥ 3 clean shadow days (operator inbox, `/ops` queue empty of blocked/needs-review surprises)
- [ ] backfill done, sequence restarted at 121
- [ ] `EXECUTION_MODE=production` + `MD_EMAIL` set → the MD starts receiving verified + audited briefs only
- [ ] n8n workflow deleted (its Hetzner VPS cron off)
- [ ] `engine/` legacy tree archived in a final commit

## 6. Where to look when something is wrong

| Symptom | Look at |
|---|---|
| No email at 06:00 | `/ops` → runs: status `failed` carries the error; the operator also gets a [RUN FAILED] email |
| Brief went to the operator, not the MD | It is `needs_review` (an unverified load-bearing claim) or the audit failed — the email lists the open claims / violations |
| The same company two days running | `/ops` → candidates: the second should read `dedup_suppressed`; if not, check `surfaced_log` |
| A race or partnership blocked a brief | Correct by design: the fixed calendar / sponsor table says it does not exist. Update the table in `/ops` (sponsors) or the seeds only from a Tier 1 source |
| 3 pages | Never ships: the renderer raises; the audit failure email says `page_overflow` |
| `[RUN FAILED] … scanner output unparseable` | The deploy log prints the tail of the last scanner text (also `runs.summary.scan_raw_tail`, visible in `/ops`). "truncated at max_tokens" = raise `SCAN_MAX_TOKENS`; "still paused" = the web-search loop never finished; validation errors name the field the model got wrong |
