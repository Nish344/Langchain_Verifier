# autoverifier/state.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class EvidenceItem(BaseModel):
    """Represents a piece of evidence for claim verification"""

    source: str = Field(
        description="Source of the evidence (e.g., 'Wikipedia', 'BBC News')"
    )
    content: str = Field(description="The actual evidence content/text")
    url: Optional[str] = Field(
        default=None, description="URL of the source (if available)"
    )
    relevance_score: Optional[float] = Field(
        default=None, description="Relevance score (0-1)"
    )

    class Config:
        """Pydantic configuration"""

        json_encoders = {
            # Add custom encoders if needed
        }

    def __str__(self) -> str:
        return f"EvidenceItem(source='{self.source}', content='{self.content[:50]}...')"

    def __repr__(self) -> str:
        return self.__str__()


class VerificationRequest(BaseModel):
    """Represents a claim verification request"""

    claim: str = Field(description="The claim to be verified")
    evidence: List[EvidenceItem] = Field(
        default_factory=list, description="List of evidence items"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context"
    )


class AgentState(TypedDict):
    """State for the verification agent workflow"""

    # Core verification data
    claim: str
    evidence: List[EvidenceItem]
    verification_result: Optional[Dict[str, Any]]

    # Workflow tracking
    step: str  # Current step in the workflow
    iterations: int
    max_iterations: int

    # Search and retrieval
    search_queries: List[str]
    search_results: List[Dict[str, Any]]

    # Configuration
    confidence_threshold: float
    require_multiple_sources: bool

    # Error handling
    errors: List[str]
    warnings: List[str]


# Utility functions for state management
def create_initial_state(claim: str, max_iterations: int = 3) -> AgentState:
    """Create initial state for verification workflow"""
    return AgentState(
        claim=claim,
        evidence=[],
        verification_result=None,
        step="initialize",
        iterations=0,
        max_iterations=max_iterations,
        search_queries=[],
        search_results=[],
        confidence_threshold=0.7,
        require_multiple_sources=True,
        errors=[],
        warnings=[],
    )


def add_evidence_to_state(state: AgentState, evidence_item: EvidenceItem) -> AgentState:
    """Add evidence item to state"""
    state["evidence"].append(evidence_item)
    return state


def update_state_step(state: AgentState, step: str) -> AgentState:
    """Update the current step in state"""
    state["step"] = step
    state["iterations"] += 1
    return state


# Constants for verification labels
VERIFICATION_LABELS = {
    "SUPPORTED": "SUPPORTED",
    "REFUTED": "REFUTED",
    "NOT_ENOUGH_EVIDENCE": "NOT_ENOUGH_EVIDENCE",
}

# Example evidence items for testing
SAMPLE_EVIDENCE = [
    EvidenceItem(
        source="Wikipedia",
        content="The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
        url="https://en.wikipedia.org/wiki/Eiffel_Tower",
    ),
    EvidenceItem(
        source="Britannica",
        content="Eiffel Tower, structure in Paris that serves as the city's most recognizable landmark.",
        url="https://www.britannica.com/topic/Eiffel-Tower-Paris-France",
    ),
]
