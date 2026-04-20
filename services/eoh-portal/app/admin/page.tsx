import AppShell from "@/components/layout/app-shell";
import AdminView from "@/features/admin/admin-view";

export default function AdminPage() {
  return (
    <AppShell pageTitle="Administration" pageSubtitle="Configuration, policy, and control-plane placeholders">
      <AdminView />
    </AppShell>
  );
}
