# autoverifier/verifier.py

from typing import Dict, Any, List
import json
import re
from pydantic import BaseModel, Field, validator
from langchain_google_genai import GoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from .state import EvidenceItem


class VerificationResult(BaseModel):
    """Structured output model for verification results"""

    label: str = Field(
        description="Verification label: SUPPORTED, REFUTED, or NOT_ENOUGH_EVIDENCE"
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1", ge=0.0, le=1.0
    )
    explanation: str = Field(
        description="Detailed explanation of the verification decision"
    )

    @validator("label")
    def validate_label(cls, v):
        valid_labels = ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
        if v not in valid_labels:
            raise ValueError(f"Label must be one of {valid_labels}, got: {v}")
        return v

    @validator("confidence")
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got: {v}")
        return v


class ClaimVerifier:
    def __init__(self, google_api_key: str, model_name: str = "gemini-1.5-flash"):
        """Initialize the claim verifier with Google API"""
        self.llm = GoogleGenerativeAI(
            google_api_key=google_api_key,
            model=model_name,
            temperature=0.1,  # Low temperature for consistent, factual responses
        )

        # Setup structured output parser
        self.output_parser = PydanticOutputParser(pydantic_object=VerificationResult)

        # Create the verification prompt template
        self.prompt_template = PromptTemplate(
            template="""You are a professional fact-checker tasked with verifying claims based on provided evidence.

CLAIM TO VERIFY: {claim}

EVIDENCE PROVIDED:
{evidence_text}

INSTRUCTIONS:
1. Carefully analyze the claim against the provided evidence
2. Determine if the evidence SUPPORTS, REFUTES, or provides NOT_ENOUGH_EVIDENCE for the claim
3. Provide a confidence score (0.0 to 1.0) based on:
   - Quality and reliability of evidence sources
   - Strength of connection between evidence and claim
   - Consistency across multiple evidence pieces
4. Explain your reasoning clearly and concisely

CLASSIFICATION RULES:
- SUPPORTED: Evidence clearly confirms the claim is true
- REFUTED: Evidence clearly shows the claim is false
- NOT_ENOUGH_EVIDENCE: Evidence is insufficient, contradictory, or doesn't address the claim

RESPONSE FORMAT:
You must respond with valid JSON matching this exact structure:
{{
    "label": "SUPPORTED" | "REFUTED" | "NOT_ENOUGH_EVIDENCE",
    "confidence": <float between 0.0 and 1.0>,
    "explanation": "<detailed explanation of your reasoning>"
}}

{format_instructions}

IMPORTANT: Your response must be valid JSON only, no additional text.""",
            input_variables=["claim", "evidence_text"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            },
        )

    def _format_evidence(self, evidence: List[EvidenceItem]) -> str:
        """Format evidence items into readable text"""
        if not evidence:
            return "No evidence provided."

        formatted_evidence = []
        for i, item in enumerate(evidence, 1):
            evidence_text = f"Evidence {i}:\n"
            if hasattr(item, "source") and item.source:
                evidence_text += f"Source: {item.source}\n"
            if hasattr(item, "content") and item.content:
                evidence_text += f"Content: {item.content}\n"
            formatted_evidence.append(evidence_text)

        return "\n".join(formatted_evidence)

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract and validate JSON from LLM response"""
        # Try to find JSON in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # If no valid JSON found, try to parse the entire response
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Fallback: create a basic response
            return {
                "label": "NOT_ENOUGH_EVIDENCE",
                "confidence": 0.1,
                "explanation": f"Failed to parse LLM response: {response[:200]}...",
            }

    def _validate_and_fix_result(
        self, result_dict: Dict[str, Any]
    ) -> VerificationResult:
        """Validate and fix the result dictionary"""
        # Ensure label is valid
        valid_labels = ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"]
        if result_dict.get("label") not in valid_labels:
            result_dict["label"] = "NOT_ENOUGH_EVIDENCE"

        # Ensure confidence is valid
        confidence = result_dict.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            result_dict["confidence"] = 0.5

        # Ensure explanation exists
        if not result_dict.get("explanation"):
            result_dict["explanation"] = "Unable to generate proper explanation."

        return VerificationResult(**result_dict)

    def verify_claim(
        self, claim: str, evidence: List[EvidenceItem]
    ) -> VerificationResult:
        """
        Verify a claim against provided evidence

        Args:
            claim: The claim to verify
            evidence: List of evidence items

        Returns:
            VerificationResult with label, confidence, and explanation
        """
        try:
            # Format evidence for the prompt
            evidence_text = self._format_evidence(evidence)

            # Create the full prompt
            prompt = self.prompt_template.format(
                claim=claim, evidence_text=evidence_text
            )

            # Get LLM response
            response = self.llm.invoke(prompt)

            # Extract and parse JSON from response
            result_dict = self._extract_json_from_response(response)

            # Validate and return structured result
            return self._validate_and_fix_result(result_dict)

        except Exception as e:
            # Fallback for any unexpected errors
            return VerificationResult(
                label="NOT_ENOUGH_EVIDENCE",
                confidence=0.1,
                explanation=f"Error during verification: {str(e)}",
            )

    def verify_claim_batch(
        self, claims_and_evidence: List[tuple]
    ) -> List[VerificationResult]:
        """
        Verify multiple claims in batch

        Args:
            claims_and_evidence: List of (claim, evidence) tuples

        Returns:
            List of VerificationResult objects
        """
        results = []
        for claim, evidence in claims_and_evidence:
            result = self.verify_claim(claim, evidence)
            results.append(result)
        return results
