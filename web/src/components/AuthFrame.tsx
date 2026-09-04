import Image from "next/image";

/** Bare, centred frame for the sign-in / enrolment screens (no app chrome). */
export function AuthFrame({ children, title, lede }: { children: React.ReactNode; title: string; lede?: string }) {
  return (
    <div className="flex min-h-dvh flex-col bg-paper">
      <div className="bg-navy safe-top">
        <div className="mx-auto flex h-14 max-w-screen-2xl items-center px-5">
          <Image src="/logo-gold.png" alt="1440 Sports" width={128} height={22} priority unoptimized className="h-[22px] w-auto" />
          <span className="ml-3 font-ui text-[0.68rem] uppercase tracking-[0.18em] text-gold/70">Intelligence</span>
        </div>
        <div className="h-px w-full bg-gold/30" />
      </div>
      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-12">
        <p className="eyebrow mb-3">1440 Intelligence</p>
        <h1 className="font-display text-3xl text-navy dark:text-ink">{title}</h1>
        {lede && <p className="mt-2 text-muted">{lede}</p>}
        <div className="mt-8">{children}</div>
      </main>
      <p className="kicker px-6 pb-8 text-center safe-bottom">Confidential · 1440Sports, London</p>
    </div>
  );
}
