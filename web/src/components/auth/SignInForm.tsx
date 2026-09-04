"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { browserSupportsWebAuthn, startAuthentication } from "@simplewebauthn/browser";
import type { PublicKeyCredentialRequestOptionsJSON } from "@simplewebauthn/browser";
import { ApiError, auth } from "@/lib/api";

function safeNext(raw: string | null): string {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//")) return "/";
  return raw;
}

export function SignInForm() {
  const router = useRouter();
  const params = useSearchParams();
  const next = safeNext(params.get("next"));

  const [supported, setSupported] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLink, setShowLink] = useState(false);
  const [email, setEmail] = useState("");
  const [linkSent, setLinkSent] = useState(false);
  const [linkBusy, setLinkBusy] = useState(false);

  useEffect(() => {
    setSupported(browserSupportsWebAuthn());
  }, []);

  const passkey = async () => {
    setBusy(true);
    setError(null);
    try {
      const options = (await auth.passkeyLoginOptions()) as unknown as PublicKeyCredentialRequestOptionsJSON;
      const credential = await startAuthentication({ optionsJSON: options });
      await auth.passkeyLoginVerify(credential);
      router.replace(next);
    } catch (err) {
      if (err instanceof ApiError) setError(err.detail);
      else if (err instanceof Error && err.name === "NotAllowedError") setError("Passkey prompt was cancelled.");
      else setError("Could not sign in with a passkey on this device. Use a sign-in link to enrol it.");
    } finally {
      setBusy(false);
    }
  };

  const sendLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setLinkBusy(true);
    try {
      await auth.magicLink(email.trim());
    } catch {
      /* Deliberately silent: the response never reveals whether an address is allowed. */
    } finally {
      setLinkBusy(false);
      setLinkSent(true);
    }
  };

  return (
    <div className="space-y-6">
      <button type="button" className="btn btn-primary w-full py-3.5 text-[0.95rem]" onClick={passkey} disabled={busy || !supported}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <circle cx="12" cy="8" r="4" />
          <path d="M5 21a7 7 0 0 1 14 0" />
        </svg>
        {busy ? "Waiting for Face ID / Touch ID…" : "Sign in with passkey"}
      </button>
      {!supported && <p className="text-sm text-muted">This browser does not support passkeys. Use a sign-in link.</p>}
      {error && <p className="text-sm text-bad">{error}</p>}

      <div>
        {!showLink ? (
          <button type="button" className="font-ui text-sm text-muted underline-offset-4 hover:underline" onClick={() => setShowLink(true)}>
            Use a sign-in link instead (first device / recovery)
          </button>
        ) : linkSent ? (
          <div className="panel p-4 text-sm">
            If that address is on the list, a link is on its way. It is valid for a short while; open it on this device.
          </div>
        ) : (
          <form onSubmit={sendLink} className="panel space-y-3 p-4">
            <label className="block">
              <span className="kicker mb-1 block">Email</span>
              <input
                type="email"
                required
                autoComplete="email"
                inputMode="email"
                className="field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@1440sports.com"
              />
            </label>
            <button type="submit" className="btn w-full" disabled={linkBusy}>
              {linkBusy ? "Sending…" : "Email me a sign-in link"}
            </button>
            <p className="text-xs text-muted">Used only to enrol a first device or recover access. No passwords anywhere.</p>
          </form>
        )}
      </div>
    </div>
  );
}
