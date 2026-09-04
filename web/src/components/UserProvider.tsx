"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { ApiError, auth } from "@/lib/api";
import type { Me } from "@/lib/types";

interface UserState {
  me: Me | null;
  loading: boolean;
  refresh: () => Promise<void>;
}

const Ctx = createContext<UserState>({ me: null, loading: true, refresh: async () => {} });

export function useUser() {
  return useContext(Ctx);
}

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      setMe(await auth.me());
    } catch (err) {
      setMe(null);
      if (err instanceof ApiError && err.status === 401) {
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.assign(`/signin${next === "%2F" ? "" : `?next=${next}`}`);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  return <Ctx.Provider value={{ me, loading, refresh }}>{children}</Ctx.Provider>;
}
