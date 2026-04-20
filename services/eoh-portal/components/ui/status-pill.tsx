import type { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

type StatusPillProps = {
  children: ReactNode;
  tone?: "info" | "success" | "warning" | "danger";
};

const toneClass: Record<NonNullable<StatusPillProps["tone"]>, string> = {
  info: "border-sky-300/35 bg-sky-400/15 text-sky-200",
  success: "border-emerald-300/35 bg-emerald-400/15 text-emerald-200",
  warning: "border-amber-300/35 bg-amber-400/15 text-amber-200",
  danger: "border-red-300/35 bg-red-400/15 text-red-200",
};

export default function StatusPill({ children, tone = "info" }: StatusPillProps) {
  return (
    <span className={cn("inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide", toneClass[tone])}>
      {children}
    </span>
  );
}
