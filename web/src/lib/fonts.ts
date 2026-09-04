/**
 * Brand type: Lora (display) + Poppins (UI), self-hosted from the vendored OFL files in
 * `public/fonts` (the same TTFs the PDF renderer uses). `next/font/local` emits the
 * @font-face rules and preloads at build time, so the build never depends on Google
 * Fonts being reachable and the installed PWA renders identically offline.
 */
import localFont from "next/font/local";

export const lora = localFont({
  src: [
    { path: "../../public/fonts/Lora-Variable.ttf", weight: "400 700", style: "normal" },
    { path: "../../public/fonts/Lora-Italic-Variable.ttf", weight: "400 700", style: "italic" },
  ],
  variable: "--font-lora",
  display: "swap",
  fallback: ["Georgia", "Times New Roman", "serif"],
});

export const poppins = localFont({
  src: [
    { path: "../../public/fonts/Poppins-Light.ttf", weight: "300", style: "normal" },
    { path: "../../public/fonts/Poppins-Regular.ttf", weight: "400", style: "normal" },
    { path: "../../public/fonts/Poppins-Medium.ttf", weight: "500", style: "normal" },
    { path: "../../public/fonts/Poppins-Bold.ttf", weight: "700", style: "normal" },
  ],
  variable: "--font-poppins",
  display: "swap",
  fallback: ["Helvetica Neue", "Arial", "sans-serif"],
});
