"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api";
import { todayLondon } from "@/lib/format";
import { getTheme, setTheme, type Theme } from "@/lib/theme";
import { useUser } from "./UserProvider";

interface Props {
  onOpenPanel: () => void;
  onSearch: () => void;
}

export function TopBar({ onOpenPanel, onSearch }: Props) {
  const { me } = useUser();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const [theme, setThemeState] = useState<Theme>("light");
  const menuRef = useRef<HTMLDivElement>(null);
  const [date, setDate] = useState("");

  useEffect(() => {
    setThemeState(getTheme());
    setDate(todayLondon());
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const close = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [menuOpen]);

  const toggleTheme = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    setThemeState(next);
  };

  const signOut = async () => {
    try {
      await auth.logout();
    } finally {
      navigator.serviceWorker?.controller?.postMessage("clear-caches");
      router.replace("/signin");
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-navy text-gold safe-top">
      <div className="mx-auto flex h-14 max-w-screen-2xl items-center gap-3 px-3 sm:px-5">
        <button
          type="button"
          onClick={onOpenPanel}
          className="-ml-1 rounded-md p-2 text-gold/90 hover:text-gold md:hidden"
          aria-label="Open history"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>

        <Link href="/" className="flex items-center" aria-label="1440 Intelligence, home">
          <Image src="/logo-gold.png" alt="1440 Sports" width={128} height={22} priority unoptimized className="h-[22px] w-auto" />
        </Link>

        <span className="hidden font-ui text-[0.68rem] uppercase tracking-[0.18em] text-gold/70 sm:inline">
          Intelligence
        </span>

        <div className="ml-auto flex items-center gap-1.5">
          <span className="hidden font-ui text-xs text-gold/80 sm:inline" suppressHydrationWarning>
            {date}
          </span>
          <button
            type="button"
            onClick={onSearch}
            className="rounded-md p-2 text-gold/90 hover:text-gold"
            aria-label="Search"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-3.5-3.5" />
            </svg>
          </button>

          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              className="rounded-md p-2 text-gold/90 hover:text-gold"
              aria-label="Menu"
              aria-expanded={menuOpen}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="5" r="1.8" />
                <circle cx="12" cy="12" r="1.8" />
                <circle cx="12" cy="19" r="1.8" />
              </svg>
            </button>
            {menuOpen && (
              <div className="card absolute right-0 mt-2 w-56 overflow-hidden py-1 font-ui text-sm text-ink">
                {me && (
                  <div className="border-b border-hair px-4 py-2.5">
                    <div className="truncate font-medium">{me.display_name || me.email}</div>
                    <div className="kicker mt-0.5">{me.role === "operator" ? "Operator" : "MD"}</div>
                  </div>
                )}
                <button type="button" className="block w-full px-4 py-2.5 text-left hover:bg-panel" onClick={toggleTheme}>
                  Theme: {theme === "dark" ? "Dark" : "Light"} → {theme === "dark" ? "Light" : "Dark"}
                </button>
                {me?.role === "operator" && (
                  <Link href="/ops" className="block px-4 py-2.5 hover:bg-panel" onClick={() => setMenuOpen(false)}>
                    Ops
                  </Link>
                )}
                <button type="button" className="block w-full px-4 py-2.5 text-left hover:bg-panel" onClick={signOut}>
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="h-px w-full bg-gold/30" />
    </header>
  );
}
