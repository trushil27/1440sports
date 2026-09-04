"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, briefs } from "@/lib/api";
import { fmtDate, plain } from "@/lib/format";
import type { ActionRow, BriefDetail, PeopleCard } from "@/lib/types";
import { Tag, TierBadge, VerificationBadge } from "../Badges";
import { ScoreStrip } from "../ScoreStrip";
import { useToast } from "../Toast";
import { ActionBar } from "./ActionBar";
import { AuditResult } from "./AuditResult";
import { OutreachPanel } from "./OutreachPanel";
import { PeoplePanel } from "./PeoplePanel";
import { ScoreComposition } from "./ScoreComposition";
import { VerificationPanel } from "./VerificationPanel";

const PdfViewer = dynamic(() => import("./PdfViewer").then((m) => m.PdfViewer), {
  ssr: false,
  loading: () => <p className="kicker py-8 text-center">Loading the brief…</p>,
});

export function BriefView({ number, tab }: { number: number; tab: "brief" | "people" }) {
  const toast = useToast();
  const [brief, setBrief] = useState<BriefDetail | null>(null);
  const [people, setPeople] = useState<PeopleCard | null>(null);
  const [peopleError, setPeopleError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setBrief(null);
    setPeople(null);
    setError(null);
    briefs
      .get(number)
      .then(setBrief)
      .catch((err) => setError(err instanceof ApiError ? (err.status === 404 ? "There is no brief with that number." : err.detail) : "Could not load the brief."));
    briefs
      .people(number)
      .then(setPeople)
      .catch((err) => setPeopleError(err instanceof ApiError ? err.detail : "Could not load the people panel."));
  }, [number]);

  useEffect(() => {
    if (!brief || !window.location.hash) return;
    const el = document.getElementById(window.location.hash.slice(1));
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [brief]);

  if (error) {
    return (
      <div className="mx-auto max-w-xl px-6 py-20 text-center">
        <h1 className="font-display text-3xl text-navy dark:text-ink">Brief not available</h1>
        <p className="mt-3 text-muted">{error}</p>
        <Link href="/" className="btn mt-6">
          Back to today
        </Link>
      </div>
    );
  }
  if (!brief) return <div className="px-5 py-16 text-center kicker">Loading brief N° {number}…</div>;

  const d = brief.brief_data ?? {};
  const pdfUrl = brief.pdf_url ? briefs.pdfUrl(brief.number) : null;

  const share = async () => {
    const url = window.location.origin + `/brief/${brief.number}`;
    const title = `1440 Intelligence Brief ${brief.label} — ${brief.company}`;
    try {
      if (navigator.share) await navigator.share({ title, url });
      else {
        await navigator.clipboard.writeText(url);
        toast("Link copied.", "ok");
      }
    } catch {
      /* cancelled */
    }
  };

  const onActions = (rows: ActionRow[]) => setBrief((b) => (b ? { ...b, actions: rows } : b));
  const refreshActions = () => briefs.get(number).then((b) => setBrief(b)).catch(() => {});

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-8">
      {/* Header */}
      <header>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="eyebrow">Intelligence brief · {brief.label}</span>
          <span className="kicker">{fmtDate(brief.date)}</span>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <TierBadge tier={brief.tier} />
          <VerificationBadge badge={brief.badge} />
          {brief.track === 2 && <Tag tone="navy">Alumni Intelligence</Tag>}
          {brief.historical && <Tag>Historical</Tag>}
          {brief.candidate.resurfaced && <Tag tone="gold">Resurfaced</Tag>}
          {!brief.md_eligible && brief.verification === "needs_review" && <Tag tone="gold">Verify before circulation</Tag>}
        </div>
        <h1 className="mt-3 font-display text-4xl leading-[1.05] tracking-tight text-navy dark:text-ink sm:text-5xl">{brief.company}</h1>
        {(d.industry_meta || brief.industry) && (
          <p className="mt-1.5 text-sm italic text-muted">
            {d.industry_meta || brief.industry}
            {d.hq ? ` · ${d.hq}` : ""}
            {d.ticker ? ` · ${d.ticker}` : ""}
          </p>
        )}
        {brief.take && <p className="mt-4 font-display text-lg leading-relaxed">{plain(brief.take)}</p>}
        <div className="mt-5">
          <ScoreStrip score={brief.score} timing={d.timing_label} series={brief.series} team={brief.team} horizon={d.horizon_label} />
        </div>

        <nav className="mt-6 flex gap-1 border-b border-hair font-ui text-sm" aria-label="Brief sections">
          <Link href={`/brief/${brief.number}`} className={`-mb-px border-b-2 px-3 py-2 ${tab === "brief" ? "border-gold text-ink" : "border-transparent text-muted hover:text-ink"}`}>
            Brief
          </Link>
          <Link href={`/brief/${brief.number}/people`} className={`-mb-px border-b-2 px-3 py-2 ${tab === "people" ? "border-gold text-ink" : "border-transparent text-muted hover:text-ink"}`}>
            People
          </Link>
          {tab === "brief" && (
            <div className="ml-auto hidden gap-3 self-center text-xs text-muted sm:flex">
              <a href="#verification" className="hover:text-ink">Verification</a>
              <a href="#score" className="hover:text-ink">Score</a>
              <a href="#actions" className="hover:text-ink">Actions</a>
              <a href="#outreach" className="hover:text-ink">Outreach</a>
            </div>
          )}
        </nav>
      </header>

      {tab === "people" ? (
        <div className="mt-6 space-y-10">
          <PeoplePanel number={number} people={people} onChange={setPeople} error={peopleError} />
          <OutreachPanel number={number} enabled={!!people?.outreach_enabled} disabledReason={people?.warning ?? (people && !people.outreach_enabled ? "Outreach is disabled until the decision-maker's role is verified." : null)} onContacted={refreshActions} />
        </div>
      ) : (
        <div className="mt-6 space-y-10">
          {/* PDF */}
          <section id="pdf">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <h2 className="h-rule !mb-0 flex-1 border-b-0">The two pages</h2>
              {pdfUrl && (
                <div className="flex gap-2">
                  <a href={pdfUrl} download className="btn">
                    Download
                  </a>
                  <button type="button" className="btn" onClick={share}>
                    Share
                  </button>
                </div>
              )}
            </div>
            {pdfUrl ? (
              <PdfViewer url={pdfUrl} />
            ) : (
              <p className="panel p-4 text-sm text-muted">No PDF is stored for this brief{brief.historical ? " (historical import)" : ""}.</p>
            )}
          </section>

          <VerificationPanel data={brief.verification_panel} />
          <ScoreComposition comp={brief.score_composition} score={brief.score} />
          <AuditResult audit={brief.audit_result} />
          <ActionBar number={number} company={brief.company} actions={brief.actions} onChange={onActions} />
          <PeoplePanel number={number} people={people} onChange={setPeople} error={peopleError} />
          <OutreachPanel number={number} enabled={!!people?.outreach_enabled} disabledReason={people?.warning ?? (people && !people.outreach_enabled ? "Outreach is disabled until the decision-maker's role is verified." : null)} onContacted={refreshActions} />

          {(brief.candidate.trigger || brief.candidate.source_url) && (
            <section>
              <h2 className="h-rule">Trigger</h2>
              <p className="text-sm">
                {brief.candidate.trigger}
                {brief.candidate.trigger_date && <span className="text-muted"> · {fmtDate(brief.candidate.trigger_date)}</span>}
              </p>
              {brief.candidate.source_url && (
                <a href={brief.candidate.source_url} target="_blank" rel="noreferrer noopener" className="mt-1 inline-block font-ui text-xs text-gold-deep underline-offset-2 hover:underline dark:text-gold">
                  {brief.candidate.source_url}
                </a>
              )}
            </section>
          )}
        </div>
      )}
    </div>
  );
}
