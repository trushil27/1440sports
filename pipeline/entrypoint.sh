#!/bin/sh
# Container entrypoint for the daily job: migrate → seed → run the scheduled step.
# Both migrate and seed are idempotent, so running them on every start is safe and
# keeps the schema/reference data in step with the deployed code.
set -e
cd /app
echo "[entrypoint] applying migrations"
python -m alembic -c db/alembic.ini upgrade head
echo "[entrypoint] loading reference seeds"
python -m intel.seed
# History + recorded engine cases (idempotent; a problem here must not stop the run).
echo "[entrypoint] importing history and recorded cases"
python -m intel.backfill > /tmp/backfill.log 2>&1 || { echo "[entrypoint] backfill skipped:"; tail -n 5 /tmp/backfill.log; }
echo "[entrypoint] starting: ${*:-python -m intel.schedule}"
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
exec python -m intel.schedule
