import type { Metadata } from "next";
import { Fraunces, Hanken_Grotesk, Geist_Mono } from "next/font/google";
import "./globals.css";

const display = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  axes: ["opsz", "SOFT", "WONK"],
});

const sans = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
});

const mono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Montecast — World Cup 2026 Forecast",
  description:
    "Fifty thousand simulated tournaments. One trophy. A Dixon-Coles × Elo ensemble forecasts every match and every nation's road to the 2026 World Cup final.",
  openGraph: {
    title: "Montecast — World Cup 2026 Forecast",
    description:
      "Fifty thousand simulated tournaments. A data-science engine forecasts the 2026 World Cup.",
    type: "website",
  },
  metadataBase: new URL("https://montecast.vercel.app"),
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${display.variable} ${sans.variable} ${mono.variable} antialiased`}
    >
      <body>{children}</body>
    </html>
  );
}
