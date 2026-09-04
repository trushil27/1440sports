"use client";

import { useState } from "react";
import { ApiError, briefs } from "@/lib/api";
import { claimClass, claimLabel, fmtDate, hostname } from "@/lib/format";
import type { PeopleCard } from "@/lib/types";
import { useToast } from "../Toast";

export function PeoplePanel({
  number,
  people,
  onChange,
  error,
}: {
  number: number;
  people: PeopleCard | null;
  onChange: (p: PeopleCard) => void;
  error?: string | null;
}) {
  const toast = useToast();
  const [busy, setBusy] = useState<"reverify" | "lookup" | null>(null);

  const reverify = async () => {
    setBusy("reverify");
    try {
      const p = await briefs.reverify(number);
      onChange(p);
      toast(p.role.status === "verified" ? "Role re-verified." : `Role check: ${claimLabel(p.role.status).toLowerCase()}.`, p.role.status === "verified" ? "ok" : "error");
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Re-verify failed.", "error");
    } finally {
      setBusy(null);
    }
  };

  const lookup = async () => {
    setBusy("lookup");
    try {
      onChange(await briefs.lookupContact(number));
      toast("Contact details retrieved from the licensed provider.", "ok");
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Lookup failed.", "error");
    } finally {
      setBusy(null);
    }
  };

  return (
    <section id="people" className="scroll-mt-20">
      <h2 className="h-rule">People</h2>
      {error ? (
        <p className="text-sm text-bad">{error}</p>
      ) : !people ? (
        <p className="kicker">Loading…</p>
      ) : !people.name ? (
        <p className="text-sm text-muted">This brief names no decision-maker.</p>
      ) : (
        <div className="card p-5">
          {people.warning && (
            <div className="mb-4 rounded-lg border border-bad-line bg-bad-bg p-3 font-ui text-sm text-bad">{people.warning}</div>
          )}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="font-display text-2xl text-navy dark:text-ink">{people.name}</div>
              <div className="mt-0.5 font-ui text-xs uppercase tracking-wider text-muted">
                {people.title || "Title not stated"} · {people.company}
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {people.alumni && <span className="pill pill-navy">Alumni · {people.alumni.tier}</span>}
              <span className={claimClass(people.role.status)}>
                {people.role.status === "verified" ? "Verified" : people.role.drifted ? "Role drifted" : claimLabel(people.role.status)}
              </span>
            </div>
          </div>

          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="chip-k">Current position</dt>
              <dd className="mt-0.5">
                {people.title || "—"}
                {people.role.verified_on && <span className="text-muted"> · verified on {fmtDate(people.role.verified_on)}</span>}
                {people.role.source && (
                  <>
                    {" · "}
                    <a href={people.role.source} target="_blank" rel="noreferrer noopener" className="text-gold-deep underline-offset-2 hover:underline dark:text-gold">
                      {hostname(people.role.source)}
                    </a>
                  </>
                )}
                {people.role.excerpt && <blockquote className="quote mt-2 text-sm">{people.role.excerpt}</blockquote>}
              </dd>
            </div>
            {people.bio && (
              <div>
                <dt className="chip-k">Background</dt>
                <dd className="mt-0.5 leading-relaxed">{people.bio}</dd>
              </div>
            )}
            {people.alumni && (
              <div>
                <dt className="chip-k">Alumni · prior deal</dt>
                <dd className="mt-0.5">
                  {people.alumni.prior_deal || "Prior deal not recorded"}
                  {typeof people.alumni.boost === "number" && <span className="text-muted"> · boost +{people.alumni.boost}</span>}
                </dd>
              </div>
            )}
            {people.co_decision_makers.length > 0 && (
              <div>
                <dt className="chip-k">Co-decision-makers</dt>
                <dd className="mt-0.5">
                  <ul className="space-y-0.5">
                    {people.co_decision_makers.map((p, i) => {
                      const o = (p && typeof p === "object" ? p : {}) as { name?: string; title?: string };
                      return <li key={i}>{typeof p === "string" ? p : [o.name, o.title].filter(Boolean).join(" · ") || JSON.stringify(p)}</li>;
                    })}
                  </ul>
                </dd>
              </div>
            )}
            <div>
              <dt className="chip-k">Contact</dt>
              <dd className="mt-0.5">
                {people.contact ? (
                  <div className="space-y-1">
                    {people.contact.opted_out && <p className="text-bad">Opted out. Do not contact.</p>}
                    {people.contact.linkedin_url && (
                      <p>
                        <a href={people.contact.linkedin_url} target="_blank" rel="noreferrer noopener" className="text-gold-deep underline-offset-2 hover:underline dark:text-gold">
                          LinkedIn profile
                        </a>
                      </p>
                    )}
                    {people.contact.email && (
                      <p>
                        <a href={`mailto:${people.contact.email}`} className="underline-offset-2 hover:underline">
                          {people.contact.email}
                        </a>
                      </p>
                    )}
                    {people.contact.phone && (
                      <p>
                        <a href={`tel:${people.contact.phone}`} className="underline-offset-2 hover:underline">
                          {people.contact.phone}
                        </a>
                      </p>
                    )}
                    <p className="font-ui text-xs text-muted">
                      {people.contact.provider || "provider not recorded"}
                      {people.contact.retrieved_at && ` · retrieved ${fmtDate(people.contact.retrieved_at)}`}
                      {people.contact.consent_basis && ` · ${people.contact.consent_basis.replace(/_/g, " ")}`}
                    </p>
                  </div>
                ) : (
                  <p className="text-muted">
                    {people.contact_provider === "none"
                      ? "No licensed contact provider is approved yet, so no LinkedIn, email or phone is shown. Nothing is guessed."
                      : "No contact record stored yet."}
                  </p>
                )}
              </dd>
            </div>
          </dl>

          <div className="mt-5 flex flex-wrap gap-2">
            <button type="button" className="btn" disabled={busy !== null} onClick={reverify}>
              {busy === "reverify" ? "Checking…" : "Re-verify role"}
            </button>
            {!people.contact && people.contact_provider !== "none" && (
              <button type="button" className="btn" disabled={busy !== null} onClick={lookup}>
                {busy === "lookup" ? "Fetching…" : `Fetch contact via ${people.contact_provider}`}
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
