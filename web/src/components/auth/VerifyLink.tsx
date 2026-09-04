"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ApiError, auth } from "@/lib/api";

/** Exchanges the emailed token for a session (the API sets the cookie) and routes on. */
export function VerifyLink() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token");
  const [error, setError] = useState<string | null>(null);
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    if (!token) {
      setError("This link is missing its token.");
      return;
    }
    auth
      .verifyMagicLink(token)
      .then((r) => router.replace(r.next === "/enrol" ? "/enrol" : "/"))
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not verify the link."));
  }, [token, router]);

  if (error) {
    return (
      <div className="space-y-4">
        <p className="text-bad">{error}</p>
        <p className="text-sm text-muted">Links expire quickly. Request a fresh one from the sign-in page.</p>
        <Link href="/signin" className="btn">
          Back to sign in
        </Link>
      </div>
    );
  }
  return <p className="kicker">Checking the link…</p>;
}
