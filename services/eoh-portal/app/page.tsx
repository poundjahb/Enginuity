"use client";

import { useEffect, useMemo, useState } from "react";

type PortalSection = "intake" | "requests" | "monitoring" | "administration" | "artifacts";

type RequestSummary = {
  request_id: string;
  user_identity: string;
  status: string;
  request_type?: string | null;
  confidence_score?: number | null;
  updated_at: string;
};

type RequestListResponse = {
  items: RequestSummary[];
  total: number;
};

type RequestStatus = {
  request_id: string;
  status: string;
  request_type?: string | null;
  extracted_scope?: string | null;
  confidence_score?: number | null;
  clarification_questions: string[];
  clarification_answers: Record<string, string>;
  workflow_events: string[];
  brd_draft?: string | null;
  brd_status?: string | null;
  brd_review_comment?: string | null;
  updated_at: string;
};

type SubmitResult = {
  request_id?: string;
  status?: string;
  request_type?: string;
  extracted_scope?: string;
  confidence_score?: number;
  clarification_questions?: string[];
  error?: string;
};

type AgentDefinition = {
  agent_id: string;
  name: string;
  role: string;
  goal: string;
  backstory: string;
  llm_model_override?: string | null;
  is_active: boolean;
  is_locked: boolean;
  version: number;
  created_at: string;
  updated_at: string;
};

type AgentDefinitionListResponse = {
  items: AgentDefinition[];
  total: number;
};

type TaskDefinition = {
  task_id: string;
  agent_id: string;
  name: string;
  description_template: string;
  expected_output: string;
  async_execution: boolean;
  execution_order: number;
  is_active: boolean;
  is_locked: boolean;
  version: number;
  created_at: string;
  updated_at: string;
};

type TaskDefinitionListResponse = {
  items: TaskDefinition[];
  total: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const MODEL_OVERRIDE_OPTIONS = ["", "llama3.2:3b", "llama3.1:8b", "llama3.1:70b"];

export default function HomePage() {
  const [section, setSection] = useState<PortalSection>("intake");
  const [userIdentity, setUserIdentity] = useState("owner@org.local");
  const [businessContext, setBusinessContext] = useState("Internal automation");
  const [rawText, setRawText] = useState("");
  const [priorityHint, setPriorityHint] = useState("medium");
  const [clarificationAnswers, setClarificationAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [clarificationLoading, setClarificationLoading] = useState(false);
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [requestStatus, setRequestStatus] = useState<RequestStatus | null>(null);
  const [requests, setRequests] = useState<RequestSummary[]>([]);
  const [brdDraftLoading, setBrdDraftLoading] = useState(false);
  const [brdReviewLoading, setBrdReviewLoading] = useState(false);
  const [brdComment, setBrdComment] = useState("");
  const [agentDefinitions, setAgentDefinitions] = useState<AgentDefinition[]>([]);
  const [agentDefinitionsLoading, setAgentDefinitionsLoading] = useState(false);
  const [agentDefinitionSaving, setAgentDefinitionSaving] = useState(false);
  const [agentTasks, setAgentTasks] = useState<TaskDefinition[]>([]);
  const [agentTasksLoading, setAgentTasksLoading] = useState(false);
  const [taskSaving, setTaskSaving] = useState(false);
  const [taskReordering, setTaskReordering] = useState(false);
  const [taskDeactivatingId, setTaskDeactivatingId] = useState<string | null>(null);
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [taskName, setTaskName] = useState("");
  const [taskDescriptionTemplate, setTaskDescriptionTemplate] = useState("");
  const [taskExpectedOutput, setTaskExpectedOutput] = useState("");
  const [taskAsyncExecution, setTaskAsyncExecution] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState("receptionist");
  const [agentRole, setAgentRole] = useState("");
  const [agentGoal, setAgentGoal] = useState("");
  const [agentBackstory, setAgentBackstory] = useState("");
  const [agentModelOverride, setAgentModelOverride] = useState("");

  const currentRequestId = useMemo(
    () => result?.request_id || requestStatus?.request_id,
    [result?.request_id, requestStatus?.request_id],
  );

  const loadRequests = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/requests`);
      if (!response.ok) {
        return;
      }
      const data: RequestListResponse = await response.json();
      setRequests(data.items || []);
    } catch {
      // Keep UI available if listing endpoint is temporarily unavailable.
    }
  };

  const loadRequestStatus = async (requestId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/requests/${requestId}`);
      if (!response.ok) {
        return;
      }
      const data: RequestStatus = await response.json();
      setRequestStatus(data);
    } catch {
      // Keep existing status state when backend is temporarily unavailable.
    }
  };

  const loadAgentDefinitions = async () => {
    setAgentDefinitionsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/agents/definitions`);
      if (!response.ok) {
        return;
      }
      const data: AgentDefinitionListResponse = await response.json();
      const items = data.items || [];
      setAgentDefinitions(items);
      if (items.length > 0) {
        const preferred = items.find((item) => item.agent_id === selectedAgentId) || items[0];
        setSelectedAgentId(preferred.agent_id);
        setAgentRole(preferred.role);
        setAgentGoal(preferred.goal);
        setAgentBackstory(preferred.backstory);
        setAgentModelOverride(preferred.llm_model_override || "");
        await loadAgentTasks(preferred.agent_id);
      }
    } catch {
      // Keep UI responsive when definitions endpoint is unavailable.
    } finally {
      setAgentDefinitionsLoading(false);
    }
  };

  const resetTaskForm = () => {
    setEditingTaskId(null);
    setTaskName("");
    setTaskDescriptionTemplate("");
    setTaskExpectedOutput("");
    setTaskAsyncExecution(false);
  };

  const loadAgentTasks = async (agentId: string = selectedAgentId) => {
    if (!agentId) {
      return;
    }

    setAgentTasksLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/agents/${agentId}/tasks`);
      if (!response.ok) {
        return;
      }

      const data: TaskDefinitionListResponse = await response.json();
      const items = data.items || [];
      setAgentTasks(items);
      if (editingTaskId) {
        const selected = items.find((item) => item.task_id === editingTaskId);
        if (!selected) {
          resetTaskForm();
        }
      }
    } catch {
      // Keep UI responsive when task endpoint is unavailable.
    } finally {
      setAgentTasksLoading(false);
    }
  };

  const saveTaskDefinition = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedAgentId) {
      return;
    }

    const payload = {
      name: taskName,
      description_template: taskDescriptionTemplate,
      expected_output: taskExpectedOutput,
      async_execution: taskAsyncExecution,
    };

    setTaskSaving(true);
    setResult(null);
    try {
      const url = editingTaskId
        ? `${API_BASE_URL}/agents/${selectedAgentId}/tasks/${editingTaskId}`
        : `${API_BASE_URL}/agents/${selectedAgentId}/tasks`;
      const method = editingTaskId ? "PATCH" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "Task definition save failed" });
      } else {
        await loadAgentTasks(selectedAgentId);
        if (!editingTaskId) {
          resetTaskForm();
        }
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setTaskSaving(false);
    }
  };

  const beginTaskEdit = (task: TaskDefinition) => {
    setEditingTaskId(task.task_id);
    setTaskName(task.name);
    setTaskDescriptionTemplate(task.description_template);
    setTaskExpectedOutput(task.expected_output);
    setTaskAsyncExecution(task.async_execution);
  };

  const deactivateTaskDefinition = async (taskId: string) => {
    if (!selectedAgentId) {
      return;
    }

    setTaskDeactivatingId(taskId);
    setResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/agents/${selectedAgentId}/tasks/${taskId}`, {
        method: "DELETE",
      });
      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "Task deactivation failed" });
      } else {
        await loadAgentTasks(selectedAgentId);
        if (editingTaskId === taskId) {
          resetTaskForm();
        }
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setTaskDeactivatingId(null);
    }
  };

  const reorderTask = async (taskId: string, direction: "up" | "down") => {
    if (!selectedAgentId || taskReordering) {
      return;
    }

    const index = agentTasks.findIndex((item) => item.task_id === taskId);
    if (index < 0) {
      return;
    }

    const swapWith = direction === "up" ? index - 1 : index + 1;
    if (swapWith < 0 || swapWith >= agentTasks.length) {
      return;
    }

    const next = [...agentTasks];
    const [moved] = next.splice(index, 1);
    next.splice(swapWith, 0, moved);
    const orderedTaskIds = next.map((item) => item.task_id);

    setTaskReordering(true);
    setResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/agents/${selectedAgentId}/tasks/reorder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ordered_task_ids: orderedTaskIds }),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "Task reorder failed" });
      } else {
        setAgentTasks(data.items || []);
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setTaskReordering(false);
    }
  };

  const saveAgentDefinition = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedAgentId) {
      return;
    }

    setAgentDefinitionSaving(true);
    setResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/agents/definitions/${selectedAgentId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: agentRole,
          goal: agentGoal,
          backstory: agentBackstory,
          llm_model_override: agentModelOverride || null,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "Agent definition update failed" });
      } else {
        await loadAgentDefinitions();
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setAgentDefinitionSaving(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  useEffect(() => {
    loadAgentDefinitions();
  }, []);

  useEffect(() => {
    if (currentRequestId) {
      loadRequestStatus(currentRequestId);
    }
  }, [currentRequestId]);

  const submitRequest = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setResult(null);
    setRequestStatus(null);
    setClarificationAnswers({});

    try {
      const response = await fetch(`${API_BASE_URL}/requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel: "web",
          user_identity: userIdentity,
          business_context: businessContext,
          raw_text: rawText,
          priority_hint: priorityHint,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail?.message || data?.detail || "Request failed" });
      } else {
        setResult({
          request_id: data.request_id,
          status: data.status,
          request_type: data.request_type,
          extracted_scope: data.extracted_scope,
          confidence_score: data.confidence_score,
          clarification_questions: data.clarification_questions || [],
        });
        setSection("intake");
        await loadRequestStatus(data.request_id);
        await loadRequests();
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setLoading(false);
    }
  };

  const submitClarifications = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!currentRequestId) {
      return;
    }

    setClarificationLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/requests/${currentRequestId}/clarifications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: clarificationAnswers }),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "Clarification submission failed" });
      } else {
        setRequestStatus(data);
        await loadRequests();
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setClarificationLoading(false);
    }
  };

  const generateBrdDraft = async () => {
    if (!currentRequestId) {
      return;
    }

    setBrdDraftLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/requests/${currentRequestId}/brd/generate`, {
        method: "POST",
      });
      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "BRD generation failed" });
      } else {
        await loadRequestStatus(currentRequestId);
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setBrdDraftLoading(false);
    }
  };

  const submitBrdReview = async (decision: "approve" | "reject") => {
    if (!currentRequestId) {
      return;
    }

    setBrdReviewLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/requests/${currentRequestId}/brd/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision, comment: brdComment || null }),
      });
      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail || "BRD review failed" });
      } else {
        setRequestStatus(data);
        setBrdComment("");
        await loadRequests();
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setBrdReviewLoading(false);
    }
  };

  const menuItems: Array<{ key: PortalSection; label: string }> = [
    { key: "intake", label: "Intake" },
    { key: "requests", label: "Requests" },
    { key: "monitoring", label: "Monitoring" },
    { key: "administration", label: "Administration" },
    { key: "artifacts", label: "Artifacts" },
  ];

  const statusLabel = requestStatus?.status || result?.status || "not-started";

  return (
    <main className="portal-layout">
      <aside className="sidebar">
        <h1>Engineering Operations Hub</h1>
        <p>Day 2 Unified Portal</p>
        {menuItems.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`menu-button ${section === item.key ? "active" : ""}`}
            onClick={() => setSection(item.key)}
          >
            {item.label}
          </button>
        ))}
      </aside>

      <section className="main-panel">
        <header className="topbar">
          <div>
            <h2>Platform Workspace</h2>
            <p>Management, monitoring, intake, and clarification in one interface</p>
          </div>
          <div className="user-chip">Signed in: {userIdentity}</div>
        </header>

        <div className="content">
          {section === "intake" && (
            <div className="grid-two">
              <section className="card">
                <h3>Request Intake</h3>
                <p className="helper">Submit a request for receptionist assessment and clarifications when needed.</p>

                <form onSubmit={submitRequest}>
                  <label className="field">
                    User Identity
                    <input value={userIdentity} onChange={(e) => setUserIdentity(e.target.value)} required />
                  </label>

                  <label className="field">
                    Business Context
                    <input value={businessContext} onChange={(e) => setBusinessContext(e.target.value)} />
                  </label>

                  <label className="field">
                    Priority
                    <select value={priorityHint} onChange={(e) => setPriorityHint(e.target.value)}>
                      <option value="low">low</option>
                      <option value="medium">medium</option>
                      <option value="high">high</option>
                    </select>
                  </label>

                  <label className="field">
                    Unstructured Request
                    <textarea value={rawText} onChange={(e) => setRawText(e.target.value)} required rows={7} />
                  </label>

                  <button disabled={loading} type="submit" className="primary">
                    {loading ? "Submitting..." : "Submit Request"}
                  </button>
                </form>
              </section>

              <section className="card">
                <h3>Intake Status</h3>
                {result?.error && <p className="error">Error: {result.error}</p>}

                {currentRequestId && (
                  <>
                    <p><strong>request_id:</strong> {currentRequestId}</p>
                    <p>
                      <strong>status:</strong>{" "}
                      <span className={`status-badge status-${statusLabel}`}>{statusLabel}</span>
                    </p>
                    <p><strong>request type:</strong> {requestStatus?.request_type || result?.request_type || "pending"}</p>
                    <p><strong>scope:</strong> {requestStatus?.extracted_scope || result?.extracted_scope || "pending"}</p>
                    <p>
                      <strong>confidence:</strong>{" "}
                      {typeof (requestStatus?.confidence_score ?? result?.confidence_score) === "number"
                        ? `${Math.round((requestStatus?.confidence_score ?? result?.confidence_score ?? 0) * 100)}%`
                        : "pending"}
                    </p>
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => currentRequestId && loadRequestStatus(currentRequestId)}
                    >
                      Refresh Status
                    </button>
                  </>
                )}

                {!currentRequestId && <p className="helper">Submit a request to start Day 2 assessment.</p>}
              </section>

              {requestStatus?.status === "clarifying" && requestStatus.clarification_questions.length > 0 && (
                <section className="card">
                  <h3>Clarification Chat</h3>
                  <p className="helper">Answer the questions to complete receptionist assessment.</p>
                  <form onSubmit={submitClarifications}>
                    {requestStatus.clarification_questions.map((question) => (
                      <label key={question} className="field">
                        {question}
                        <input
                          required
                          value={clarificationAnswers[question] || ""}
                          onChange={(e) =>
                            setClarificationAnswers((prev) => ({
                              ...prev,
                              [question]: e.target.value,
                            }))
                          }
                        />
                      </label>
                    ))}
                    <button type="submit" disabled={clarificationLoading} className="primary">
                      {clarificationLoading ? "Submitting..." : "Submit Clarifications"}
                    </button>
                  </form>
                </section>
              )}
            </div>
          )}

          {section === "requests" && (
            <section className="card">
              <h3>Recent Requests</h3>
              <p className="helper">Management view of latest request activity.</p>
              <button type="button" className="secondary" onClick={loadRequests}>Refresh List</button>
              <table className="requests-table">
                <thead>
                  <tr>
                    <th>Request</th>
                    <th>User</th>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((request) => (
                    <tr key={request.request_id}>
                      <td>{request.request_id.slice(0, 8)}</td>
                      <td>{request.user_identity}</td>
                      <td><span className={`status-badge status-${request.status}`}>{request.status}</span></td>
                      <td>{request.request_type || "pending"}</td>
                      <td>{typeof request.confidence_score === "number" ? `${Math.round(request.confidence_score * 100)}%` : "-"}</td>
                    </tr>
                  ))}
                  {requests.length === 0 && (
                    <tr>
                      <td colSpan={5}>No requests yet.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </section>
          )}

          {section === "monitoring" && (
            <section className="card">
              <h3>Workflow Monitoring</h3>
              <p className="helper">Real-time state and event trail for the active request.</p>
              {!requestStatus && <p className="helper">Submit an intake request to populate monitoring telemetry.</p>}
              {requestStatus && (
                <>
                  <p><strong>Current state:</strong> <span className={`status-badge status-${requestStatus.status}`}>{requestStatus.status}</span></p>
                  <p><strong>Last updated:</strong> {new Date(requestStatus.updated_at).toLocaleString()}</p>
                  <h4>Recent Events</h4>
                  <ul className="events">
                    {requestStatus.workflow_events.map((event) => (
                      <li key={event}>{event}</li>
                    ))}
                  </ul>
                </>
              )}
            </section>
          )}

          {section === "artifacts" && (
            <section className="card">
              <h3>Artifacts</h3>
              <p className="helper">Day 3 implementation: generate BRD draft and process reviewer approval decision.</p>

              {!currentRequestId && <p className="helper">Submit and complete intake flow first to generate BRD.</p>}

              {currentRequestId && (
                <>
                  <p><strong>request_id:</strong> {currentRequestId}</p>
                  <p><strong>brd status:</strong> {requestStatus?.brd_status || "not-generated"}</p>

                  {(requestStatus?.status === "assessment_complete" || requestStatus?.status === "brd_rejected") && (
                    <button type="button" className="primary" disabled={brdDraftLoading} onClick={generateBrdDraft}>
                      {brdDraftLoading ? "Generating BRD..." : "Generate BRD Draft"}
                    </button>
                  )}

                  {requestStatus?.brd_draft && (
                    <>
                      <h4>BRD Draft</h4>
                      <pre className="artifact-draft">{requestStatus.brd_draft}</pre>
                    </>
                  )}

                  {requestStatus?.brd_status === "pending_approval" && (
                    <>
                      <label className="field">
                        Review Comment
                        <textarea value={brdComment} onChange={(event) => setBrdComment(event.target.value)} rows={3} />
                      </label>
                      <div style={{ display: "flex", gap: "0.6rem" }}>
                        <button
                          type="button"
                          className="primary"
                          disabled={brdReviewLoading}
                          onClick={() => submitBrdReview("approve")}
                        >
                          Approve BRD
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          disabled={brdReviewLoading}
                          onClick={() => submitBrdReview("reject")}
                        >
                          Reject BRD
                        </button>
                      </div>
                    </>
                  )}

                  {requestStatus?.brd_review_comment && (
                    <p><strong>last review comment:</strong> {requestStatus.brd_review_comment}</p>
                  )}
                </>
              )}
            </section>
          )}

          {section === "administration" && (
            <section className="card">
              <h3>Agent Definitions</h3>
              <p className="helper">Manage CrewAI role, goal, and backstory stored in SQLite.</p>

              <button type="button" className="secondary" onClick={loadAgentDefinitions}>
                {agentDefinitionsLoading ? "Refreshing..." : "Refresh Definitions"}
              </button>

              {agentDefinitions.length === 0 && <p className="helper">No agent definitions found.</p>}

              {agentDefinitions.length > 0 && (
                <>
                  <label className="field">
                    Agent
                    <select
                      value={selectedAgentId}
                      onChange={(event) => {
                        const nextId = event.target.value;
                        setSelectedAgentId(nextId);
                        const selected = agentDefinitions.find((item) => item.agent_id === nextId);
                        if (selected) {
                          setAgentRole(selected.role);
                          setAgentGoal(selected.goal);
                          setAgentBackstory(selected.backstory);
                          setAgentModelOverride(selected.llm_model_override || "");
                        }
                        resetTaskForm();
                        loadAgentTasks(nextId);
                      }}
                    >
                      {agentDefinitions.map((definition) => (
                        <option key={definition.agent_id} value={definition.agent_id}>
                          {definition.name} ({definition.agent_id})
                        </option>
                      ))}
                    </select>
                  </label>

                  <form onSubmit={saveAgentDefinition}>
                    <label className="field">
                      Role
                      <input value={agentRole} onChange={(event) => setAgentRole(event.target.value)} required />
                    </label>

                    <label className="field">
                      Goal
                      <textarea value={agentGoal} onChange={(event) => setAgentGoal(event.target.value)} rows={4} required />
                    </label>

                    <label className="field">
                      Backstory
                      <textarea
                        value={agentBackstory}
                        onChange={(event) => setAgentBackstory(event.target.value)}
                        rows={6}
                        required
                      />
                    </label>

                    <label className="field">
                      LLM Model Override
                      <select
                        value={agentModelOverride}
                        onChange={(event) => setAgentModelOverride(event.target.value)}
                      >
                        {MODEL_OVERRIDE_OPTIONS.map((option) => (
                          <option key={option || "__default"} value={option}>
                            {option || "Default (from backend config)"}
                          </option>
                        ))}
                        {agentModelOverride && !MODEL_OVERRIDE_OPTIONS.includes(agentModelOverride) && (
                          <option value={agentModelOverride}>{agentModelOverride}</option>
                        )}
                      </select>
                    </label>

                    <button type="submit" className="primary" disabled={agentDefinitionSaving}>
                      {agentDefinitionSaving ? "Saving..." : "Save Definition"}
                    </button>
                  </form>

                  <hr style={{ margin: "1.4rem 0", border: 0, borderTop: "1px solid var(--line)" }} />
                  <h4>Agent Tasks</h4>
                  <p className="helper">Tasks execute in ascending order and updates apply to new runs immediately.</p>

                  <button type="button" className="secondary" onClick={() => loadAgentTasks(selectedAgentId)}>
                    {agentTasksLoading ? "Refreshing Tasks..." : "Refresh Tasks"}
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    style={{ marginLeft: "0.6rem" }}
                    onClick={resetTaskForm}
                  >
                    New Task
                  </button>

                  <table className="requests-table" style={{ marginTop: "1rem" }}>
                    <thead>
                      <tr>
                        <th>Order</th>
                        <th>Name</th>
                        <th>Async</th>
                        <th>Version</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {agentTasks.map((task, index) => (
                        <tr key={task.task_id}>
                          <td>{task.execution_order}</td>
                          <td>{task.name}</td>
                          <td>{task.async_execution ? "true" : "false"}</td>
                          <td>{task.version}</td>
                          <td>
                            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                              <button type="button" className="secondary" onClick={() => beginTaskEdit(task)}>
                                Edit
                              </button>
                              <button
                                type="button"
                                className="secondary"
                                disabled={index === 0 || taskReordering}
                                onClick={() => reorderTask(task.task_id, "up")}
                              >
                                Up
                              </button>
                              <button
                                type="button"
                                className="secondary"
                                disabled={index === agentTasks.length - 1 || taskReordering}
                                onClick={() => reorderTask(task.task_id, "down")}
                              >
                                Down
                              </button>
                              <button
                                type="button"
                                className="secondary"
                                disabled={taskDeactivatingId === task.task_id}
                                onClick={() => deactivateTaskDefinition(task.task_id)}
                              >
                                {taskDeactivatingId === task.task_id ? "Deactivating..." : "Deactivate"}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {agentTasks.length === 0 && (
                        <tr>
                          <td colSpan={5}>No active tasks found.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>

                  <form onSubmit={saveTaskDefinition} style={{ marginTop: "1rem" }}>
                    <h4>{editingTaskId ? "Edit Task" : "Create Task"}</h4>
                    <label className="field">
                      Task Name
                      <input value={taskName} onChange={(event) => setTaskName(event.target.value)} required />
                    </label>
                    <label className="field">
                      Description Template
                      <textarea
                        value={taskDescriptionTemplate}
                        onChange={(event) => setTaskDescriptionTemplate(event.target.value)}
                        rows={7}
                        required
                      />
                    </label>
                    <label className="field">
                      Expected Output
                      <textarea
                        value={taskExpectedOutput}
                        onChange={(event) => setTaskExpectedOutput(event.target.value)}
                        rows={3}
                        required
                      />
                    </label>

                    <label className="field" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <input
                        type="checkbox"
                        checked={taskAsyncExecution}
                        onChange={(event) => setTaskAsyncExecution(event.target.checked)}
                      />
                      Run asynchronously (async_execution)
                    </label>

                    <button type="submit" className="primary" disabled={taskSaving}>
                      {taskSaving ? "Saving Task..." : editingTaskId ? "Update Task" : "Create Task"}
                    </button>
                  </form>
                </>
              )}
            </section>
          )}
        </div>
      </section>
    </main>
  );
}
