"use client";

import Link from "next/link";
import { useState } from "react";
import { useUser } from "../UserProvider";
import { AlumniTable } from "./AlumniTable";
import { BlocklistEditor } from "./BlocklistEditor";
import { ConfigPanel } from "./ConfigPanel";
import { ProviderUsagePanel } from "./ProviderUsagePanel";
import { QueuePanel } from "./QueuePanel";
import { RunsPanel } from "./RunsPanel";
import { SponsorsTable } from "./SponsorsTable";

const TABS = [
  ["runs", "Runs"],
  ["queue", "Queue"],
  ["blocklist", "Blocklist"],
  ["alumni", "Alumni"],
  ["sponsors", "Sponsors"],
  ["providers", "Providers"],
  ["config", "Config"],
] as const;
type Tab = (typeof TABS)[number][0];

export function OpsView() {
  const { me, loading } = useUser();
  const [tab, setTab] = useState<Tab>("runs");

  if (loading) return <div className="px-5 py-16 text-center kicker">Loading…</div>;
  if (!me || me.role !== "operator") {
    return (
      <div className="mx-auto max-w-xl px-6 py-20 text-center">
        <h1 className="font-display text-3xl text-navy dark:text-ink">Operator only</h1>
        <p className="mt-3 text-muted">This page is for the operator account.</p>
        <Link href="/" className="btn mt-6">
          Back to today
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
      <p className="eyebrow">Operations</p>
      <h1 className="mt-1 font-display text-3xl text-navy dark:text-ink">Ops</h1>
      <nav className="mt-4 flex gap-1 overflow-x-auto border-b border-hair font-ui text-sm" aria-label="Ops sections">
        {TABS.map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`-mb-px whitespace-nowrap border-b-2 px-3 py-2 ${tab === id ? "border-gold text-ink" : "border-transparent text-muted hover:text-ink"}`}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className="mt-6">
        {tab === "runs" && <RunsPanel />}
        {tab === "queue" && <QueuePanel />}
        {tab === "blocklist" && <BlocklistEditor />}
        {tab === "alumni" && <AlumniTable />}
        {tab === "sponsors" && <SponsorsTable />}
        {tab === "providers" && <ProviderUsagePanel />}
        {tab === "config" && <ConfigPanel />}
      </div>
    </div>
  );
}
