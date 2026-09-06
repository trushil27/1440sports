#!/bin/sh
# Container entrypoint for the daily job / desk build service: preflight → migrate → seed →
# backfill → run. Migrate, seed and backfill are idempotent, so running them on every start
# is safe and keeps the schema/reference data in step with the deployed code.
set -e
cd /app

# Preflight: if the database is not reachable (typically DATABASE_URL missing on the Railway
# service), print which variables are set / missing, email the operator, and stop with exit 0.
# A non-zero exit here would make Railway restart the container in a loop that only ever
# shows "Crashed"; the email and the log line below are the actual signal.
SERVICE_NAME="${SERVICE_NAME:-daily job}"
if ! python -m intel.preflight --service "$SERVICE_NAME"; then
  echo "[entrypoint] database not reachable — emailing the operator and stopping (no restart loop)"
  python -m intel.preflight --alert --service "$SERVICE_NAME" || true
  exit 0
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
