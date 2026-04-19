## Plan: Post-Day-15 LLM Selection

Schedule frontend-driven LLM model selection as a post-Day-15 enhancement (Day 16+), while keeping the existing Day 1–Day 15 commitments unchanged and stable.

**Steps**
1. Phase A - Scheduling Boundary (Immediate planning action)
2. Mark LLM selection as explicitly out of scope for Day 1–Day 15 delivery.
3. Keep current runtime control during the 15-day plan via environment/default config only.
4. Add this feature to the first post-plan increment (Day 16+ backlog).
5. Dependencies: none.

6. Phase B - Post-Day-15 Backend Runtime Model State (Global Persisted)
7. Introduce persisted config state in backend storage for active receptionist model (global for all users/sessions).
8. Load active model at startup using precedence: persisted value -> `RECEPTIONIST_MODEL` env default.
9. Add helper functions for model state access/update (get active model, set active model, validate against Ollama tags).
10. Ensure model name normalization remains consistent with current `ollama/...` routing behavior.
11. Dependencies: depends on Phase A.

12. Phase C - Post-Day-15 Backend Model Management API
13. Add `GET /models/available` to return Ollama model names from `/api/tags` plus dependency error status when unavailable.
14. Add `GET /models/active` to return active model, source (`persisted` or `env-default`), and availability status.
15. Add `POST /models/active` to set active model with strict validation (reject unknown models with informative error payload).
16. Keep failure semantics explicit: return 4xx/5xx errors with actionable reason, never silently downgrade behavior.
17. Dependencies: depends on Phase B.

18. Phase D - Post-Day-15 Receptionist Flow Wiring to Active Model
19. Update receptionist assessment path to use the active model from runtime state instead of static config-only value.
20. Capture active model once at request start and pass through the full assessment execution to avoid mid-request race effects.
21. Preserve current strict error handling behavior (`503` when configured/selected model unavailable, `502` for agent execution failure).
22. Dependencies: depends on Phases B and C.

23. Phase E - Post-Day-15 Frontend LLM Selection UX
24. Add model selector UI in the intake experience to:
25. show current active model,
26. list available models,
27. allow switching active model.
28. Wire UI to `GET /models/available`, `GET /models/active`, and `POST /models/active`.
29. Show clear success/error feedback on selection changes; keep current intake submission UX untouched.
30. Dependencies: depends on Phase C.

31. Phase F - Post-Day-15 Configuration and Environment Consistency
32. Keep `RECEPTIONIST_MODEL` as startup fallback/default only (not authoritative once user selects from UI).
33. Ensure docker-compose and env docs reflect fallback semantics and include valid examples (including `llama3.1:8b` now present on PC1).
34. Dependencies: parallel with Phases C-E.

35. Phase G - Post-Day-15 Verification and Hardening
36. Validate happy path:
37. `GET /models/available` returns installed models,
38. `POST /models/active` switches model,
39. `/requests` uses selected model and completes.
40. Validate failure path:
41. selecting unknown model is rejected,
42. Ollama unavailable returns explicit dependency errors,
43. request creation blocked with clear reason when active model unavailable.
44. Validate persistence path:
45. restart backend container and confirm active model remains persisted globally.
46. Validate concurrency path:
47. switch model during active traffic; in-flight requests continue with captured model and do not fail due to state race.
48. Dependencies: depends on Phases D and E.

**Relevant files**
- `/home/habibpoundja/pasf/services/backend/app/config.py` — keep env-based default model as fallback only.
- `/home/habibpoundja/pasf/services/backend/app/db.py` — add persisted config state model/table support if needed.
- `/home/habibpoundja/pasf/services/backend/app/models.py` — add config-state persistence entity for active model.
- `/home/habibpoundja/pasf/services/backend/app/services/health.py` — reuse model discovery and availability checks for management APIs.
- `/home/habibpoundja/pasf/services/backend/app/agents/receptionist.py` — ensure active model is injected into LLM construction path.
- `/home/habibpoundja/pasf/services/backend/app/workflow/receptionist_flow.py` — pass active model through graph invocation state.
- `/home/habibpoundja/pasf/services/backend/app/routes/requests.py` — consume active model for request execution; keep strict errors.
- `/home/habibpoundja/pasf/services/backend/app/schemas.py` — add request/response schemas for model management routes.
- `/home/habibpoundja/pasf/services/backend/app/main.py` — initialize/persist config-state schema at startup as needed.
- `/home/habibpoundja/pasf/services/eoh-portal/app/page.tsx` — add model selection UI and API wiring.
- `/home/habibpoundja/pasf/docker-compose.yml` — document fallback semantics for `RECEPTIONIST_MODEL`.
- `/home/habibpoundja/pasf/.env.example` — add/update examples for model fallback and usage notes.

**Verification**
1. Confirm Day 1–Day 15 deliverables are unchanged and not blocked by this deferred feature.
2. On Day 16+ branch, run model-management API tests (`/models/available`, `/models/active` get/set).
3. Verify selected model is used by `/requests` and preserved across backend restart.
4. Verify unknown model selection is rejected with clear error details.
5. Verify dependency outage behavior remains explicit (no fallback bypass).

**Decisions**
- Frontend-driven model selection is deferred to post-Day-15 (Day 16+).
- Day 1–Day 15 remain focused on committed roadmap scope.
- Model selection is global and persisted when implemented.
- Existing `/requests` contract remains stable; model management is additive.
- Strict error behavior is preserved; no deterministic fallback bypass for model/runtime failures.

**Further Considerations**
1. Access control for model switching post-Day-15: Option A expose to all authenticated users; Option B restrict to admin/operator roles (recommended).
2. Auditability: persist `changed_by` and `changed_at` for model switch events.
3. UX safety: disable model switch while dependency health is unhealthy.
