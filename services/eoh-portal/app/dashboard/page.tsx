import AppShell from "@/components/layout/app-shell";
import DashboardView from "@/features/dashboard/dashboard-view";

export default function DashboardPage() {
  return (
    <AppShell pageTitle="Dashboard" pageSubtitle="Operational visibility across autonomous delivery flows">
      <DashboardView />
    </AppShell>
  );
}
