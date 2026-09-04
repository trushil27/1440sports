import type { Metadata, Viewport } from "next";
import "./globals.css";
import { lora, poppins } from "@/lib/fonts";
import { THEME_INIT_SCRIPT } from "@/lib/theme";
import { RegisterSW } from "@/components/RegisterSW";
import { ToastProvider } from "@/components/Toast";

export const metadata: Metadata = {
  title: { default: "1440 Intelligence", template: "%s · 1440 Intelligence" },
  description: "Daily F1 / Formula E sponsorship intelligence for 1440Sports.",
  applicationName: "1440 Intelligence",
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "1440",
  },
  icons: {
    icon: [{ url: "/favicon-64.png", sizes: "64x64", type: "image/png" }],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  formatDetection: { telephone: false },
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#191a48",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-GB" suppressHydrationWarning className={`${lora.variable} ${poppins.variable}`}>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="mobile-web-app-capable" content="yes" />
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-dvh bg-paper text-ink">
        <ToastProvider>{children}</ToastProvider>
        <RegisterSW />
      </body>
    </html>
  );
}
