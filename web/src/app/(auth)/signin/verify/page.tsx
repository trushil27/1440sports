import { Suspense } from "react";
import { AuthFrame } from "@/components/AuthFrame";
import { VerifyLink } from "@/components/auth/VerifyLink";

export const metadata = { title: "Signing in" };

export default function VerifyPage() {
  return (
    <AuthFrame title="Signing you in">
      <Suspense fallback={<p className="kicker">Checking the link…</p>}>
        <VerifyLink />
      </Suspense>
    </AuthFrame>
  );
}
