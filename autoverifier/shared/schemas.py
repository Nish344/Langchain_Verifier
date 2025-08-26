# shared/schemas.py
from typing import List, TypedDict, Annotated
import operator

class EvidenceItem(TypedDict):
    evidence_id: str
    source_type: str
    url: str
    content: str
    timestamp: str
    author: str

class VerificationResult(TypedDict):
    evidence_id: str
    trust_score: float
    reasoning: str

class AgentState(TypedDict):
    task_id: str
    initial_query: str
    evidence: Annotated[List[EvidenceItem], operator.add]
    analysis_results: Annotated[List[VerificationResult], operator.add]
    next_query: str
    iterations: int
    final_conclusion: str
