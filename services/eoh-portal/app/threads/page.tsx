import AppShell from "@/components/layout/app-shell";
import IntakeView from "@/features/intake/intake-view";
import MonitoringView from "@/features/monitoring/monitoring-view";

export default function ThreadsPage() {
  return (
    <AppShell pageTitle="Threads" pageSubtitle="Dynamic intake forms and synchronous agent-state monitoring">
      <div className="space-y-6">
        <IntakeView />
        <MonitoringView />
      </div>
    </AppShell>
  );
}
