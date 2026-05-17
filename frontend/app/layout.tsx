import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClimaShock — Pakistan Climate Intelligence",
  description: "Pakistan's first distributed causal climate-economic intelligence system",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}