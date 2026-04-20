import AppShell from "@/components/layout/app-shell";
import Panel from "@/components/ui/panel";

export default function KnowledgePage() {
  return (
    <AppShell pageTitle="Knowledge" pageSubtitle="Knowledge graph, retrieval traces, and research snapshots">
      <Panel title="Knowledge Placeholder">
        <p className="text-xl text-slate-300">No backend contract available yet. This placeholder is ready for RAG indexing and retrieval diagnostics.</p>
      </Panel>
    </AppShell>
  );
}
