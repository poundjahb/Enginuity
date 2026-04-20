import "./globals.css";
import "../styles/tokens.css";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hub Commander",
  description: "EOH control center for dynamic intake, gatekeeping, and agent-state monitoring",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
