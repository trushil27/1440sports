"""1440 Intelligence Platform — pipeline package.

Stages (see the build brief §6): scan → parse → freshness → blocklist/dedup → score →
verify → write → audit → render → send → log. Every stage writes to Postgres.
"""

__version__ = "0.1.0"
