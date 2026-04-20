import Panel from "@/components/ui/panel";
import StatusPill from "@/components/ui/status-pill";

export default function GatekeeperView() {
  return (
    <div className="grid gap-5 lg:grid-cols-12">
      <Panel className="lg:col-span-12" title="Gate Active" rightSlot={<StatusPill tone="warning">Architecture Approval Required</StatusPill>}>
        <p className="text-xl text-amber-100">ID: #REQ-4098</p>
      </Panel>

      <Panel className="lg:col-span-6" title="User Request">
        <p className="text-2xl text-slate-100">Build a secure microservice for payment tokens.</p>
      </Panel>

      <Panel className="lg:col-span-6" title="Agent Output">
        <p className="text-2xl text-slate-100">Architecture Decision Record (Draft)</p>
        <p className="mt-3 text-lg text-slate-300">Confidence: High (88%)</p>
      </Panel>

      <Panel className="lg:col-span-12" title="Decision">
        <div className="flex flex-wrap gap-3">
          <button className="rounded-xl bg-emerald-500 px-5 py-3 text-base-950">Approve & Continue</button>
          <button className="rounded-xl bg-amber-500/80 px-5 py-3 text-base-950">Request Clarification</button>
          <button className="rounded-xl bg-red-500 px-5 py-3 text-white">Reject & Escalate</button>
        </div>
      </Panel>
    </div>
  );
}
