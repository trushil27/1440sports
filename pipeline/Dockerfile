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
COPY db/ /app/db/
COPY spec/ /app/spec/
RUN pip install --no-cache-dir -e "pipeline[render]"

ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/pipeline TZ=Europe/London
# The cron schedule lives in railway.json (two UTC firings; intel.schedule picks the London one).
CMD ["python", "-m", "intel.schedule"]
