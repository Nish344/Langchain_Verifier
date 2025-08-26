# autoverifier/state.py
from dataclasses import dataclass
from typing import List

@dataclass
class EvidenceItem:
    id: str
    content: str

@dataclass
class AgentState:
    query: str
    evidence: List[EvidenceItem]
