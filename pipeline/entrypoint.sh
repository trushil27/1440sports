#!/bin/sh
# Container entrypoint for the daily job / desk build service / API: preflight → migrate →
# seed → backfill → run. Migrate, seed and backfill are idempotent, so running them on every
# start is safe and keeps the schema/reference data in step with the deployed code.
set -e
cd /app

# Preflight: if the database is not reachable (typically DATABASE_URL missing on the Railway
# service), print which variables are set / missing, email the operator once, and:
#   - cron job (no args): exit 0 — the run is over, the next slot retries; a non-zero exit
#     would only show "Crashed" with no email;
#   - long-running service (uvicorn args): keep probing for 2 minutes, then exit 1 so Railway's
#     ON_FAILURE policy retries with backoff (one email per container start).
# Exit code 3 = database unreachable; any other non-zero code is a defect in preflight itself
# and must not be mistaken for "no database" — then we fail loudly.
SERVICE_NAME="${SERVICE_NAME:-${RAILWAY_SERVICE_NAME:-daily job}}"
if [ "$#" -gt 0 ]; then WAIT=120; else WAIT=0; fi
set +e
python -m intel.preflight --alert --wait "$WAIT" --service "$SERVICE_NAME"
rc=$?
set -e
if [ "$rc" -eq 3 ]; then
  if [ "$#" -gt 0 ]; then
    echo "[entrypoint] database not reachable — stopping so the platform retries (exit 1)"
    exit 1
  fi
  echo "[entrypoint] database not reachable — operator emailed; run skipped (exit 0, no restart loop)"
  exit 0
elif [ "$rc" -ne 0 ]; then
  echo "[entrypoint] preflight itself failed (exit $rc) — refusing to continue blindly"
  exit 1
fi

echo "[entrypoint] applying migrations"
python -m alembic -c db/alembic.ini upgrade head
echo "[entrypoint] loading reference seeds"
python -m intel.seed
# History + recorded engine cases + signal checks (idempotent; a problem here must not stop the run).
echo "[entrypoint] importing history and recorded cases"
python -m intel.backfill > /tmp/backfill.log 2>&1 || { echo "[entrypoint] backfill skipped:"; tail -n 5 /tmp/backfill.log; }
echo "[entrypoint] starting: ${*:-python -m intel.schedule}"
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
exec python -m intel.schedule
