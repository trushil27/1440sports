"use client";

import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";

type Kind = "info" | "ok" | "error";
interface ToastItem {
  id: number;
  text: string;
  kind: Kind;
}

const ToastCtx = createContext<(text: string, kind?: Kind) => void>(() => {});

export function useToast() {
  return useContext(ToastCtx);
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const seq = useRef(0);
  const push = useCallback((text: string, kind: Kind = "info") => {
    const id = ++seq.current;
    setItems((xs) => [...xs, { id, text, kind }]);
    window.setTimeout(() => setItems((xs) => xs.filter((x) => x.id !== id)), 4500);
  }, []);
  const value = useMemo(() => push, [push]);
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div
        aria-live="polite"
        className="pointer-events-none fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 p-4 safe-bottom"
      >
        {items.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto max-w-md rounded-full border px-4 py-2 font-ui text-sm shadow-card ${
              t.kind === "ok"
                ? "border-ok-line bg-ok-bg text-ok"
                : t.kind === "error"
                  ? "border-bad-line bg-bad-bg text-bad"
                  : "border-hair bg-panel text-ink"
            }`}
          >
            {t.text}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}
