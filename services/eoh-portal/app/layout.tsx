import "./globals.css";

export const metadata = {
  title: "Engineering Operations Hub",
  description: "Unified intake, management, and monitoring portal",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
