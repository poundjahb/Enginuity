from types import SimpleNamespace

import pytest

from app.agents.analyst import AnalystAgentError, AnalystBrd
from app.models import RequestRecord


async def _healthy_check() -> tuple[bool, None]:
    return True, None


def _assessment_complete() -> SimpleNamespace:
    return SimpleNamespace(
        request_type="feature",
        extracted_scope="Mobile onboarding flow",
        confidence_score=0.9,
        clarification_questions=[],
        rationale_summary="Sufficient context for drafting",
    )


def _sample_brd() -> AnalystBrd:
    return AnalystBrd(
        business_objective="Reduce onboarding abandonment by improving first session guidance.",
        problem_statement="Users drop off before completing first task in onboarding.",
        proposed_scope="Introduce guided checklist and progress indicators.",
        acceptance_criteria=[
            "Users can see a 3-step onboarding checklist.",
            "Checklist progress persists between sessions.",
            "Completion events are tracked per step.",
        ],
        assumptions=["Existing analytics SDK remains available."],
        out_of_scope=["Changes to authentication provider."],
        success_metrics=["Onboarding completion rate improves by 15% in 30 days."],
    )


def _insert_request(db_session, request_id: str, status: str = "assessment_complete") -> None:
    record = RequestRecord(
        request_id=request_id,
        channel="web",
        user_identity="qa.user",
        business_context="growth",
        raw_text="Need a better onboarding flow",
        priority_hint="high",
        status=status,
        request_type="feature",
        extracted_scope="onboarding",
        confidence_score=0.9,
        clarification_questions="[]",
        clarification_answers="{}",
        workflow_events='["Request submitted", "Assessment completed at 90% confidence"]',
    )
    db_session.add(record)
    db_session.commit()


def test_analyst_happy_path_with_review_and_regenerate(client, db_session, monkeypatch):
    from app.routes import requests as requests_routes

    monkeypatch.setattr(requests_routes, "check_ollama_health", _healthy_check)
    monkeypatch.setattr(requests_routes, "check_receptionist_model_available", _healthy_check)
    monkeypatch.setattr(requests_routes, "check_analyst_model_available", _healthy_check)
    monkeypatch.setattr(requests_routes, "run_receptionist_flow", lambda *args, **kwargs: _assessment_complete())
    monkeypatch.setattr(requests_routes, "run_analyst_flow", lambda *args, **kwargs: _sample_brd())

    create_res = client.post(
        "/requests",
        json={
            "channel": "web",
            "user_identity": "qa.user",
            "business_context": "growth",
            "raw_text": "Improve onboarding completion for first-time users",
            "priority_hint": "high",
        },
    )
    assert create_res.status_code == 200
    request_id = create_res.json()["request_id"]
    assert create_res.json()["status"] == "assessment_complete"

    generate_res = client.post(f"/requests/{request_id}/brd/generate")
    assert generate_res.status_code == 200
    payload = generate_res.json()
    assert payload["brd_status"] == "pending_approval"
    assert "## 1. Business Objective" in payload["brd_draft"]
    assert "## 7. Success Metrics" in payload["brd_draft"]

    reject_res = client.post(
        f"/requests/{request_id}/brd/review",
        json={"decision": "reject", "comment": "Need tighter KPIs"},
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "brd_rejected"
    assert reject_res.json()["brd_status"] == "rejected"

    regenerate_res = client.post(f"/requests/{request_id}/brd/generate")
    assert regenerate_res.status_code == 200
    assert regenerate_res.json()["brd_status"] == "pending_approval"


def test_generate_brd_rejects_invalid_state(client, db_session, monkeypatch):
    from app.routes import requests as requests_routes

    monkeypatch.setattr(requests_routes, "check_ollama_health", _healthy_check)
    monkeypatch.setattr(requests_routes, "check_analyst_model_available", _healthy_check)

    _insert_request(db_session, request_id="req-invalid-state", status="received")
    response = client.post("/requests/req-invalid-state/brd/generate")

    assert response.status_code == 400
    assert response.json()["detail"] == "BRD generation requires completed assessment"


def test_generate_brd_fails_when_model_missing(client, db_session, monkeypatch):
    from app.routes import requests as requests_routes

    async def _missing_model() -> tuple[bool, str]:
        return False, "Configured ANALYST_MODEL 'foo' is not available in Ollama"

    monkeypatch.setattr(requests_routes, "check_ollama_health", _healthy_check)
    monkeypatch.setattr(requests_routes, "check_analyst_model_available", _missing_model)

    _insert_request(db_session, request_id="req-model-missing")
    response = client.post("/requests/req-model-missing/brd/generate")

    assert response.status_code == 503
    assert response.json()["detail"]["message"] == "Configured analyst model is unavailable in Ollama."
    assert "ANALYST_MODEL" in response.json()["detail"]["blocked_reason"]


def test_generate_brd_returns_502_on_agent_failure(client, db_session, monkeypatch):
    from app.routes import requests as requests_routes

    def _raise_agent_error(*args, **kwargs):
        raise AnalystAgentError("Analyst response parsing failed: malformed JSON")

    monkeypatch.setattr(requests_routes, "check_ollama_health", _healthy_check)
    monkeypatch.setattr(requests_routes, "check_analyst_model_available", _healthy_check)
    monkeypatch.setattr(requests_routes, "run_analyst_flow", _raise_agent_error)

    _insert_request(db_session, request_id="req-agent-error")
    response = client.post("/requests/req-agent-error/brd/generate")

    assert response.status_code == 502
    assert response.json()["detail"]["message"] == "Analyst agent execution failed."
    assert "response parsing failed" in response.json()["detail"]["blocked_reason"]


def test_generate_brd_returns_404_when_request_missing(client):
    response = client.post("/requests/does-not-exist/brd/generate")
    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"