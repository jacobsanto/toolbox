import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { L } from "@/lib/labels";

export const metadata: Metadata = {
  title: L.appName,
  description: "Agentic OS — τοπικό κέντρο ελέγχου AI πρακτόρων",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="el" className="dark">
      <body className="min-h-screen">
        <header className="border-b border-zinc-800 bg-zinc-950/80 sticky top-0 z-10 backdrop-blur">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 text-sm">
            <Link href="/" className="font-semibold tracking-tight text-zinc-100">
              🏛️ {L.appName}
            </Link>
            <Link href="/" className="text-zinc-400 hover:text-zinc-100">
              {L.agents}
            </Link>
            <Link href="/runs" className="text-zinc-400 hover:text-zinc-100">
              {L.runs}
            </Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
