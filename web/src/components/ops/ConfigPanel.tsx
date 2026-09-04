"use client";

import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import type { OpsConfig } from "@/lib/types";

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-3 px-3 py-2">
      <dt className="font-ui text-xs uppercase tracking-wider text-muted">{k}</dt>
      <dd className="text-right font-ui text-sm">{v}</dd>
    </div>
  );
}

function Flag({ on }: { on: boolean }) {
  return <span className={on ? "pill pill-ok" : "pill pill-warn"}>{on ? "Configured" : "Missing"}</span>;
}

export function ConfigPanel() {
  const [cfg, setCfg] = useState<OpsConfig | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    ops
      .config()
      .then(setCfg)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load config."));
  }, []);

  if (error) return <p className="text-sm text-bad">{error}</p>;
  if (!cfg) return <p className="kicker">Loading…</p>;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <dl className="panel divide-y divide-hair">
        <Row k="Execution mode" v={<span className="pill pill-navy">{cfg.execution_mode}</span>} />
        <Row k="Scan model" v={cfg.models.scan} />
        <Row k="Writer model" v={cfg.models.writer} />
        <Row k="Verify model" v={cfg.models.verify} />
        <Row k="Timezone" v={cfg.timezone} />
      </dl>
      <dl className="panel divide-y divide-hair">
        <Row k="MD threshold" v={`${cfg.md_threshold} / 100`} />
        <Row k="Freshness · track 1" v={`${cfg.freshness_days_track1} days`} />
        <Row k="Freshness · alumni" v={`${cfg.freshness_days_alumni} days`} />
        <Row k="Dedup window" v={`${cfg.dedup_window_days} days`} />
        <Row k="Max verification attempts" v={cfg.max_verification_attempts} />
        <Row k="Anthropic key" v={<Flag on={cfg.anthropic_key_configured} />} />
        <Row k="Microsoft Graph" v={<Flag on={cfg.graph_configured} />} />
        <Row k="MD email" v={<Flag on={cfg.md_email_configured} />} />
      </dl>
      <p className="kicker md:col-span-2">Read-only. Change values through the API service environment.</p>
    </div>
  );
}
