# verifier_agent/runner.py
from shared.schemas import AgentState
from .nodes import verifier_node, refinement_node
import uuid, time

def run_once(initial_query: str, evidence_list: list):
    state: AgentState = {
        "task_id": str(uuid.uuid4()),
        "initial_query": initial_query,
        "evidence": evidence_list,
        "analysis_results": [],
        "next_query": "",
        "iterations": 0,
        "final_conclusion": ""
    }

    # run verifier node
    out = verifier_node(state)
    # apply operator.add semantics
    state["analysis_results"].extend(out.get("analysis_results", []))

    # run refinement node
    out2 = refinement_node(state)
    state["next_query"] = out2.get("next_query", "")

    return state

if __name__ == "__main__":
    # quick smoke test with one dummy evidence
    ev = [{
      "evidence_id": "e1",
      "source_type": "web_page",
      "url": "https://example.com/news/1",
      "content": "Official spokesperson announced that X happened today.",
      "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
      "author": "Reporter"
    }]
    s = run_once("Did public figure X resign?", ev)
    print("RESULTS:", s["analysis_results"])
    print("NEXT_QUERY:", s["next_query"])
