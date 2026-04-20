import type { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

type PanelProps = {
  title?: string;
  rightSlot?: ReactNode;
  className?: string;
  children: ReactNode;
};

export default function Panel({ title, rightSlot, className, children }: PanelProps) {
  return (
    <section className={cn("rounded-2xl border border-sky-400/20 bg-slate-950/60 p-5 shadow-card backdrop-blur", className)}>
      {(title || rightSlot) && (
        <header className="mb-4 flex items-center justify-between gap-4">
          {title ? <h3 className="text-2xl font-semibold text-slate-100">{title}</h3> : <span />}
          {rightSlot}
        </header>
      )}
      {children}
    </section>
  );
}
