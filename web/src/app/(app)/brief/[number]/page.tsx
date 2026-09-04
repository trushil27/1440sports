import { notFound } from "next/navigation";
import { BriefView } from "@/components/brief/BriefView";

export async function generateMetadata({ params }: { params: Promise<{ number: string }> }) {
  const { number } = await params;
  return { title: `Brief N° ${number}` };
}

export default async function BriefPage({ params }: { params: Promise<{ number: string }> }) {
  const { number } = await params;
  const n = Number(number);
  if (!Number.isInteger(n) || n <= 0) notFound();
  return <BriefView number={n} tab="brief" />;
}
