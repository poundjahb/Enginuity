import AppShell from "@/components/layout/app-shell";
import Panel from "@/components/ui/panel";

export default function VaultPage() {
  return (
    <AppShell pageTitle="Vault" pageSubtitle="Secrets and key-management integrations will be introduced as backend endpoints mature">
      <Panel title="Vault Placeholder">
        <p className="text-xl text-slate-300">No backend contract available yet. This screen is intentionally scaffolded for future secure-secret workflows.</p>
      </Panel>
    </AppShell>
  );
}
