# tests/test_real_world_case.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI

def test_real_world_claim_verification():
    api_key = os.getenv("GOOGLE_API_KEY")
    assert api_key, "GOOGLE_API_KEY not set!"

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

    claim = "The Eiffel Tower is in Paris, France."
    evidence = [
        "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
        "The landmark is one of the most visited monuments in Paris."
    ]

    prompt = f"""
    You are a fact verifier. 
    Claim: {claim}
    Evidence: {evidence}

    Decide if the claim is:
    - SUPPORTED (clearly true from evidence)
    - REFUTED (clearly false from evidence)
    - INSUFFICIENT (not enough evidence)

    Only output one of: SUPPORTED / REFUTED / INSUFFICIENT.
    """

    resp = llm.invoke(prompt)
    result = resp.content.strip()

    print("Verifier output:", result)
    assert result in ["SUPPORTED", "REFUTED", "INSUFFICIENT"]
    assert result == "SUPPORTED"
