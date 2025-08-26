# demo_verifier.py
"""
Fixed demo script to test the enhanced verifier module.
Make sure to set your GOOGLE_API_KEY environment variable before running.
"""

import os
import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from autoverifier.verifier import ClaimVerifier, VerificationResult
    from autoverifier.state import EvidenceItem
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory.")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    sys.exit(1)


def demo_verifier():
    """Demonstrate the enhanced verifier functionality"""

    # Check if API key is available
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return

    print("🚀 Initializing Enhanced Claim Verifier...")

    try:
        verifier = ClaimVerifier(google_api_key=api_key)
        print("✅ Verifier initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize verifier: {e}")
        return

    # Test cases with corrected EvidenceItem usage
    test_cases = [
        {
            "name": "SUPPORTED Case - Eiffel Tower Location",
            "claim": "The Eiffel Tower is located in Paris, France",
            "evidence": [
                EvidenceItem(
                    source="Wikipedia",
                    content="The Eiffel Tower is a wrought-iron lattice tower located in Paris, France.",
                ),
                EvidenceItem(
                    source="Britannica Encyclopedia",
                    content="Eiffel Tower, structure in Paris that serves as the city's most iconic landmark.",
                ),
            ],
        },
        {
            "name": "REFUTED Case - Wrong Location",
            "claim": "The Eiffel Tower is located in London, England",
            "evidence": [
                EvidenceItem(
                    source="Wikipedia",
                    content="The Eiffel Tower is a wrought-iron lattice tower located in Paris, France.",
                ),
                EvidenceItem(
                    source="Tourism Guide",
                    content="Visit the Eiffel Tower in the heart of Paris, the capital of France.",
                ),
            ],
        },
        {
            "name": "NOT_ENOUGH_EVIDENCE Case - Specific Detail",
            "claim": "The Eiffel Tower was painted bright purple in 2024",
            "evidence": [
                EvidenceItem(
                    source="General Travel Blog",
                    content="The Eiffel Tower is a beautiful monument that attracts millions of visitors.",
                )
            ],
        },
        {
            "name": "NO EVIDENCE Case",
            "claim": "Aliens visited Earth in 2023",
            "evidence": [],
        },
    ]

    print("\n" + "=" * 60)
    print("🔍 TESTING ENHANCED VERIFIER")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Claim: {test_case['claim']}")
        print(f"Evidence Count: {len(test_case['evidence'])}")

        if test_case["evidence"]:
            for j, evidence in enumerate(test_case["evidence"], 1):
                print(f"  Evidence {j}: {evidence.source} - {evidence.content[:60]}...")

        try:
            # Perform verification
            print("\n🔄 Verifying claim...")
            result = verifier.verify_claim(test_case["claim"], test_case["evidence"])

            # Display results
            print(f"\n✅ VERIFICATION RESULT:")
            print(f"   Label: {result.label}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Explanation: {result.explanation}")

            # Validate structure (as per requirements)
            try:
                assert result.label in [
                    "SUPPORTED",
                    "REFUTED",
                    "NOT_ENOUGH_EVIDENCE",
                ], f"Invalid label: {result.label}"
                assert 0 <= result.confidence <= 1, (
                    f"Invalid confidence: {result.confidence}"
                )
                assert isinstance(result.explanation, str), (
                    f"Explanation must be string: {type(result.explanation)}"
                )
                assert len(result.explanation.strip()) > 0, (
                    "Explanation cannot be empty"
                )

                print(f"   ✓ Structure validation: PASSED")

                # Show JSON output
                result_json = {
                    "label": result.label,
                    "confidence": result.confidence,
                    "explanation": result.explanation,
                }
                print(f"\n📄 JSON Output:")
                print(json.dumps(result_json, indent=2))

            except AssertionError as validation_error:
                print(f"   ❌ Structure validation: FAILED - {validation_error}")

        except Exception as e:
            print(f"❌ Error in test case: {e}")
            import traceback

            traceback.print_exc()

        print("\n" + "-" * 50)

    # Test batch verification
    print(f"\n🔄 TESTING BATCH VERIFICATION")
    print("-" * 50)

    try:
        batch_data = [
            (test_cases[0]["claim"], test_cases[0]["evidence"]),
            (test_cases[1]["claim"], test_cases[1]["evidence"]),
        ]

        print("Running batch verification...")
        batch_results = verifier.verify_claim_batch(batch_data)
        print(f"✅ Batch verification completed!")
        print(f"   Results count: {len(batch_results)}")

        for i, result in enumerate(batch_results, 1):
            print(
                f"   Result {i}: {result.label} (confidence: {result.confidence:.2f})"
            )

    except Exception as e:
        print(f"❌ Batch verification error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("\n📊 SUMMARY OF ENHANCEMENTS:")
    print("✅ Structured JSON Output (label, confidence, explanation)")
    print("✅ Confidence Scoring (0.0 to 1.0)")
    print("✅ Multi-label Validation (SUPPORTED/REFUTED/NOT_ENOUGH_EVIDENCE)")
    print("✅ Robust Error Handling")
    print("✅ Pydantic Model Validation")
    print("✅ Batch Processing Support")
    print("✅ Comprehensive Test Suite")


def check_environment():
    """Check if the environment is set up correctly"""
    print("🔧 ENVIRONMENT CHECK")
    print("-" * 30)

    # Check Python path
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")

    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✅ GOOGLE_API_KEY found (length: {len(api_key)})")
    else:
        print("❌ GOOGLE_API_KEY not found")

    # Check imports
    try:
        from autoverifier.verifier import ClaimVerifier

        print("✅ ClaimVerifier import successful")
    except ImportError as e:
        print(f"❌ ClaimVerifier import failed: {e}")

    try:
        from autoverifier.state import EvidenceItem

        print("✅ EvidenceItem import successful")

        # Test EvidenceItem creation
        test_evidence = EvidenceItem(source="Test", content="Test content")
        print(f"✅ EvidenceItem creation successful: {test_evidence}")

    except ImportError as e:
        print(f"❌ EvidenceItem import failed: {e}")
    except Exception as e:
        print(f"❌ EvidenceItem creation failed: {e}")

    print("-" * 30)


if __name__ == "__main__":
    print("🧪 ENHANCED VERIFIER DEMO")
    print("=" * 60)

    # Check environment first
    check_environment()
    print()

    # Run the main demo
    demo_verifier()
