import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MultiTenant App",
  description: "Multi-tenant SaaS with OAuth login",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
