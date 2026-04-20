## Plan: Frontend-Driven LLM Selection

Enable runtime LLM model selection from the frontend, persisted globally in backend storage, while keeping request processing strict (no silent fallback) and validating model availability against Ollama before use.

**Steps**
1. Phase A - Scope and Contract Alignment
2. Keep existing intake flow behavior and response contracts unchanged for `/requests` endpoints.
3. Add model-management capability as an additive API surface (no breaking changes to existing routes).
4. Confirm runtime policy: selected model must be validated against Ollama installed models before activation.
5. Dependencies: none.

6. Phase B - Backend Runtime Model State (Global Persisted)
7. Introduce persisted config state in backend storage for active receptionist model (global for all users/sessions).
8. Load active model at startup using precedence: persisted value -> `RECEPTIONIST_MODEL` env default.
9. Add helper functions for model state access/update (get active model, set active model, validate against Ollama tags).
10. Ensure model name normalization remains consistent with current `ollama/...` routing behavior.
11. Dependencies: depends on Phase A.

12. Phase C - Backend Model Management API
13. Add `GET /models/available` to return Ollama model names from `/api/tags` plus dependency error status when unavailable.
14. Add `GET /models/active` to return active model, source (`persisted` or `env-default`), and availability status.
15. Add `POST /models/active` to set active model with strict validation (reject unknown models with informative error payload).
16. Keep failure semantics explicit: return 4xx/5xx errors with actionable reason, never silently downgrade behavior.
17. Dependencies: depends on Phase B.

18. Phase D - Receptionist Flow Wiring to Active Model
19. Update receptionist assessment path to use the active model from runtime state instead of static config-only value.
20. Capture active model once at request start and pass through the full assessment execution to avoid mid-request race effects.
21. Preserve current strict error handling behavior (`503` when configured/selected model unavailable, `502` for agent execution failure).
22. Dependencies: depends on Phases B and C.

23. Phase E - Frontend LLM Selection UX
24. Add model selector UI in the intake experience to:
25. show current active model,
26. list available models,
27. allow switching active model.
28. Wire UI to `GET /models/available`, `GET /models/active`, and `POST /models/active`.
29. Show clear success/error feedback on selection changes; keep current intake submission UX untouched.
30. Dependencies: depends on Phase C.

31. Phase F - Configuration and Environment Consistency
32. Keep `RECEPTIONIST_MODEL` as startup fallback/default only (not authoritative once user selects from UI).
33. Ensure docker-compose and env docs reflect fallback semantics and reference examples (including `llama3.1:8b`).
34. Dependencies: parallel with Phases C-E.

35. Phase G - Verification and Hardening
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
1. Start stack, call `GET /models/available`, verify installed model list includes `llama3.1:8b` and others from Ollama.
2. Call `GET /models/active`, verify source and status fields are accurate.
3. Call `POST /models/active` with valid model, then submit `POST /requests`; verify 200 and backend logs show LLM call on selected model.
4. Call `POST /models/active` with invalid model; verify rejection and unchanged active model.
5. Restart backend container; verify `GET /models/active` still returns previously selected model (global persistence).
6. Submit parallel requests while switching model; verify no race-induced crashes and deterministic per-request model usage.

**Decisions**
- Model selection is global and persisted (applies to all users/sessions).
- Frontend manages model selection through backend APIs, not by editing static env files.
- Existing `/requests` contract remains stable; model management is additive.
- Strict error behavior is preserved; no deterministic fallback bypass for model/runtime failures.

**Further Considerations**
1. Access control for model switching: Option A expose to all authenticated users; Option B restrict to admin/operator roles (recommended for production).
2. Auditability: persist `changed_by` and `changed_at` for model switch events to support traceability.
3. UX safety: disable model switch while backend dependency check is unhealthy to prevent noisy failures.

