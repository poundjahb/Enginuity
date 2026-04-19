from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.receptionist import ReceptionistAssessment, assess_request_with_receptionist


class ReceptionistState(TypedDict):
    raw_text: str
    business_context: str | None
    priority_hint: str | None
    assessment: ReceptionistAssessment | None


def _assess_node(state: ReceptionistState) -> ReceptionistState:
    assessment = assess_request_with_receptionist(
        raw_text=state["raw_text"],
        business_context=state.get("business_context"),
        priority_hint=state.get("priority_hint"),
    )
    state["assessment"] = assessment
    return state


def build_receptionist_graph():
    graph = StateGraph(ReceptionistState)
    graph.add_node("assess", _assess_node)
    graph.add_edge(START, "assess")
    graph.add_edge("assess", END)
    return graph.compile()


_RECEPTIONIST_GRAPH = build_receptionist_graph()


def run_receptionist_flow(raw_text: str, business_context: str | None, priority_hint: str | None) -> ReceptionistAssessment:
    initial_state: ReceptionistState = {
        "raw_text": raw_text,
        "business_context": business_context,
        "priority_hint": priority_hint,
        "assessment": None,
    }
    result = _RECEPTIONIST_GRAPH.invoke(initial_state)
    assessment = result.get("assessment")
    if assessment is None:
        raise RuntimeError("Receptionist workflow returned no assessment")
    return assessment
