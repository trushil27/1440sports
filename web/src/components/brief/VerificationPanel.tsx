import { claimClass, claimLabel, fmtDate, hostname } from "@/lib/format";
import type { VerificationPanelData } from "@/lib/types";
import { VerificationBadge } from "../Badges";

export function VerificationPanel({ data }: { data: VerificationPanelData }) {
  const loadBearing = data.claims.filter((c) => c.load_bearing);
  const supporting = data.claims.filter((c) => !c.load_bearing);
  return (
    <section id="verification" className="scroll-mt-20">
      <h2 className="h-rule">Verification</h2>
      <div className="flex flex-wrap items-center gap-3">
        <VerificationBadge badge={data.badge} />
        <p className="font-display text-lg text-ink">{data.summary}</p>
      </div>
      {data.claims.length === 0 ? (
        <p className="mt-3 text-sm text-muted">No claim ledger is stored for this brief. Nothing here has been checked against a source.</p>
      ) : (
        <>
          <ClaimList rows={loadBearing} />
          {supporting.length > 0 && (
            <details className="mt-3">
              <summary className="kicker cursor-pointer">Supporting claims ({supporting.length})</summary>
              <ClaimList rows={supporting} />
            </details>
          )}
        </>
      )}
    </section>
  );
}

function ClaimList({ rows }: { rows: VerificationPanelData["claims"] }) {
  return (
    <ul className="mt-3 divide-y divide-hair overflow-hidden rounded-xl border border-hair">
      {rows.map((c) => (
        <li key={c.id} className="bg-paper p-3.5 sm:p-4">
          <div className="flex items-start gap-3">
            <span className={`${claimClass(c.status)} mt-0.5 shrink-0`}>{claimLabel(c.status)}</span>
            <div className="min-w-0 flex-1">
              <p className="text-[0.95rem] leading-snug text-ink">{c.text}</p>
              {c.excerpt && <blockquote className="quote mt-2 text-sm">{c.excerpt}</blockquote>}
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 font-ui text-[0.7rem] text-muted">
                {c.evidence_url ? (
                  <a href={c.evidence_url} target="_blank" rel="noreferrer noopener" className="text-gold-deep underline-offset-2 hover:underline dark:text-gold">
                    Source · {hostname(c.evidence_url)}
                  </a>
                ) : c.cited_source_url ? (
                  <a href={c.cited_source_url} target="_blank" rel="noreferrer noopener" className="underline-offset-2 hover:underline">
                    Cited · {hostname(c.cited_source_url)}
                  </a>
                ) : (
                  <span>No source recorded</span>
                )}
                <span className="uppercase tracking-wider">{c.section.replace(/_/g, " ")}</span>
                <span className="uppercase tracking-wider">{c.type.replace(/_/g, " ")}</span>
                {c.method && <span>Method · {c.method.replace(/_/g, " ")}</span>}
                {c.checked_at && <span>Checked {fmtDate(c.checked_at)}</span>}
                {c.model && <span>{c.model}</span>}
              </div>
              {c.notes && <p className="mt-1.5 text-xs text-muted">{c.notes}</p>}
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
