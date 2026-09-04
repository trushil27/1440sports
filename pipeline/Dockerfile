# 1440 Intelligence Platform — pipeline image (Railway cron job / API host).
FROM python:3.12-slim

# WeasyPrint system libraries (Pango, Cairo, GDK-PixBuf) + Postgres client headers.
RUN apt-get update -q \
 && apt-get install -y -q --no-install-recommends \
      libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libcairo2 libffi8 \
      fonts-liberation fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pipeline/ /app/pipeline/
COPY api/ /app/api/
COPY db/ /app/db/
COPY spec/ /app/spec/
RUN pip install --no-cache-dir -e "pipeline[render]" -e "api"

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/pipeline:/app/api TZ=Europe/London
# One image, two Railway services:
#   cron job (railway.json):     python -m intel.schedule
#   API service (api/railway.json): uvicorn intel_api.app:get_app --factory --host 0.0.0.0 --port $PORT
CMD ["python", "-m", "intel.schedule"]
