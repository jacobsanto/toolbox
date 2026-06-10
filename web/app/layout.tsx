import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { L, L2 } from "@/lib/labels";

export const metadata: Metadata = {
  title: L.appName,
  description: "Agentic OS — τοπικό κέντρο ελέγχου AI πρακτόρων",
};

const NAV = [
  { href: "/", label: L.agents },
  { href: "/runs", label: L.runs },
  { href: "/room", label: `🗣️ ${L2.room}` },
  { href: "/artifacts", label: `🗂️ ${L2.artifacts}` },
  { href: "/inbox", label: `📥 ${L2.inbox}` },
  { href: "/memory", label: `🧠 ${L2.memory}` },
  { href: "/ask", label: `🎙️ ${L2.ask}` },
  { href: "/budgets", label: `💰 ${L2.budgets}` },
  { href: "/connectors", label: `🔌 ${L2.connectors}` },
  { href: "/standards", label: `🧬 ${L2.standards}` },
  { href: "/journal", label: `📔 ${L2.journal}` },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="el" className="dark">
      <body className="min-h-screen">
        <header className="border-b border-zinc-800 bg-zinc-950/80 sticky top-0 z-10 backdrop-blur">
          <nav className="mx-auto flex max-w-6xl items-center gap-4 overflow-x-auto px-4 py-3 text-sm">
            <Link href="/" className="shrink-0 font-semibold tracking-tight text-zinc-100">
              🏛️ {L.appName}
            </Link>
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="shrink-0 text-zinc-400 hover:text-zinc-100"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
