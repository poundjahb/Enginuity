# Enginuity — Architecture-First Implementation Roadmap

> **Single source of truth** for implementation sequencing.  
> The earlier `15days_plan.md` and `45days_plan.md` are superseded by this document and kept only as historical references.

---

## Guiding Principles

- **Architecture before velocity.** No feature is built without a clear architectural slot.
- **Agent-by-agent delivery.** Each agent slice is shipped end-to-end (agent → workflow node → route → portal) before moving to the next.
- **Human gates are non-negotiable.** BRD, Architecture, and Release approvals are always enforced.
- **Strict error semantics.** No silent degradation. Dependency unavailability → explicit 503/502 with actionable reason.
- **Privacy-first.** All inference stays on-prem via Ollama. No outbound calls for model inference.

---

## Phase 0 — Platform Skeleton (Completed)

| # | Deliverable | Status |
|---|---|---|
| 0.1 | FastAPI backend with SQLite persistence | ✅ Done |
| 0.2 | Ollama integration and health checks | ✅ Done |
| 0.3 | LangGraph + CrewAI runtime wired | ✅ Done |
| 0.4 | `DBConfiguredAgent` base class (DB-overridable prompts/tasks) | ✅ Done |
| 0.5 | Portal shell (intake, requests, monitoring, artifacts) | ✅ Done |
| 0.6 | Agent + Task definition management API | ✅ Done |

---

## Phase 1 — Receptionist-Analyst Slice

> **Goal:** A submitted request flows through Receptionist intake assessment → Analyst BRD drafting → human BRD approval gate — fully agent-driven with no hard-coded templates.

### 1.1 Receptionist Agent (Completed)

| # | Deliverable | Status |
|---|---|---|
| 1.1.1 | `ReceptionistAgent` (CrewAI + Ollama) — request classification, confidence scoring | ✅ Done |
| 1.1.2 | Clarification loop — questions returned when confidence < 0.7 | ✅ Done |
| 1.1.3 | `POST /requests` → runs receptionist flow → persists assessment | ✅ Done |
| 1.1.4 | `POST /requests/{id}/clarifications` → re-scores and unlocks BRD step | ✅ Done |

### 1.2 Analyst Agent

| # | Deliverable | Status |
|---|---|---|
| 1.2.1 | `AnalystAgent` (CrewAI + Ollama) — AI-generated BRD from assessed intake | ✅ Done |
| 1.2.2 | `AnalystBrd` Pydantic model — structured BRD sections (objective, problem, scope, criteria, assumptions, metrics) | ✅ Done |
| 1.2.3 | `analyst_flow.py` — LangGraph single-node workflow wrapping analyst execution | ✅ Done |
| 1.2.4 | `POST /requests/{id}/brd/generate` wired to real analyst agent (replaces static template) | ✅ Done |
| 1.2.5 | `ANALYST_MODEL` / `ANALYST_TIMEOUT_SECONDS` config settings | ✅ Done |
| 1.2.6 | Analyst agent + task seeded in DB at startup | ✅ Done |
| 1.2.7 | `POST /requests/{id}/brd/review` — approve / reject BRD (existing, unchanged) | ✅ Done |

### 1.3 BRD Approval Gate

| # | Deliverable | Status |
|---|---|---|
| 1.3.1 | Status machine: `assessment_complete` → `brd_pending_approval` → `brd_approved` / `brd_rejected` | ✅ Done |
| 1.3.2 | Rejected BRDs can be regenerated from new analyst run | ✅ Done |

---

## Phase 2 — Architect Slice

> **Goal:** Approved BRD triggers Architect agent to produce system requirements, architecture doc, and ADRs.

| # | Deliverable | Status |
|---|---|---|
| 2.1 | `ArchitectAgent` (CrewAI + Ollama) — architecture draft + NFRs | ⬜ Pending |
| 2.2 | `architect_flow.py` — LangGraph workflow node | ⬜ Pending |
| 2.3 | `RequestRecord` extended with `architecture_draft`, `architecture_status` columns | ⬜ Pending |
| 2.4 | `POST /requests/{id}/architecture/generate` route | ⬜ Pending |
| 2.5 | `POST /requests/{id}/architecture/review` route (approve / reject gate) | ⬜ Pending |
| 2.6 | Architect agent + task seeded in DB | ⬜ Pending |

---

## Phase 3 — Security / Risk Agent Slice

> **Goal:** Parallel to or after architecture, a Security/Risk Agent performs threat modeling and vulnerability triage on the planned change.

| # | Deliverable | Status |
|---|---|---|
| 3.1 | `SecurityRiskAgent` (CrewAI + Ollama) — threat model, risk score, mitigation recommendations | ⬜ Pending |
| 3.2 | `security_risk_flow.py` — LangGraph workflow node | ⬜ Pending |
| 3.3 | `RequestRecord` extended with `security_risk_report`, `risk_score`, `risk_status` columns | ⬜ Pending |
| 3.4 | `POST /requests/{id}/security/assess` route | ⬜ Pending |
| 3.5 | Security findings feed into Architecture approval gate | ⬜ Pending |
| 3.6 | Security agent + task seeded in DB | ⬜ Pending |

---

## Phase 4 — PM / Planning Slice

| # | Deliverable | Status |
|---|---|---|
| 4.1 | `PMAgent` — epic/story/task decomposition, milestone plan | ⬜ Pending |
| 4.2 | `pm_flow.py` — LangGraph workflow node | ⬜ Pending |
| 4.3 | Auto-create GitHub issues from approved plan | ⬜ Pending |
| 4.4 | `POST /requests/{id}/plan/generate` and `/plan/review` routes | ⬜ Pending |

---

## Phase 5 — Developer Slice

| # | Deliverable | Status |
|---|---|---|
| 5.1 | `DeveloperAgent` — code + tests + docs generation per story | ⬜ Pending |
| 5.2 | `developer_flow.py` — LangGraph workflow node | ⬜ Pending |
| 5.3 | Auto-create feature branch per story | ⬜ Pending |
| 5.4 | Open PRs automatically with generated code | ⬜ Pending |
| 5.5 | ChromaDB memory layer — retrieve prior decisions to augment prompts | ⬜ Pending |

---

## Phase 6 — Reviewer / QA Slice

| # | Deliverable | Status |
|---|---|---|
| 6.1 | `ReviewerAgent` — static analysis, architecture compliance, code review | ⬜ Pending |
| 6.2 | `reviewer_flow.py` — LangGraph workflow node | ⬜ Pending |
| 6.3 | Wire CI checks (tests, SAST, quality gates) | ⬜ Pending |
| 6.4 | Enforce merge policy — protected branch rules | ⬜ Pending |
| 6.5 | Memory-grounded consistency check (detect contradictions vs prior accepted decisions) | ⬜ Pending |

---

## Phase 7 — Release Slice

| # | Deliverable | Status |
|---|---|---|
| 7.1 | `ReleaseAgent` — staging deploy, release notes, production promotion | ⬜ Pending |
| 7.2 | `release_flow.py` — LangGraph workflow node | ⬜ Pending |
| 7.3 | Production release approval gate for medium/high-risk changes | ⬜ Pending |

---

## Phase 8 — Learning & Knowledge Slice

| # | Deliverable | Status |
|---|---|---|
| 8.1 | `LearningAgent` — postmortem extraction, prompt improvement signals | ⬜ Pending |
| 8.2 | ChromaDB memory write hooks for finalized artifacts | ⬜ Pending |
| 8.3 | Memory deduplication, max-payload, and outage-fallback safeguards | ⬜ Pending |

---

## Non-Negotiable MVP Acceptance Criteria

1. End-to-end run completes without manual coding.
2. At least one feature request becomes a merged PR with passing tests.
3. Staging deployment works from merged code.
4. Human approvals enforced at BRD, Architecture, and Release gates.
5. Every run has traceable artifacts: request → BRD → architecture → security report → PR → test result → deployment result.

---

## Deferred (Post-Phase 8)

- Frontend-driven LLM model selection per agent (see `45days_plan.md`).
- Fine-tuning models on internal examples.
- Advanced compliance automation.
- Multi-team portfolio orchestration.
- Full policy engine with many risk classes.
- Production auto-release for medium/high-risk work.
- Deep observability dashboards and SLO automation.
