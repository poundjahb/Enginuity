"use client";

import Panel from "@/components/ui/panel";
import StatusPill from "@/components/ui/status-pill";
import { useAgentStream } from "@/hooks/use-agent-stream";

const stateColor: Record<string, string> = {
  complete: "bg-sky-500/30 border-sky-300/40 text-sky-100",
  running: "bg-amber-500/20 border-amber-300/40 text-amber-100",
  failed: "bg-red-500/20 border-red-300/40 text-red-100",
  idle: "bg-slate-500/20 border-slate-300/30 text-slate-200",
  blocked: "bg-red-500/20 border-red-300/40 text-red-100",
};

export default function MonitoringView() {
  const { nodes, feed } = useAgentStream();

  return (
    <div className="grid gap-5 lg:grid-cols-12">
      <Panel className="lg:col-span-8" title="Live Graph Monitor: REQ-4098" rightSlot={<StatusPill tone="success">Streaming</StatusPill>}>
        <div className="flex flex-wrap gap-3">
          {nodes.map((node) => (
            <div key={node.id} className={`min-w-[150px] rounded-xl border px-4 py-3 ${stateColor[node.state] || stateColor.idle}`}>
              <p className="text-lg font-semibold">{node.label}</p>
              <p className="text-sm uppercase">{node.state}</p>
              {node.retries ? <p className="text-xs">{node.retries} retries</p> : null}
            </div>
          ))}
        </div>
      </Panel>

      <Panel className="lg:col-span-4" title="Streaming Logs">
        <div className="max-h-[420px] space-y-2 overflow-auto rounded-xl border border-slate-800 bg-slate-950/70 p-3 font-mono text-sm">
          {feed.map((event) => (
            <p key={event.id} className="text-slate-200">
              <span className="text-emerald-300">{event.source}</span>: {event.message}
            </p>
          ))}
        </div>
      </Panel>

      <Panel className="lg:col-span-12" title="Administrative Actions">
        <div className="flex flex-wrap gap-3">
          <button className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-slate-100">Fine-tune retry policy</button>
          <button className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-slate-100">Resume blocked node</button>
          <button className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-slate-100">Export incident trace</button>
        </div>
      </Panel>
    </div>
  );
}
