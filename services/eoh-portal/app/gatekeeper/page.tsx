import AppShell from "@/components/layout/app-shell";
import GatekeeperView from "@/features/gatekeeper/gatekeeper-view";

export default function GatekeeperPage() {
  return (
    <AppShell pageTitle="Gatekeeper Approval" pageSubtitle="Human-in-the-loop controls for critical release and design gates">
      <GatekeeperView />
    </AppShell>
  );
}
