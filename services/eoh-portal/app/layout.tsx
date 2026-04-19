export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "Segoe UI, sans-serif", background: "#f4f7fb" }}>
        {children}
      </body>
    </html>
  );
}
