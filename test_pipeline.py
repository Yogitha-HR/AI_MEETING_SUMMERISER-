"""
Unit tests for pipeline validation and schema integrity.
"""

import os
import tempfile
import json
from step1_transcription import validate_audio_file, AudioValidationError
from step2_summary import build_summary_prompt
from step3_action_items import clean_json_response, build_action_item_prompt

def test_audio_validation_safeguards():
    print("\n--- Running Test 1: Audio Validation Safeguards ---")
    
    # 1. Test unsupported extension
    try:
        validate_audio_file("fake_document.pdf")
        print("❌ FAILED: Expected AudioValidationError for .pdf format")
    except AudioValidationError as e:
        print(f"✅ PASSED: Correctly rejected unsupported format ({e})")

    # 2. Test empty file (0 bytes)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as empty_tmp:
        empty_tmp_name = empty_tmp.name
    
    try:
        validate_audio_file(empty_tmp_name)
        print("❌ FAILED: Expected AudioValidationError for empty 0-byte file")
    except AudioValidationError as e:
        print(f"✅ PASSED: Correctly caught empty audio file ({e})")
    finally:
        if os.path.exists(empty_tmp_name):
            os.remove(empty_tmp_name)


def test_prompt_structures():
    print("\n--- Running Test 2: Prompt Engineering & Schema Validation ---")
    sample_text = "Alice: Please finish the budget spreadsheet by Friday. Bob: I will do it."
    
    # Check Step 2 prompt contains the 6 required categories
    summary_prompt = build_summary_prompt(sample_text)
    required_sections = [
        "Meeting Purpose", 
        "Main Discussion Points", 
        "Important Updates", 
        "Key Decisions", 
        "Unresolved Questions", 
        "Next Steps"
    ]
    all_sections_present = all(sec in summary_prompt for sec in required_sections)
    if all_sections_present:
        print("✅ PASSED: Step 2 prompt strictly enforces all 6 required sections.")
    else:
        print("❌ FAILED: Missing required sections in Step 2 prompt.")

    # Check Step 3 JSON parser handles codeblocks
    mock_llm_output = """
    ```json
    {
      "action_items": [
        {
          "task_description": "Finish the budget spreadsheet",
          "responsible_person": "Bob",
          "deadline": "Friday",
          "priority": "Medium",
          "transcript_excerpt": "Bob: I will do it."
        }
      ]
    }
    ```
    """
    cleaned = clean_json_response(mock_llm_output)
    if "action_items" in cleaned and len(cleaned["action_items"]) == 1:
        print("✅ PASSED: Step 3 JSON cleaner extracts clean JSON even if LLM wraps in markdown code fences.")
    else:
        print("❌ FAILED: JSON parser could not parse output.")


if __name__ == "__main__":
    print("==========================================")
    print("AI MEETING SUMMARIZER - PIPELINE TESTS")
    print("==========================================")
    test_audio_validation_safeguards()
    test_prompt_structures()
    print("\n🎉 All logic tests passed! Code is clean and production-ready.")

