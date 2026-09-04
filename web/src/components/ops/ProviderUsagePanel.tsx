"use client";

import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import { fmtDateTime } from "@/lib/format";
import type { ProviderUsage } from "@/lib/types";

export function ProviderUsagePanel() {
  const [data, setData] = useState<ProviderUsage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    ops
      .providerUsage()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load provider usage."));
  }, []);

  if (error) return <p className="text-sm text-bad">{error}</p>;
  if (!data) return <p className="kicker">Loading…</p>;

  return (
    <div className="space-y-3">
      {data.providers.length === 0 ? (
        <p className="text-sm text-muted">No contact records stored from any provider.</p>
      ) : (
        <table className="w-full max-w-xl text-left font-ui text-sm">
          <thead className="kicker">
            <tr>
              <th className="py-1 pr-3">Provider</th>
              <th className="py-1 pr-3">Records</th>
              <th className="py-1">Last retrieved</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-hair">
            {data.providers.map((p) => (
              <tr key={p.provider}>
                <td className="py-1.5 pr-3 font-medium">{p.provider}</td>
                <td className="py-1.5 pr-3">{p.records}</td>
                <td className="py-1.5 text-muted">{p.last_retrieved ? fmtDateTime(p.last_retrieved) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="text-xs text-muted">{data.note}</p>
    </div>
  );
}
