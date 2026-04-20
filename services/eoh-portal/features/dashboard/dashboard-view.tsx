"use client";

import MetricCard from "@/components/ui/metric-card";
import Panel from "@/components/ui/panel";
import StatusPill from "@/components/ui/status-pill";

import { useAgentStream } from "@/hooks/use-agent-stream";

export default function DashboardView() {
  const { feed } = useAgentStream();

  return (
    <div className="grid gap-5 lg:grid-cols-12">
      <div className="grid gap-4 sm:grid-cols-2 lg:col-span-12 xl:grid-cols-4">
        <MetricCard label="System Health" value="98%" hint="Realtime cluster status" />
        <MetricCard label="Lead Time to Staging" value="3h 12m" hint="7-day average" />
        <MetricCard label="Agent Rework Rate" value="15%" hint="Rolling 24h" />
        <MetricCard label="Human Interventions" value="3" hint="Last 24h" />
      </div>

      <Panel className="lg:col-span-7" title="Activity Feed" rightSlot={<StatusPill tone="success">Live</StatusPill>}>
        <ul className="space-y-4">
          {feed.slice(0, 4).map((event) => (
            <li key={event.id} className="flex gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-3">
              <span className="mt-2 h-3 w-3 rounded-full bg-emerald-300" />
              <div>
                <p className="text-xl text-slate-200">
                  <span className="font-semibold text-emerald-200">{event.source}</span>: {event.message}
                </p>
                <p className="text-sm text-slate-400">{event.ts}</p>
              </div>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel className="lg:col-span-5" title="Self-Healing Log">
        <p className="text-xl text-slate-200">AdmAgent resolved 4 CI timeout events automatically.</p>
      </Panel>

      <Panel className="lg:col-span-12" title="Resource Monitor">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-emerald-400/25 bg-emerald-500/10 p-4 text-lg text-emerald-100">Local GPU #1: 80%</div>
          <div className="rounded-xl border border-sky-400/25 bg-sky-500/10 p-4 text-lg text-sky-100">Local GPU #2: 76%</div>
          <div className="rounded-xl border border-amber-400/25 bg-amber-500/10 p-4 text-lg text-amber-100">Queue Depth: 12 tasks</div>
        </div>
      </Panel>
    </div>
  );
}
