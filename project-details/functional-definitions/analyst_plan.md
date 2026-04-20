## Plan: Receptionist-Analyst Slice Implementation

Implement the first architecture slice as a true agent handoff: Receptionist completes intake + clarification, Analyst generates BRD via agent runtime (not route template), and BRD approval gate controls progression. This plan is implementation-ready and scoped to this slice only.

**Steps**
1. Freeze slice boundary and states: keep current intake states and add/confirm BRD states used by this slice (`assessment_complete`, `brd_pending_approval`, `brd_approved`, `brd_rejected`). This is required before wiring new nodes.
2. Add Analyst agent module in backend using existing DBConfiguredAgent pattern from receptionist as template, including robust output parsing and defaults for malformed model output. *depends on 1*
3. Add default Analyst definition/task seed on startup so administration UI can edit role/goal/backstory/tasks immediately after deploy. *parallel with 2 once agent id/task ids are finalized*
4. Introduce BRD artifact contract updates in schemas: preserve current string draft for compatibility, and add optional structured metadata fields to support future traceability without breaking portal rendering. *depends on 1*
5. Move BRD generation responsibility from route template helper to Analyst execution path (route invokes analyst flow/service, not inline template). *depends on 2 and 4*
6. Expand workflow orchestration for this slice: receptionist output remains unchanged; analyst invocation is called only when request is in allowed preconditions (`assessment_complete` or `brd_rejected`). *depends on 2 and 5*
7. Keep BRD review gate behavior, but tighten guardrails: require pending BRD state before review, preserve rejection comments, and append deterministic workflow events for audit. *depends on 5*
8. Update portal artifact actions for this slice to remain aligned with new backend behavior (generate BRD button, approval/reject flow, comment persistence, status refresh). Ensure no UX regressions in intake/clarification sections. *depends on 5 and 7*
9. Run emergence checkpoint for slice A and capture findings: BRD quality, rejection frequency, parse failures, and ambiguous-intake patterns requiring prompt/task updates. *depends on 8*

**Implementation phases and parallelism**
1. Phase 1 (contract and seeds): steps 1, 3, 4.
2. Phase 2 (agent execution path): steps 2, 5, 6.
3. Phase 3 (gate and UI stabilization): steps 7, 8.
4. Phase 4 (emergence validation): step 9.

**Relevant files**
- /home/habibpoundja/pasf/services/backend/app/agents/receptionist.py — reference implementation for DB-configured agent behavior, parsing, normalization, and default task conventions.
- /home/habibpoundja/pasf/services/backend/app/agents/base_agent.py — shared execution/runtime contract to reuse for Analyst.
- /home/habibpoundja/pasf/services/backend/app/agents/analyst.py — new Analyst agent module.
- /home/habibpoundja/pasf/services/backend/app/workflow/receptionist_flow.py — maintain receptionist responsibilities; avoid regression.
- /home/habibpoundja/pasf/services/backend/app/workflow/analyst_flow.py — new orchestration wrapper for BRD generation path.
- /home/habibpoundja/pasf/services/backend/app/routes/requests.py — replace template BRD generator with analyst invocation and retain review gate.
- /home/habibpoundja/pasf/services/backend/app/schemas.py — BRD generation/review payload and response contract adjustments.
- /home/habibpoundja/pasf/services/backend/app/models.py — request status and BRD-related persistence fields (reuse existing columns; extend only if necessary).
- /home/habibpoundja/pasf/services/backend/app/main.py — seed default Analyst agent definition and task definition at startup.
- /home/habibpoundja/pasf/services/eoh-portal/app/page.tsx — ensure artifact UI calls same endpoints and reflects new analyst-produced output.

**Verification**
1. Backend unit-level checks:
- Analyst output parser tolerates non-ideal model responses and still returns valid BRD output or explicit error.
- Request state guards reject BRD generation when request is not `assessment_complete` or `brd_rejected`.
2. API integration checks:
- POST /requests creates request and reaches `assessment_complete` or `clarifying`.
- POST /requests/{request_id}/clarifications transitions to `assessment_complete`.
- POST /requests/{request_id}/brd/generate calls Analyst path and sets `brd_pending_approval`.
- POST /requests/{request_id}/brd/review with approve sets `brd_approved`; with reject sets `brd_rejected` and retains comment.
3. Portal manual checks:
- Intake and clarification behavior unchanged.
- BRD draft appears after generation and reflects analyst output.
- Approve/reject buttons and comment flow behave as expected.
4. Emergence checklist:
- Track parse failure rate, average confidence before BRD generation, BRD rejection rate, and top recurring reviewer comments.

**Decisions**
- Scope includes only Receptionist-Analyst slice end-to-end.
- BRD generation must be agent-driven (Analyst), not static template rendering.
- Existing BRD review endpoints are retained to minimize contract churn.
- Current approval model remains any authenticated user for MVP unless later tightened.

**Out of scope for this slice**
- Architect, Security and Risk, PM, Developer, Reviewer, Release, Learning implementation.
- GitHub issue/branch automation changes.
- Production policy engine hardening.

**Further considerations**
1. Decide whether to enforce reviewer identity capture now (`reviewed_by`) or defer to RBAC phase.
2. Decide whether BRD storage should remain markdown text only for this slice or include early JSON envelope in parallel.
3. Add migration strategy only if new persistence columns become mandatory; otherwise keep schema additive and backward compatible.