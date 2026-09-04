import { Suspense } from "react";
import { AuthFrame } from "@/components/AuthFrame";
import { SignInForm } from "@/components/auth/SignInForm";

export const metadata = { title: "Sign in" };

export default function SignInPage() {
  return (
    <AuthFrame title="Sign in" lede="Face ID or Touch ID on a device you have already enrolled.">
      <Suspense fallback={null}>
        <SignInForm />
      </Suspense>
    </AuthFrame>
  );
}
