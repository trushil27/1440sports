"use client";

import { useCallback, useRef, useState } from "react";
import { SidePanel, type SidePanelHandle } from "./SidePanel";
import { TopBar } from "./TopBar";
import { UserProvider } from "./UserProvider";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [panelOpen, setPanelOpen] = useState(false);
  const panel = useRef<SidePanelHandle>(null);

  const onSearch = useCallback(() => {
    setPanelOpen(true);
    window.setTimeout(() => panel.current?.focusSearch(), 50);
  }, []);

  return (
    <UserProvider>
      <div className="flex min-h-dvh flex-col">
        <TopBar onOpenPanel={() => setPanelOpen(true)} onSearch={onSearch} />
        <div className="mx-auto flex w-full max-w-screen-2xl flex-1 items-stretch">
          <SidePanel ref={panel} open={panelOpen} onClose={() => setPanelOpen(false)} />
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </div>
    </UserProvider>
  );
}
