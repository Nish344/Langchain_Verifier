# tests/test_enhanced_verifier.py

import pytest
import json
import os
from autoverifier.verifier import ClaimVerifier, VerificationResult
from autoverifier.state import EvidenceItem


class TestVerificationResult:
    """Test the VerificationResult model validation"""

    def test_valid_result_creation(self):
        """Test creating valid VerificationResult"""
        result = VerificationResult(
            label="SUPPORTED",
            confidence=0.85,
            explanation="The evidence clearly supports the claim.",
        )
        assert result.label == "SUPPORTED"
        assert result.confidence == 0.85
        assert result.explanation == "The evidence clearly supports the claim."

    def test_invalid_label_raises_error(self):
        """Test that invalid labels raise ValidationError"""
        with pytest.raises(ValueError, match="Label must be one of"):
            VerificationResult(
                label="INVALID_LABEL", confidence=0.5, explanation="Test explanation"
            )

    def test_invalid_confidence_raises_error(self):
        """Test that invalid confidence scores raise ValidationError"""
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            VerificationResult(
                label="SUPPORTED", confidence=1.5, explanation="Test explanation"
            )

        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            VerificationResult(
                label="SUPPORTED", confidence=-0.1, explanation="Test explanation"
            )

    def test_boundary_confidence_values(self):
        """Test boundary confidence values (0.0 and 1.0)"""
        result_min = VerificationResult(
            label="NOT_ENOUGH_EVIDENCE", confidence=0.0, explanation="No confidence"
        )
        assert result_min.confidence == 0.0

        result_max = VerificationResult(
            label="SUPPORTED", confidence=1.0, explanation="Maximum confidence"
        )
        assert result_max.confidence == 1.0


class TestClaimVerifier:
    """Test the ClaimVerifier class"""

    @pytest.fixture
    def verifier(self):
        """Create a verifier instance for testing"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not found in environment")
        return ClaimVerifier(google_api_key=api_key)

    @pytest.fixture
    def sample_evidence(self):
        """Sample evidence for testing"""
        return [
            EvidenceItem(
                source="Wikipedia",
                content="The Eiffel Tower is a wrought-iron lattice tower located in Paris, France.",
            ),
            EvidenceItem(
                source="Britannica",
                content="Eiffel Tower, structure in Paris that serves as the city's most iconic landmark.",
            ),
        ]

    def test_format_evidence(self, verifier):
        """Test evidence formatting"""
        evidence = [
            EvidenceItem(source="Test Source", content="Test content"),
            EvidenceItem(source="Another Source", content="More content"),
        ]
        formatted = verifier._format_evidence(evidence)

        assert "Evidence 1:" in formatted
        assert "Evidence 2:" in formatted
        assert "Test Source" in formatted
        assert "Test content" in formatted

    def test_format_empty_evidence(self, verifier):
        """Test formatting empty evidence list"""
        formatted = verifier._format_evidence([])
        assert formatted == "No evidence provided."

    def test_extract_json_from_valid_response(self, verifier):
        """Test JSON extraction from valid response"""
        response = '{"label": "SUPPORTED", "confidence": 0.9, "explanation": "Test"}'
        result = verifier._extract_json_from_response(response)

        assert result["label"] == "SUPPORTED"
        assert result["confidence"] == 0.9
        assert result["explanation"] == "Test"

    def test_extract_json_with_extra_text(self, verifier):
        """Test JSON extraction when response has extra text"""
        response = 'Here is my analysis: {"label": "REFUTED", "confidence": 0.8, "explanation": "False"} Done.'
        result = verifier._extract_json_from_response(response)

        assert result["label"] == "REFUTED"
        assert result["confidence"] == 0.8

    def test_extract_json_from_invalid_response(self, verifier):
        """Test fallback when JSON extraction fails"""
        response = "This is not valid JSON at all"
        result = verifier._extract_json_from_response(response)

        assert result["label"] == "NOT_ENOUGH_EVIDENCE"
        assert result["confidence"] == 0.1
        assert "Failed to parse LLM response" in result["explanation"]

    def test_validate_and_fix_invalid_label(self, verifier):
        """Test fixing invalid labels"""
        result_dict = {
            "label": "INVALID_LABEL",
            "confidence": 0.5,
            "explanation": "Test",
        }
        result = verifier._validate_and_fix_result(result_dict)

        assert result.label == "NOT_ENOUGH_EVIDENCE"
        assert result.confidence == 0.5

    def test_validate_and_fix_invalid_confidence(self, verifier):
        """Test fixing invalid confidence scores"""
        result_dict = {
            "label": "SUPPORTED",
            "confidence": 1.5,  # Invalid
            "explanation": "Test",
        }
        result = verifier._validate_and_fix_result(result_dict)

        assert result.label == "SUPPORTED"
        assert result.confidence == 0.5  # Fixed to default

    def test_validate_and_fix_missing_explanation(self, verifier):
        """Test fixing missing explanation"""
        result_dict = {
            "label": "SUPPORTED",
            "confidence": 0.8,
            "explanation": "",  # Empty
        }
        result = verifier._validate_and_fix_result(result_dict)

        assert result.explanation == "Unable to generate proper explanation."


class TestIntegrationWithRealAPI:
    """Integration tests with real Google API calls"""

    @pytest.fixture
    def verifier(self):
        """Create a verifier instance for testing"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not found in environment")
        return ClaimVerifier(google_api_key=api_key)

    def test_eiffel_tower_claim_supported(self, verifier):
        """Test a claim that should be SUPPORTED"""
        claim = "The Eiffel Tower is located in Paris, France"
        evidence = [
            EvidenceItem(
                source="Wikipedia",
                content="The Eiffel Tower is a wrought-iron lattice tower located in Paris, France.",
            ),
            EvidenceItem(
                source="Britannica",
                content="Eiffel Tower, structure in Paris that serves as the city's most iconic landmark.",
            ),
        ]

        result = verifier.verify_claim(claim, evidence)

        # Validate structure
        assert isinstance(result, VerificationResult)
        assert result.label in ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
        assert 0 <= result.confidence <= 1
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

        # This claim should likely be SUPPORTED
        print(f"Result: {result.label} (confidence: {result.confidence})")
        print(f"Explanation: {result.explanation}")

    def test_false_claim_refuted(self, verifier):
        """Test a claim that should be REFUTED"""
        claim = "The Eiffel Tower is located in London, England"
        evidence = [
            EvidenceItem(
                source="Wikipedia",
                content="The Eiffel Tower is a wrought-iron lattice tower located in Paris, France.",
            ),
            EvidenceItem(
                source="Tourism Site",
                content="Visit the Eiffel Tower in the heart of Paris, the capital of France.",
            ),
        ]

        result = verifier.verify_claim(claim, evidence)

        # Validate structure
        assert isinstance(result, VerificationResult)
        assert result.label in ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
        assert 0 <= result.confidence <= 1
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

        print(f"Result: {result.label} (confidence: {result.confidence})")
        print(f"Explanation: {result.explanation}")

    def test_insufficient_evidence_claim(self, verifier):
        """Test a claim with insufficient evidence"""
        claim = "The Eiffel Tower was painted blue in 2023"
        evidence = [
            EvidenceItem(
                source="Random Blog", content="The Eiffel Tower is a famous monument."
            )
        ]

        result = verifier.verify_claim(claim, evidence)

        # Validate structure
        assert isinstance(result, VerificationResult)
        assert result.label in ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
        assert 0 <= result.confidence <= 1
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

        print(f"Result: {result.label} (confidence: {result.confidence})")
        print(f"Explanation: {result.explanation}")

    def test_no_evidence_claim(self, verifier):
        """Test a claim with no evidence"""
        claim = "Artificial intelligence will replace all jobs by 2030"
        evidence = []

        result = verifier.verify_claim(claim, evidence)

        # Validate structure
        assert isinstance(result, VerificationResult)
        assert result.label == "NOT_ENOUGH_EVIDENCE"  # Should be this with no evidence
        assert 0 <= result.confidence <= 1
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

        print(f"Result: {result.label} (confidence: {result.confidence})")
        print(f"Explanation: {result.explanation}")

    def test_batch_verification(self, verifier):
        """Test batch verification of multiple claims"""
        claims_and_evidence = [
            (
                "The Eiffel Tower is in Paris",
                [
                    EvidenceItem(
                        source="Wikipedia",
                        content="The Eiffel Tower is located in Paris, France.",
                    )
                ],
            ),
            (
                "The Eiffel Tower is in London",
                [
                    EvidenceItem(
                        source="Wikipedia",
                        content="The Eiffel Tower is located in Paris, France.",
                    )
                ],
            ),
        ]

        results = verifier.verify_claim_batch(claims_and_evidence)

        assert len(results) == 2
        for result in results:
            assert isinstance(result, VerificationResult)
            assert result.label in ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
            assert 0 <= result.confidence <= 1
            assert isinstance(result.explanation, str)


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_verifier_with_invalid_api_key(self):
        """Test verifier behavior with invalid API key"""
        verifier = ClaimVerifier(google_api_key="invalid_key")

        claim = "Test claim"
        evidence = [EvidenceItem(source="Test", content="Test content")]

        # Should handle the error gracefully and return fallback result
        result = verifier.verify_claim(claim, evidence)

        assert isinstance(result, VerificationResult)
        assert result.label == "NOT_ENOUGH_EVIDENCE"
        assert result.confidence == 0.1
        assert "Error during verification" in result.explanation


if __name__ == "__main__":
    # Run specific tests for development
    pytest.main(["-v", __file__])
