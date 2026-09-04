import { AuthFrame } from "@/components/AuthFrame";
import { EnrolPasskey } from "@/components/auth/EnrolPasskey";

export const metadata = { title: "Add a passkey" };

export default function EnrolPage() {
  return (
    <AuthFrame
      title="Add Face ID / Touch ID"
      lede="One tap now, then this device signs you in without links or passwords."
    >
      <EnrolPasskey />
    </AuthFrame>
  );
}
