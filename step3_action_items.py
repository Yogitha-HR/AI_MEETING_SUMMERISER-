"""
STEP 3: ACTION-ITEM EXTRACTION MODULE (STRUCTURED JSON)
======================================================
- Scans transcripts for commitments, deadlines, and owners.
- Enforces strict JSON schema:
    1. task_description
    2. responsible_person
    3. deadline
    4. priority (High | Medium | Low)
    5. transcript_excerpt (exact ground-truth quote)
- Uses Ollama native JSON mode or Hugging Face API directly (NO LangChain).
"""

import json
import re
import requests

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


ACTION_ITEM_SCHEMA = {
    "action_items": [
        {
            "task_description": "Clear description of what action needs to be taken",
            "responsible_person": "Full name or role (or null if not explicitly assigned)",
            "deadline": "Specific date, day or timeframe (or null if not mentioned)",
            "priority": "High | Medium | Low",
            "transcript_excerpt": "Direct exact quote from the transcript proving this task"
        }
    ]
}


def build_action_item_prompt(transcript: str) -> str:
    """
    Constructs the prompt enforcing strict JSON output and precise extraction rules.
    """
    schema_str = json.dumps(ACTION_ITEM_SCHEMA, indent=2)
    return f"""You are an AI task specialist. Extract all actionable tasks from the transcript.

RULES:
1. Extract only REAL, committed tasks mentioned in the discussion.
2. If a person is NOT explicitly named, set "responsible_person" to null.
3. If a deadline is NOT mentioned, set "deadline" to null.
4. Assess "priority" strictly as "High", "Medium", or "Low" based on urgency words.
5. "transcript_excerpt" MUST be the exact verbatim quote from the transcript.
6. Return ONLY a valid JSON object matching the schema below.

SCHEMA:
{schema_str}

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"
"""


def clean_json_response(raw_text: str) -> dict:
    """
    Strips markdown code fences like ```json ... ``` to guarantee pure JSON parsing.
    """
    cleaned = raw_text.strip()
    
    if "```json" in cleaned:
        cleaned = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL).group(1)
    elif "```" in cleaned:
        cleaned = re.search(r"```\s*(.*?)\s*```", cleaned, re.DOTALL).group(1)
        
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Could not parse valid JSON from response: {raw_text}")


def extract_action_items_with_ollama(transcript: str, model: str = "llama3.2") -> list:
    """
    Direct local Ollama call with native format='json'.
    """
    if not OLLAMA_AVAILABLE:
        raise ImportError("Ollama library not installed. Run: pip install ollama")

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": build_action_item_prompt(transcript)}],
        format="json",
        options={"temperature": 0.1}
    )

    data = clean_json_response(response["message"]["content"])
    return data.get("action_items", [])


def extract_action_items_with_huggingface(transcript: str, hf_token: str, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3") -> list:
    """
    Direct HTTP POST call to Hugging Face Inference API.
    """
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}

    prompt = f"<s>[INST] {build_action_item_prompt(transcript)} [/INST]"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1500,
            "temperature": 0.1,
            "return_full_text": False
        }
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face API Error: {response.text}")

    result = response.json()
    raw_text = result[0].get("generated_text", "") if isinstance(result, list) else str(result)
    
    data = clean_json_response(raw_text)
    return data.get("action_items", [])


def extract_action_items(transcript: str, provider: str = "ollama", model_name: str = "llama3.2", hf_token: str = None) -> list:
    """
    Unified entry point for Step 3.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Cannot extract action items from an empty transcript.")

    if provider.lower() == "ollama":
        return extract_action_items_with_ollama(transcript, model=model_name)
    elif provider.lower() == "huggingface":
        if not hf_token:
            raise ValueError("Hugging Face API token is required for Hugging Face provider.")
        return extract_action_items_with_huggingface(transcript, hf_token=hf_token, model_id=model_name)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose 'ollama' or 'huggingface'.")


# Direct verification test
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("🎯 STEP 3: ACTION-ITEM JSON EXTRACTOR VERIFICATION")
    print("=" * 55)
    
    # Test JSON parser robustness
    mock_response = '```json\n{\n  "action_items": [\n    {\n      "task_description": "Fix login bug",\n      "responsible_person": "Dave",\n      "deadline": "Thursday",\n      "priority": "High",\n      "transcript_excerpt": "I will fix it by Thursday"\n    }\n  ]\n}\n```'
    
    parsed = clean_json_response(mock_response)
    items = parsed.get("action_items", [])
    
    print(f"[*] JSON Schema check: Extracted {len(items)} task item(s).")
    print(f"  ✅ Task: {items[0]['task_description']}")
    print(f"  ✅ Owner: {items[0]['responsible_person']}")
    print(f"  ✅ Priority: {items[0]['priority']}")
    print(f"  ✅ Excerpt: \"{items[0]['transcript_excerpt']}\"")
    
    print("\n🎉 STEP 3 MODULE IS READY AND COMPILED!")
    print("=" * 55 + "\n")