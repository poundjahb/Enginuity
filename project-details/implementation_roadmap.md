# Implementation Roadmap (Architecture-First, Agent-Driven)

## Purpose

This roadmap replaces calendar-first planning with capability-first delivery.
Implementation progresses by adding one agent interaction slice at a time,
including all required wiring/plumbing (state, schemas, orchestration, API,
UI visibility, and persistence), then validating emergent constraints before
unlocking the next slice.

## Planning Status

- This is the current source of truth for implementation sequencing.
- Historical plans remain available in:
  - `project-details/15days_plan.md`
  - `project-details/45days_plan.md`

## Core Principles

1. Agent handoff quality is the primary delivery metric.
2. Every slice is end-to-end and runnable with real upstream artifacts.
3. Approval gates block downstream execution when required.
4. Retries are idempotent.
5. Emergent constraints discovered during implementation must be captured
   before proceeding.
6. Platform adapters (for example GitHub) are delivery backends, not core
   workflow drivers.

## Workflow Backbone

Canonical progression (high level):

1. Intake and assessment
2. Clarification loop
3. BRD draft and BRD approval
4. Architecture draft and architecture approval
5. Threat modeling and security acceptance criteria
6. Planning and backlog decomposition
7. Delivery publication (issues, branches, PR references)
8. Optional later extensions: autonomous implementation, review, release,
   learning feedback loops

## Capability Slices

### Slice A - Receptionist -> Analyst

Goal:
Convert intake plus clarifications into a structured BRD draft and enforce
human approval.

Required implementation wiring:

- Lifecycle states for BRD draft/review/approved/rejected.
- BRD artifact schema and persisted version lineage.
- Orchestration node for Analyst execution.
- API endpoints to generate/review BRD.
- Portal visibility for BRD content and approval actions.

Exit criteria:

- BRD output validates against schema.
- Rejection loop works and preserves prior versions.
- No downstream execution without BRD approval.

Emergence checkpoint A:

- Measure ambiguity reduction from clarification loop.
- Capture recurring BRD quality failures.
- Update contracts/prompts only after evidence.

### Slice B - Analyst -> Architect

Goal:
Transform approved BRD into architecture decisions that are actionable for
planning.

Required implementation wiring:

- Architecture artifact schema (NFR mapping, decisions, risks, assumptions).
- Architecture lifecycle states and review metadata.
- Orchestration handoff from BRD-approved state.
- API endpoints to generate/review architecture.
- Portal visibility for architecture review.
- Trace links from architecture sections back to BRD requirements.

Exit criteria:

- Architecture is reviewable and approved through explicit gate.
- Traceability between BRD and architecture is queryable.
- Planning cannot run without architecture approval.

Emergence checkpoint B:

- Identify architecture-review bottlenecks.
- Validate architecture output readiness for planning automation.

### Slice B2 - Architect -> Security and Risk

Goal:
Convert approved architecture into actionable security constraints before
planning and implementation begin.

Required implementation wiring:

- Threat model artifact schema (assets, trust boundaries, abuse cases,
  mitigations, residual risk).
- Security acceptance criteria schema linked to BRD/architecture requirements.
- Vulnerability triage schema (severity, disposition, owner, target SLA).
- Orchestration node for Security and Risk agent execution.
- Security risk gate that blocks planning for unresolved medium/high risk.
- Portal visibility for threat model, security criteria, and triage decisions.

Exit criteria:

- Threat model and security acceptance criteria are generated and persisted.
- PM planning is blocked until security risk gate passes.
- Security outputs are trace-linked to architecture and BRD requirements.

Emergence checkpoint B2:

- Validate threat-model coverage quality and false-positive rate.
- Identify policy thresholds that cause excess friction or weak control.

### Slice C - Architect -> PM/Planner

Goal:
Generate backlog artifacts from approved architecture, security criteria, and
BRD, ready for
publication to a delivery platform.

Required implementation wiring:

- Planning/backlog schema (epics, stories, tasks, dependencies, priority).
- Orchestration node for PM planning.
- API endpoint to generate planning artifacts.
- Portal visibility for backlog and dependency ordering.
- Persisted trace chain from backlog item to source architecture/BRD elements.
- Persisted trace chain from backlog item to security acceptance criteria.

Exit criteria:

- Backlog generation is deterministic for same approved inputs.
- Dependencies and sequencing are explicit.
- Output is publish-ready for external tooling.
- Security acceptance criteria are represented in planning outputs.

Emergence checkpoint C:

- Validate planning completeness and decomposition quality.
- Capture recurring decomposition errors and tune rules.

### Slice C Adapter - Delivery Publication (GitHub)

Goal:
Publish planning artifacts to GitHub while preserving idempotency and
traceability.

Required implementation wiring:

- Service adapter to create issues and branches.
- Idempotent publish semantics (no duplicate issues on retry).
- Persisted external references (issue IDs/URLs/branch names).
- API endpoint for publication status and results.
- Portal visibility for created links and publish outcome.

Exit criteria:

- Publication creates expected artifacts once.
- Retries are safe.
- Full chain traceability reaches GitHub references.

## Cross-Cutting Engineering Workstreams

1. State model and persistence:
   request lifecycle, artifact lineage, approval metadata, workflow events.
2. Contracts and schemas:
   strict request/response and artifact envelopes per handoff.
3. Orchestration:
   graph transitions, conditional gates, deterministic retries.
4. API surface:
   generation, review, publication, and status retrieval endpoints.
5. Portal orchestration UI:
   visibility by stage, operator approvals, and artifact trace navigation.
6. Observability and audit:
   event timeline per request, gate decisions, and publish results.
7. Security assurance:
   threat-model coverage, vulnerability triage status, and risk disposition
   evidence across the workflow.

## Definition of Done (Roadmap Level)

The roadmap phase is considered successful when:

1. A request can traverse Slice A -> Slice B -> Slice C -> Delivery Adapter
   using real artifacts.
2. Gate enforcement is correct (no bypass of required approvals).
3. Each handoff validates against defined schemas.
4. End-to-end traceability is available from intake to delivery references.
5. Emergence notes are documented after each slice and reflected in next
   implementation decisions.
6. Security and Risk slice artifacts are present and approved before planning.
7. Vulnerability triage results are captured with explicit risk disposition.

## Out of Scope for This Roadmap Revision

- Replacing historical planning files.
- Full autonomous coding/reviewer/release pipelines in the same increment.
- Advanced policy engine and enterprise governance hardening.

## Document Governance

- Update this file when sequencing or gate semantics change.
- Keep historical context in legacy planning documents.
- Maintain the changelog section below for all roadmap revisions.

## Changelog

- 2026-04-20: Created architecture-first roadmap and set it as the active
   implementation planning reference, superseding day-based planning files.
- 2026-04-20: Added Security and Risk Agent slice, including threat modeling,
  security acceptance criteria, and vulnerability triage gate expectations.
