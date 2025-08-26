# verifier_agent/nodes.py
from shared.schemas import AgentState, VerificationResult, EvidenceItem
from typing import Dict, List
from .tools import claim_analysis_tool, source_credibility_tool
from .scoring import compute_trust_score
import time

def verifier_node(state: AgentState) -> Dict[str, List[VerificationResult]]:
    """
    Input: AgentState
    Output: {"analysis_results": [VerificationResult, ...]}

    - Skip evidence already analyzed (match evidence_id against existing analysis_results).
    - Use tools to analyze and compute trust.
    """
    existing = {r["evidence_id"] for r in state.get("analysis_results", []) or []}
    out_results: List[VerificationResult] = []

    for ev in state.get("evidence", []) or []:
        if ev["evidence_id"] in existing:
            continue

        # call tools
        cred = source_credibility_tool(ev["url"])
        claim = claim_analysis_tool(ev["content"])

        trust = compute_trust_score(
            cred=float(cred.get("score", 0.5)),
            stance=str(claim.get("stance", "speculation")),
            fallacies=list(claim.get("fallacies", [])),
            content_len=len(ev.get("content", "") or "")
        )

        reasoning = (
            f"domain={cred.get('domain')}; cred={cred.get('score')}. "
            f"stance={claim.get('stance')}; fallacies={claim.get('fallacies') or 'none'}. "
            f"len={len(ev.get('content',''))}. computed_trust={trust}"
        )

        res: VerificationResult = {
            "evidence_id": ev["evidence_id"],
            "trust_score": trust,
            "reasoning": reasoning
        }
        out_results.append(res)

    return {"analysis_results": out_results}


def refinement_node(state: AgentState) -> Dict[str, str]:
    """
    Input: AgentState (with analysis_results)
    Output: {"next_query": "<string>"} or {"next_query": ""} when done.

    Simple logic:
      - sufficient if >=2 items with trust>=0.75 and no major conflicts
      - else ask Gemini to produce a single precise next query (<=140 chars)
    """
    results = state.get("analysis_results", []) or []

    if not results:
        # no analysis yet -> recommend querying high-quality sources about the initial query
        return {"next_query": f'{state.get("initial_query","")} site:reuters.com OR site:apnews.com "official statement"'}

    high = [r for r in results if r["trust_score"] >= 0.75]
    low = [r for r in results if r["trust_score"] < 0.4]

    if len(high) >= 2 and not (high and low):
        return {"next_query": ""}

    # else try to craft a concise next query using Gemini; fallback to heuristic
    try:
        from .tools import _gemini_generate  # internal helper
        table = "; ".join(f"{r['evidence_id']}={r['trust_score']}" for r in results[:8])
        prompt = (
            f"Initial query: {state.get('initial_query')}\n"
            f"Trust summary: {table}\n"
            "Return a single precise search query (<=140 chars) that would find decisive primary sources or reputable fact-checks."
        )
        q = _gemini_generate(prompt).strip().splitlines()[0][:140]
        if q:
            return {"next_query": q}
    except Exception:
        pass

    # fallback
    fallback = f'{state.get("initial_query","")} site:reuters.com OR site:apnews.com OR site:bbc.com "official statement"'
    return {"next_query": fallback[:140]}
