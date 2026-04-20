"use client";

import { useMemo } from "react";

import type { AgentFeedEvent, AgentNode } from "@/lib/types/workflow";

const NODES: AgentNode[] = [
  { id: "intake", label: "Intake", state: "complete" },
  { id: "brd", label: "BRD", state: "complete" },
  { id: "architecture", label: "Architecture", state: "complete" },
  { id: "planning", label: "Planning", state: "running" },
  { id: "dev-a", label: "DevAgent", state: "running" },
  { id: "dev-b", label: "DevAgent", state: "failed", retries: 9 },
];

const FEED: AgentFeedEvent[] = [
  {
    id: "evt-1",
    ts: "3 minutes ago",
    source: "IntakeAgent",
    message: "New request #4101 normalized",
    severity: "success",
  },
  {
    id: "evt-2",
    ts: "3 minutes ago",
    source: "AdmAgent",
    message: "Patched Llama-3-8B config for DevAgent",
    severity: "info",
  },
  {
    id: "evt-3",
    ts: "3 minutes ago",
    source: "AnalystAgent",
    message: "BRD #4099 ready for approval",
    severity: "success",
  },
  {
    id: "evt-4",
    ts: "Now",
    source: "Agent-Think",
    message: "Retrying DevAgent and re-planning after context length error",
    severity: "warning",
  },
];

export function useAgentStream() {
  const nodes = useMemo(() => NODES, []);
  const feed = useMemo(() => FEED, []);
  return { nodes, feed };
}
