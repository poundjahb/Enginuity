## Plan: SQLite Agent Task Definitions With Live Frontend Management

Move agent task definitions from hardcoded Python into SQLite-backed records linked to each agent, then expose frontend-managed create/update/deactivate with ordered execution and immediate effect on new runs.

**Steps**
1. Phase 1 - Data model and migration groundwork.
2. Add TaskDefinition model in services/backend/app/models.py with fields: task_id (string PK), agent_id (FK-like indexed relation to AgentDefinition.agent_id), name, description_template, expected_output, execution_order (int), is_active, is_locked, version, created_at, updated_at.
3. Add lightweight startup schema ensure function in services/backend/app/main.py for task_definitions columns using the same pattern as _ensure_requests_schema_columns; call it during startup before seeding.
4. Add default task seeding function in services/backend/app/main.py to create at least one receptionist task if none exists; preserve idempotency. Depends on 2 and 3.
5. Phase 2 - API contract and backend routes.
6. Extend services/backend/app/schemas.py with TaskDefinitionResponse, TaskDefinitionListResponse, TaskDefinitionCreate, TaskDefinitionUpdate, and TaskDefinitionReorder payloads (for ordered execution changes from frontend).
7. Add new router services/backend/app/routes/tasks.py with endpoints scoped by agent: list tasks, create task, update task, deactivate task (soft delete), reorder tasks. Enforce locked checks and version increment on updates. Depends on 2 and 6.
8. Register tasks router in services/backend/app/main.py. Depends on 7.
9. Phase 3 - Runtime execution integration.
10. Refactor receptionist task construction in services/backend/app/agents/receptionist.py to load active receptionist tasks from DB ordered by execution_order ascending, then build CrewAI Task objects dynamically from DB definitions.
11. Update execution path to run configured task sequence for receptionist and use final structured output contract expected by ReceptionistAssessment; fail fast with ReceptionistAgentError when no active tasks exist.
12. Keep immediate-effect semantics as agreed: changes apply to new runs only; in-flight runs keep the already loaded task sequence.
13. Phase 4 - Frontend management UX.
14. Extend administration section in services/eoh-portal/app/page.tsx with Task Management for selected agent: list ordered tasks, create task form, edit task, deactivate toggle/action, and move up/down reorder actions.
15. Add frontend fetch handlers for task CRUD/reorder endpoints and refresh task list after each mutation so updates are reflected immediately in UI and next backend invocation.
16. Optional cleanup split: extract agent/task admin UI from page.tsx into focused components once task UI lands, if file complexity becomes high. Parallel with 14-15.
17. Phase 5 - Verification and safety.
18. Validate API behavior manually: task create/update/deactivate/reorder, lock enforcement, version bump, and list ordering.
19. Validate runtime behavior by submitting requests before/after task updates and confirming new requests use the latest task definitions while running requests are unaffected.
20. Validate frontend behavior: optimistic feel (loading states + immediate refresh), error handling, and correct order persistence.

**Relevant files**
- /home/habibpoundja/pasf/services/backend/app/models.py - add TaskDefinition model aligned with AgentDefinition conventions.
- /home/habibpoundja/pasf/services/backend/app/schemas.py - add task CRUD and reorder schemas.
- /home/habibpoundja/pasf/services/backend/app/main.py - schema ensure, seed, and router registration.
- /home/habibpoundja/pasf/services/backend/app/routes/tasks.py - new task management API surface.
- /home/habibpoundja/pasf/services/backend/app/agents/receptionist.py - replace hardcoded Task with DB-driven ordered tasks.
- /home/habibpoundja/pasf/services/backend/app/routes/agents.py - reference update/lock/version behavior pattern for tasks.
- /home/habibpoundja/pasf/services/eoh-portal/app/page.tsx - administration UI enhancements for task lifecycle and ordering.

**Verification**
1. Run backend startup and confirm task_definitions table is present and seeded for receptionist.
2. Exercise task endpoints: create two tasks, reorder them, patch text, deactivate one, and verify list excludes inactive by default.
3. Submit intake request and confirm receptionist flow succeeds with active ordered tasks.
4. Update task definition from frontend, submit a new request, and verify new behavior is applied immediately.
5. Confirm deactivated task no longer participates in new runs.

**Decisions**
- Immediate update scope: applies to new runs only, not in-flight requests.
- Deactivate behavior: soft-delete only (is_active=false), no hard delete.
- Multi-task behavior: execute active tasks in configurable frontend-managed order.

**Further Considerations**
1. Sequence semantics: whether each task must produce a strict JSON contract or only the final task must output receptionist schema-compatible JSON.
2. Concurrency guard: whether to add simple optimistic concurrency check via version in PATCH payloads to prevent overwrite races.
3. Audit visibility: whether to expose inactive tasks in administration with a filter for potential reactivation in a later iteration.
