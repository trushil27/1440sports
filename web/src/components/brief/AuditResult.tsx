import { auditClass, auditLabel } from "@/lib/format";
import type { BriefDetail } from "@/lib/types";

function violationText(v: unknown): string {
  if (typeof v === "string") return v;
  if (v && typeof v === "object") {
    const o = v as Record<string, unknown>;
    const rule = o.rule ?? o.id ?? o.code;
    const msg = o.message ?? o.detail ?? o.text ?? o.reason;
    if (rule || msg) return [rule ? `Rule ${String(rule)}` : null, msg ? String(msg) : null].filter(Boolean).join(" · ");
    return JSON.stringify(o);
  }
  return String(v);
}

export function AuditResult({ audit }: { audit: BriefDetail["audit_result"] }) {
  return (
    <section id="audit" className="scroll-mt-20">
      <h2 className="h-rule">Audit</h2>
      <div className="flex flex-wrap items-center gap-3">
        <span className={auditClass(audit.status)}>{auditLabel(audit.status)}</span>
        <span className="font-ui text-xs text-muted">
          13-rule audit · {audit.attempts ?? 0} attempt{audit.attempts === 1 ? "" : "s"}
        </span>
      </div>
      {audit.violations.length > 0 ? (
        <ul className="mt-3 space-y-1.5 text-sm">
          {audit.violations.map((v, i) => (
            <li key={i} className="flex gap-2">
              <span className="mt-[0.55em] h-1.5 w-1.5 shrink-0 rounded-full bg-bad" aria-hidden />
              <span>{violationText(v)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-muted">No violations recorded.</p>
      )}
    </section>
  );
}
