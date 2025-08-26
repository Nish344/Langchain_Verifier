# tests/test_verifier.py
from autoverifier.state import AgentState, EvidenceItem

def test_dummy_verifier():
    ev = EvidenceItem(id="1", content="sample evidence")
    state = AgentState(query="Is this working?", evidence=[ev])

    assert state.query == "Is this working?"
    assert state.evidence[0].content == "sample evidence"
