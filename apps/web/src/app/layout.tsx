import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

// NOTE: This app is offline-first, so we intentionally do NOT use
// `next/font/google` (which requires internet access at build time).
// The font stack below relies on fonts already present on most systems
// (Vazirmatn/Tahoma on Windows/Linux, system Persian fonts on macOS).
// To ship a bundled, fully offline-guaranteed font later, drop a
// Vazirmatn .woff2 file under `public/fonts/` and switch to
// `next/font/local`.

export const metadata: Metadata = {
  title: "ژورنال معاملاتی حرفه‌ای ICT",
  description: "ژورنال معاملاتی آفلاین با موتور هوش تحلیلی — نسخه حرفه‌ای",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
