from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.analyst import AnalystBrd, draft_brd_with_analyst


class AnalystState(TypedDict):
    raw_text: str
    business_context: str | None
    request_type: str | None
    extracted_scope: str | None
    clarification_answers: dict[str, str] | None
    brd: AnalystBrd | None


def _draft_node(state: AnalystState) -> AnalystState:
    brd = draft_brd_with_analyst(
        raw_text=state["raw_text"],
        business_context=state.get("business_context"),
        request_type=state.get("request_type"),
        extracted_scope=state.get("extracted_scope"),
        clarification_answers=state.get("clarification_answers"),
    )
    state["brd"] = brd
    return state


def build_analyst_graph():
    graph = StateGraph(AnalystState)
    graph.add_node("draft", _draft_node)
    graph.add_edge(START, "draft")
    graph.add_edge("draft", END)
    return graph.compile()


_ANALYST_GRAPH = build_analyst_graph()


def run_analyst_flow(
    raw_text: str,
    business_context: str | None,
    request_type: str | None,
    extracted_scope: str | None,
    clarification_answers: dict[str, str] | None,
) -> AnalystBrd:
    initial_state: AnalystState = {
        "raw_text": raw_text,
        "business_context": business_context,
        "request_type": request_type,
        "extracted_scope": extracted_scope,
        "clarification_answers": clarification_answers,
        "brd": None,
    }
    result = _ANALYST_GRAPH.invoke(initial_state)
    brd = result.get("brd")
    if brd is None:
        raise RuntimeError("Analyst workflow returned no BRD")
    return brd
