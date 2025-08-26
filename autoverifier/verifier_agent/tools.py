# verifier_agent/tools.py
import re
import json
from typing import Dict, List
from langchain.tools import tool  # `@tool` decorator
import os

# Optional: Gemini client helper
def _gemini_generate(prompt: str) -> str:
    """Try to call Google Gemini; if not available, raise or return empty string."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            return ""
        genai.configure(api_key=api_key)
        model = genai.models.get("gemini-1.5-flash")
        # use model.generate or equivalent depending on SDK; we'll call a generic endpoint
        resp = genai.generate_text(model="gemini-1.5-flash", prompt=prompt)
        return getattr(resp, "text", "") or resp.get("candidates", [{}])[0].get("content", "")
    except Exception:
        return ""


@tool
def source_credibility_tool(url_or_source: str) -> Dict:
    """
    Estimate credibility for a given URL or domain.

    Args:
        url_or_source (str): URL or domain (e.g., 'https://bbc.com/news/...' or 'randomblog.net').

    Returns:
        dict:
            {
              "domain": str,
              "score": float,   # in [0.0, 1.0]
              "rationale": str
            }

    Behavior:
      - Uses a small static domain score map for well-known outlets.
      - If domain unseen, applies simple heuristics (TLD, contains gov/edu).
      - Never raises an exception; on failure returns a conservative score 0.5.
    """
    try:
        domain = re.sub(r"^https?://", "", url_or_source).split("/")[0].lower()
        known = {
            "bbc.com": 0.90, "reuters.com": 0.92, "apnews.com": 0.90,
            "nytimes.com": 0.88, "theguardian.com": 0.85, "aljazeera.com": 0.82,
            "wikipedia.org": 0.75, "reddit.com": 0.55, "x.com": 0.45, "twitter.com": 0.45
        }
        if domain in known:
            return {"domain": domain, "score": known[domain], "rationale": "Known outlet (static map)."}
        score = 0.5
        if domain.endswith((".gov", ".edu")): score += 0.25
        if domain.endswith((".info", ".xyz", ".blog")): score -= 0.1
        score = max(0.0, min(1.0, round(score, 2)))
        return {"domain": domain, "score": score, "rationale": "Heuristic fallback."}
    except Exception as e:
        return {"domain": url_or_source, "score": 0.5, "rationale": f"Error: {e}"}


@tool
def claim_analysis_tool(text: str) -> Dict:
    """
    Extract core claim + meta-signals from the provided text.

    Args:
        text (str): Raw text of evidence.

    Returns:
        dict:
            {
              "core_claim": str,
              "stance": "assertion"|"speculation"|"opinion"|"question",
              "sentiment": "pos"|"neg"|"neutral",
              "fallacies": List[str],
              "supporting_facts": List[str]
            }

    Behavior:
      - Attempts to call Gemini to get a structured output.
      - If Gemini is unavailable or response can't be parsed, uses simple heuristics.
      - Always returns a dict (never raises).
    """
    text = (text or "").strip()
    if len(text) < 40:
        return {
            "core_claim": text,
            "stance": "speculation",
            "sentiment": "neutral",
            "fallacies": [],
            "supporting_facts": []
        }

    # try LLM first
    prompt = (
        "Extract a JSON with keys: core_claim, stance (one of assertion/speculation/opinion/question), "
        "sentiment (pos/neg/neutral), fallacies (list), supporting_facts (list). Respond only JSON.\n\nTEXT:\n"
        + text
    )
    raw = _gemini_generate(prompt)
    if raw:
        # try to locate and parse a JSON object in the LLM output
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
                # normalize keys if needed
                return {
                    "core_claim": parsed.get("core_claim", "")[:200],
                    "stance": parsed.get("stance", "speculation"),
                    "sentiment": parsed.get("sentiment", "neutral"),
                    "fallacies": parsed.get("fallacies", []),
                    "supporting_facts": parsed.get("supporting_facts", [])
                }
            except Exception:
                pass

    # fallback heuristics
    stance = "assertion" if any(w in text.lower() for w in ["confirmed", "announced", "stated", "said"]) else "speculation"
    sentiment = "neg" if any(w in text.lower() for w in ["not", "no", "never", "deny", "denied"]) else "neutral"
    return {"core_claim": text[:250], "stance": stance, "sentiment": sentiment, "fallacies": [], "supporting_facts": []}
