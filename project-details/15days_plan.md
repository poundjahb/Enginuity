# 15‑Day MVP Plan — Clean Day-by-Day Grouping

> **Note:** This document is superseded by [`implementation_roadmap.md`](implementation_roadmap.md), which consolidates all plans into a single architecture-first roadmap. This file is kept for historical reference only.

## Overall Goal

**Prototype Target (Day 15)**  
A user submits a natural-language feature request, agents produce BRD + architecture + task plan, generate code in a demo repo, open PRs, run tests in CI, and deploy to staging for feedback.

## Days 1–3 — Platform Skeleton & Foundations

*   Stand up Ollama, CrewAI runtime, LangGraph runtime.
*   Stand up core API and backend runtime.
*   Create one workflow state model and artifact schema.
*   Keep relational persistence for request lifecycle in existing DB.
*   Define memory object schema for future ChromaDB write/read integration (memory type, source artifact, confidence, timestamp).
*   Connect to one GitHub org/repo.
*   Connect to one staging environment.
*   Deliver Day 2 professional portal shell:
    *   Menu
    *   Header
    *   Intake
    *   Requests
    *   Monitoring
    *   Artifacts sections
*   Integrate clarification loop entry point in the portal.


## Days 4–6 — Front Workflow (Intake → Analysis → Architecture)

*   Build Receptionist agent.
*   Build Analyst agent.
*   Build Architect agent.
*   Implement clarification loop.
*   Implement BRD approval gate with human approval.
*   Generate BRD artifacts.
*   Generate architecture output.
*   Store clarified request summary, approved BRD excerpts, and architecture decisions as stable artifacts.
*   Ensure outputs are suitable for downstream planning and memory ingestion.
*   Day 1–6 outputs remain unchanged before enabling memory writes.


## Days 7–9 — Delivery Workflow + ChromaDB Memory Foundation

### Core Delivery Flow

*   Add PM agent.
*   Add Developer agent.
*   Auto-create GitHub issues.
*   Auto-create implementation branches.
*   Generate code and tests.
*   Open PRs automatically.

### ChromaDB Integration

*   Day 7: introduce ChromaDB service.
*   Day 7: add memory repository module in backend.
*   Day 7: add memory write hooks for finalized/validated artifacts (avoid raw noisy transcripts).
*   Day 8: add retrieval hooks for PM and Developer agents before planning/code generation.
*   Day 8–9: add memory filtering strategy:
    *   top‑k
    *   recency
    *   confidence threshold
    *   source tags
*   Day 9: verify GitHub issue/PR generation behavior remains stable with memory‑augmented prompts.

***

## Days 10–12 — Quality, Review, CI & Staging

*   Add Reviewer agent with rule-based checks.
*   Wire CI checks.
*   Enforce merge policy.
*   Add Reviewer checks for memory-grounded output consistency (detect contradictions against prior accepted decisions).
*   Add safeguards:
    *   deduplication
    *   max memory payload size
    *   graceful fallback when ChromaDB is unavailable
*   Deploy successful builds to staging.
*   Validate staging pipeline with memory-enabled runs.


## Days 13–15 — Pilot, Hardening‑Lite & Demo

*   Run 2–3 pilot requests end-to-end.
*   Run pilots with memory enabled.
*   Fix highest-impact failures.
*   Fix highest-impact memory retrieval/write defects.
*   Add minimal runbook.
*   Add escalation path.
*   Deliver runbook entries for memory operations:
    *   rebuild index
    *   rotate collections
    *   outage fallback
*   Measure impact:
    *   fewer repeated clarifications
    *   higher consistency of architecture and implementation outputs
*   Demo with measurable KPIs.
*   Validate at least one pilot request reaches:
    *   merged PR
    *   passing tests
    *   staging deployment


## Scope Boundaries (Unchanged)

### Must Be In Scope (Days 1–15)

*   Intake flow with clarification questions.
*   Analyst, Architect, PM, Developer, Reviewer agents.
*   LangGraph workflow with checkpoints and retry.
*   Ollama on‑prem inference for all agent tasks.
*   GitHub integration: issues, branch, PR, CI checks.
*   Staging deployment pipeline.
*   Basic audit log of decisions and approvals.

### Deferred After Day 15

*   Fine-tuning models.
*   Advanced compliance automation.
*   Multi-team portfolio orchestration.
*   Full policy engine with many risk classes.
*   Production auto-release for medium/high-risk work.
*   Deep observability dashboards and SLO automation.
*   LLM selection from frontend (explicitly Day 16+).

***

## Non‑Negotiable MVP Acceptance Criteria (Unchanged)

1.  End-to-end run completes without manual coding.
2.  At least one feature request becomes a merged PR with passing tests.
3.  Staging deployment works from merged code.
4.  Human approvals are enforced at BRD and release gates.
5.  Every run has traceable artifacts:
    *   request
    *   BRD
    *   architecture
    *   PR
    *   test result
    *   deployment result


## Reality Check (Unchanged)

15 days is enough for a working prototype, not for production-grade autonomy.  
This proves value and flow reliability; governance, security, and scale follow in the next phase.
