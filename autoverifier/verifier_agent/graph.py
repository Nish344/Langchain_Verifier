# verifier_agent/graph.py
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except Exception:
    LANGGRAPH_AVAILABLE = False

from shared.schemas import AgentState
from .nodes import verifier_node, refinement_node

def build_verifier_graph():
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError("LangGraph not installed or API incompatible in this env.")
    g = StateGraph(AgentState)
    g.add_node("verifier_node", verifier_node)
    g.add_node("refinement_node", refinement_node)
    g.set_entry_point("verifier_node")
    g.add_edge("verifier_node", "refinement_node")
    g.add_edge("refinement_node", END)
    return g.compile()
