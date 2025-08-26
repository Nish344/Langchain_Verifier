# Enhanced Claim Verifier Module 🔍

A robust fact-checking pipeline component that verifies claims against provided evidence using Google's Gemini AI.

## 🚀 What's New in the Enhanced Version

✅ **Structured JSON Output** - Returns proper JSON with `label`, `confidence`, and `explanation`  
✅ **Confidence Scoring** - Provides confidence scores between 0.0 and 1.0  
✅ **Multi-label Validation** - Strictly enforces valid labels: `SUPPORTED`, `REFUTED`, `NOT_ENOUGH_EVIDENCE`  
✅ **Robust Error Handling** - Graceful fallbacks for API errors and malformed responses  
✅ **Pydantic Validation** - Type-safe models with automatic validation  
✅ **Batch Processing** - Support for verifying multiple claims at once  
✅ **Comprehensive Tests** - Full test suite covering all scenarios  

## 📁 Project Structure

```
autoverifier/
├── state.py          # Data structures (AgentState, EvidenceItem)
├── verifier.py       # Enhanced verifier logic with structured output
tests/
├── test_verifier.py  # Basic unit tests
├── test_google_api.py# Integration tests  
├── test_enhanced_verifier.py # Comprehensive test suite
demo_verifier.py      # Demo script
requirements.txt      # Dependencies
```

## 🛠️ Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up Google API key:**
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

## 🎯 Usage

### Basic Usage

```python
from autoverifier.verifier import ClaimVerifier, VerificationResult
from autoverifier.state import EvidenceItem
import os

# Initialize verifier
verifier = ClaimVerifier(google_api_key=os.getenv("GOOGLE_API_KEY"))

# Create evidence
evidence = [
    EvidenceItem(
        source="Wikipedia",
        content="The Eiffel Tower is located in Paris, France."
    )
]

# Verify claim
claim = "The Eiffel Tower is in Paris"
result = verifier.verify_claim(claim, evidence)

# Access structured results
print(f"Label: {result.label}")           # SUPPORTED/REFUTED/NOT_ENOUGH_EVIDENCE
print(f"Confidence: {result.confidence}") # 0.0 to 1.0
print(f"Explanation: {result.explanation}") # Detailed reasoning
```

### Batch Processing

```python
# Verify multiple claims at once
claims_and_evidence = [
    ("The Eiffel Tower is in Paris", evidence1),
    ("The Eiffel Tower is in London", evidence2)
]

results = verifier.verify_claim_batch(claims_and_evidence)
for result in results:
    print(f"{result.label} (confidence: {result.confidence:.2f})")
```

### JSON Output

The verifier returns structured JSON that looks like this:

```json
{
  "label": "SUPPORTED",
  "confidence": 0.92,
  "explanation": "The evidence clearly confirms that the Eiffel Tower is located in Paris, France, as stated by multiple reliable sources."
}
```

## 🧪 Testing

### Run All Tests
```bash
# Set Python path and run tests
PYTHONPATH=. pytest -s tests/

# Run specific test file
PYTHONPATH=. pytest -s tests/test_enhanced_verifier.py

# Run with verbose output
PYTHONPATH=. pytest -v tests/
```

### Run Demo Script
```bash
python demo_verifier.py
```

### Test Coverage

The test suite covers:
- ✅ **Structure validation** - JSON format, field types, value ranges
- ✅ **Label enforcement** - Only valid labels accepted
- ✅ **Confidence scoring** - Values between 0.0 and 1.0
- ✅ **Error handling** - API failures, malformed responses
- ✅ **Edge cases** - Empty evidence, invalid inputs
- ✅ **Integration tests** - Real API calls with various scenarios
- ✅ **Batch processing** - Multiple claims verification

## 🔧 Configuration

### Model Parameters

```python
verifier = ClaimVerifier(
    google_api_key="your-api-key",
    model_name="gemini-1.5-flash",  # Default model
    temperature=0.1          # Low for consistent results
)
```

### Custom Validation

The `VerificationResult` model uses Pydantic for validation:

```python
class VerificationResult(BaseModel):
    label: str = Field(description="Must be SUPPORTED, REFUTED, or NOT_ENOUGH_EVIDENCE")
    confidence: float = Field(description="Between 0.0 and 1.0", ge=0.0, le=1.0)
    explanation: str = Field(description="Detailed reasoning")
```

## 📊 Verification Logic

The verifier follows this decision process:

1. **SUPPORTED** - Evidence clearly confirms the claim is true
2. **REFUTED** - Evidence clearly shows the claim is false  
3. **NOT_ENOUGH_EVIDENCE** - Evidence is insufficient, contradictory, or doesn't address the claim

### Confidence Scoring Factors

- **Quality of evidence sources** (Wikipedia > Random blog)
- **Strength of connection** between evidence and claim
- **Consistency across** multiple evidence pieces
- **Completeness of coverage** for the specific claim

## 🚨 Error Handling

The enhanced verifier includes robust error handling:

- **API failures** → Returns `NOT_ENOUGH_EVIDENCE` with low confidence
- **Invalid JSON responses** → Attempts parsing, falls back gracefully
- **Invalid labels** → Automatically corrected to valid values
- **Invalid confidence** → Normalized to valid range (0.0-1.0)
- **Empty explanations** → Provides fallback explanation

## 🔍 Validation Checklist

When testing your implementation, ensure:

```python
# Structure validation
assert result.label in ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
assert 0 <= result.confidence <= 1
assert isinstance(result.explanation, str)
assert len(result.explanation.strip()) > 0

# JSON serialization
result_dict = {
    "label": result.label,
    "confidence": result.confidence, 
    "explanation": result.explanation
}
json.dumps(result_dict)  # Should work without errors
```

## 📈 Performance Notes

- **Response time**: ~2-5 seconds per claim (depends on Google API)
- **Batch processing**: More efficient for multiple claims
- **Rate limits**: Respects Google API rate limits
- **Memory usage**: Minimal - processes claims individually

## 🤝 Contributing

To extend the verifier:

1. **Add new evidence types** in `state.py`
2. **Modify prompts** in `verifier.py` for better accuracy
3. **Add custom validators** to `VerificationResult` model
4. **Extend test cases** in `test_enhanced_verifier.py`

## 📋 API Reference

### ClaimVerifier

```python
ClaimVerifier(google_api_key: str, model_name: str = "gemini-pro")
```

**Methods:**
- `verify_claim(claim: str, evidence: List[EvidenceItem]) -> VerificationResult`
- `verify_claim_batch(claims_and_evidence: List[tuple]) -> List[VerificationResult]`

### VerificationResult

```python
VerificationResult(label: str, confidence: float, explanation: str)
```

**Fields:**
- `label`: One of "SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"
- `confidence`: Float between 0.0 and 1.0
- `explanation`: String with detailed reasoning

### EvidenceItem

```python
EvidenceItem(source: str, content: str)
```

**Fields:**
- `source`: Source of the evidence (e.g., "Wikipedia")
- `content`: Text content of the evidence

## 🎉 Success Metrics

Your enhanced verifier is working correctly if:

✅ All tests pass with `PYTHONPATH=. pytest -s tests/`  
✅ Demo script runs without errors  
✅ JSON output is properly structured  
✅ Confidence scores are meaningful (0.0-1.0)  
✅ Labels are strictly enforced  
✅ Error cases are handled gracefully  

---

**Status: Production Ready** 🚀

The enhanced verifier module now includes all missing features and is ready for integration into your fact-checking pipeline!
