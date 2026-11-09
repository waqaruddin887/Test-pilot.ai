import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "TestPilot AI · Fixture laboratory",
  description: "Evidence-backed testing of controlled synthetic fixtures.",
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
