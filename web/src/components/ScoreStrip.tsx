/** The brief header's score strip: navy score box + four chips, as on page 1 of the PDF. */
export function ScoreStrip({
  score,
  timing,
  series,
  team,
  horizon,
}: {
  score: number | null | undefined;
  timing?: string | null;
  series?: string | null;
  team?: string | null;
  horizon?: string | null;
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-stretch">
      <div className="scorebox">
        <div className="font-display text-[2.6rem] font-bold leading-[0.9]">{score ?? "—"}</div>
        <div className="mt-1.5 font-ui text-[0.6rem] uppercase tracking-[0.19em] text-gold">Opportunity / 100</div>
      </div>
      <div className="grid flex-1 grid-cols-2 gap-2 lg:grid-cols-4">
        <div className="chip">
          <div className="chip-k">Timing window</div>
          <div className="chip-v">{timing || "—"}</div>
        </div>
        <div className="chip">
          <div className="chip-k">Series</div>
          <div className="chip-v">{series || "—"}</div>
        </div>
        <div className="chip">
          <div className="chip-k">Recommended team</div>
          <div className="chip-v">{team || "—"}</div>
        </div>
        <div className="chip">
          <div className="chip-k">Action horizon</div>
          <div className="chip-v">{horizon || "—"}</div>
        </div>
      </div>
    </div>
  );
}
