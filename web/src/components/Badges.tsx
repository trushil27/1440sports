import { badgeClass, tierClass } from "@/lib/format";

export function TierBadge({ tier }: { tier: string | null | undefined }) {
  if (!tier) return null;
  return <span className={tierClass(tier)}>{tier}</span>;
}

export function VerificationBadge({ badge }: { badge: string | null | undefined }) {
  if (!badge) return null;
  const dot =
    badge === "Verified"
      ? "bg-ok"
      : badge === "Review"
        ? "bg-warn"
        : badge === "Blocked"
          ? "bg-bad"
          : "bg-muted";
  return (
    <span className={badgeClass(badge)}>
      <span className={`inline-block h-1.5 w-1.5 rounded-full ${dot}`} aria-hidden />
      {badge}
    </span>
  );
}

export function Tag({ children, tone = "muted" }: { children: React.ReactNode; tone?: "muted" | "navy" | "gold" }) {
  const cls =
    tone === "navy"
      ? "pill pill-navy"
      : tone === "gold"
        ? "pill border-gold/60 bg-transparent text-gold-deep dark:text-gold"
        : "pill pill-muted";
  return <span className={cls}>{children}</span>;
}
