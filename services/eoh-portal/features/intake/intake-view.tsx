"use client";

import { useMemo, useState } from "react";

import Panel from "@/components/ui/panel";
import StatusPill from "@/components/ui/status-pill";
import type { DynamicSchema } from "@/lib/types/forms";

const DYNAMIC_SCHEMA: DynamicSchema = {
  schemaVersion: "3.2",
  requestClass: "GREENFIELD",
  fields: [
    { id: "requestClass", label: "Request Class", type: "select", options: ["GREENFIELD", "MODIFICATION"], required: true },
    { id: "businessValue", label: "Business Value", type: "text", placeholder: "Define core objective" },
    { id: "priority", label: "Strategic Priority", type: "select", options: ["LOW", "MEDIUM", "HIGH", "CRITICAL"], required: true },
    { id: "nfr", label: "Non-functional Requirements", type: "multiselect", options: ["ENCRYPTION", "SAST", "AUDIT LOGGING"] },
    { id: "integrations", label: "Integration Points", type: "multiselect", options: ["ORACLE DB", "INTERNAL S3", "GITHUB"] },
  ],
};

export default function IntakeView() {
  const [synopsis, setSynopsis] = useState(
    "Create a microservice that periodically syncs data from an internal Oracle DB to an S3-compatible bucket, ensuring encryption at rest.",
  );

  const readiness = useMemo(() => {
    const metaCount = DYNAMIC_SCHEMA.fields.length;
    return `High (88% - ${metaCount} metadata fields provided)`;
  }, []);

  return (
    <div className="grid gap-5 lg:grid-cols-12">
      <Panel className="lg:col-span-7" title="Request Synopsis">
        <textarea
          className="h-64 w-full rounded-xl border border-sky-300/35 bg-base-900/75 p-4 text-2xl text-slate-100 outline-none ring-sky-300/50 transition focus:ring"
          value={synopsis}
          onChange={(e) => setSynopsis(e.target.value)}
        />
        <div className="mt-4">
          <StatusPill tone="success">Agent Readiness: {readiness}</StatusPill>
        </div>
      </Panel>

      <Panel className="lg:col-span-5" title={`Dynamic Metadata (v${DYNAMIC_SCHEMA.schemaVersion} Schema)`}>
        <div className="space-y-3">
          {DYNAMIC_SCHEMA.fields.map((field) => (
            <div key={field.id} className="space-y-1">
              <label className="block text-sm uppercase tracking-wide text-slate-300">{field.label}</label>
              {field.type === "text" ? (
                <input className="w-full rounded-lg border border-slate-700 bg-slate-900/75 px-3 py-2 text-slate-100" placeholder={field.placeholder || ""} />
              ) : (
                <select className="w-full rounded-lg border border-slate-700 bg-slate-900/75 px-3 py-2 text-slate-100">
                  {(field.options || []).map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </select>
              )}
            </div>
          ))}
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3">
          <button className="rounded-xl bg-emerald-500 px-4 py-3 text-base-950 transition hover:bg-emerald-400">Review & Submit</button>
          <button className="rounded-xl border border-amber-400/50 bg-amber-500/15 px-4 py-3 text-amber-200 transition hover:bg-amber-500/25">Reload DB Config</button>
        </div>
      </Panel>
    </div>
  );
}
