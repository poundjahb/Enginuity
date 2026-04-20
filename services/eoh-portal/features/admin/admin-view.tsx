import Panel from "@/components/ui/panel";

const placeholders = [
  "Role-based access management",
  "Config registry for dynamic forms",
  "Model policy and approved list",
  "Secrets and vault integrations",
  "Audit retention and export controls",
];

export default function AdminView() {
  return (
    <div className="grid gap-5 lg:grid-cols-12">
      <Panel className="lg:col-span-12" title="Administration Workbench">
        <p className="text-lg text-slate-300">This screen is scaffolded for iterative backend integration and policy controls.</p>
      </Panel>

      <Panel className="lg:col-span-12" title="Planned Modules">
        <ul className="grid gap-3 md:grid-cols-2">
          {placeholders.map((item) => (
            <li key={item} className="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-slate-100">
              {item}
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}
