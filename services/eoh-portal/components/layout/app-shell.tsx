"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { NAV_ITEMS } from "@/lib/config/navigation";
import { cn } from "@/lib/utils/cn";

type AppShellProps = {
  pageTitle: string;
  pageSubtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export default function AppShell({ pageTitle, pageSubtitle, actions, children }: AppShellProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-base-950 text-slate-100">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_10%_0%,rgba(23,217,163,0.2),transparent_35%),radial-gradient(circle_at_95%_0%,rgba(33,212,253,0.15),transparent_38%)]" />
      <div className="absolute inset-0 -z-10 bg-mesh-grid bg-grid opacity-35" />

      <header className="sticky top-0 z-20 border-b border-sky-300/15 bg-base-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-[1360px] items-center justify-between px-6 py-4">
          <div className="flex items-center gap-8">
            <div>
              <p className="text-3xl font-semibold leading-none text-emerald-300">Hub Commander</p>
            </div>
            <nav className="flex items-center gap-2">
              {NAV_ITEMS.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "rounded-xl px-4 py-2 text-2xl text-slate-300 transition",
                      active
                        ? "bg-emerald-400/20 text-emerald-200 shadow-glow"
                        : "hover:bg-slate-800/60 hover:text-slate-100",
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="hidden md:block">{actions}</div>
        </div>
      </header>

      <main className="mx-auto max-w-[1360px] px-6 py-8">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <h1 className="text-6xl font-semibold tracking-tight">{pageTitle}</h1>
            {pageSubtitle ? <p className="mt-3 text-2xl text-slate-300">{pageSubtitle}</p> : null}
          </div>
          <div className="md:hidden">{actions}</div>
        </div>
        {children}
      </main>
    </div>
  );
}
