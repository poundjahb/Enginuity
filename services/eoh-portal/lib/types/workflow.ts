export type AgentNodeState = "idle" | "running" | "blocked" | "failed" | "complete";

export type AgentNode = {
  id: string;
  label: string;
  state: AgentNodeState;
  updatedAt?: string;
  retries?: number;
};

export type WorkflowRun = {
  requestId: string;
  nodes: AgentNode[];
  streamLog: string[];
  startedAt: string;
};

export type AgentFeedEvent = {
  id: string;
  ts: string;
  source: string;
  message: string;
  severity: "info" | "warning" | "error" | "success";
};
