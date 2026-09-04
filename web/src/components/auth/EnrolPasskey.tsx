"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { browserSupportsWebAuthn, startRegistration } from "@simplewebauthn/browser";
import type { PublicKeyCredentialCreationOptionsJSON } from "@simplewebauthn/browser";
import { ApiError, auth } from "@/lib/api";

function guessDeviceName(): string {
  const ua = navigator.userAgent;
  if (/iPhone/.test(ua)) return "iPhone";
  if (/iPad/.test(ua)) return "iPad";
  if (/Macintosh/.test(ua)) return "Mac";
  if (/Android/.test(ua)) return "Android";
  if (/Windows/.test(ua)) return "Windows";
  return "This device";
}

export function EnrolPasskey() {
  const router = useRouter();
  const [device, setDevice] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [supported, setSupported] = useState(true);
  const [sessionOk, setSessionOk] = useState<boolean | null>(null);

  useEffect(() => {
    setSupported(browserSupportsWebAuthn());
    setDevice(guessDeviceName());
    auth
      .me()
      .then(() => setSessionOk(true))
      .catch(() => setSessionOk(false));
  }, []);

  const enrol = async () => {
    setBusy(true);
    setError(null);
    try {
      const options = (await auth.passkeyRegisterOptions()) as unknown as PublicKeyCredentialCreationOptionsJSON;
      const credential = await startRegistration({ optionsJSON: options });
      await auth.passkeyRegisterVerify(credential, device.trim() || null);
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError) setError(err.status === 401 ? "Your sign-in link session has ended. Request a new link." : err.detail);
      else if (err instanceof Error && err.name === "NotAllowedError") setError("The passkey prompt was cancelled.");
      else if (err instanceof Error && err.name === "InvalidStateError") setError("A passkey for this account already exists on this device.");
      else setError("Could not create a passkey on this device.");
    } finally {
      setBusy(false);
    }
  };

  if (sessionOk === false) {
    return (
      <div className="space-y-4">
        <p className="text-bad">You need an active sign-in link session to add a passkey.</p>
        <Link href="/signin" className="btn">
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <label className="block">
        <span className="kicker mb-1 block">Device name</span>
        <input className="field" value={device} onChange={(e) => setDevice(e.target.value)} placeholder="iPhone" />
      </label>
      <button type="button" className="btn btn-primary w-full py-3.5 text-[0.95rem]" onClick={enrol} disabled={busy || !supported || sessionOk !== true}>
        {busy ? "Waiting for Face ID / Touch ID…" : "Add Face ID / Touch ID"}
      </button>
      {!supported && <p className="text-sm text-muted">This browser does not support passkeys.</p>}
      {error && <p className="text-sm text-bad">{error}</p>}
      <Link href="/" className="block font-ui text-sm text-muted underline-offset-4 hover:underline">
        Skip for now
      </Link>
    </div>
  );
}
