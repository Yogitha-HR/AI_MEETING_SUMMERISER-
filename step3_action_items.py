"""
STEP 3: ACTION-ITEM EXTRACTION MODULE (STRUCTURED JSON)
======================================================
Purpose:
  Scans the meeting transcript for commitments, assigned tasks, and follow-ups.
  Enforces a strict JSON output schema containing:
    1. Task description
    2. Responsible person (if explicitly stated, otherwise null)
    3. Deadline (if explicitly stated, otherwise null)
    4. Priority ('High', 'Medium', 'Low' if supported by discussion)
    5. Supporting transcript excerpt (exact verbatim quote)

Why Structured JSON?
  Outputs can be directly loaded into Jira, Asana, Trello, Google Tasks, or an internal SQL database.
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
            "responsible_person": "Full name or team role (or null if not explicitly assigned)",
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
    return f"""You are an AI task extraction engine. Your job is to extract actionable tasks and follow-up items from the meeting transcript.

RULES:
1. Extract only REAL, committed tasks or follow-ups mentioned in the discussion.
2. If a responsible person is NOT explicitly named, set "responsible_person" to null.
3. If a deadline or timeframe is NOT mentioned, set "deadline" to null.
4. Assess "priority" strictly as "High", "Medium", or "Low" based on urgency words (e.g., "ASAP", "blocker", "critical" -> High; "eventually", "nice to have" -> Low).
5. "transcript_excerpt" MUST be the exact quote from the transcript where this task was assigned or discussed.
6. Return ONLY a valid JSON object matching the schema below. Do not include introductory or concluding conversational text.

SCHEMA:
{schema_str}

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"
"""


def clean_json_response(raw_text: str) -> dict:
    """
    Cleans and extracts JSON if the model wrapped it in markdown tags like ```json ... ```.
    """
    cleaned = raw_text.strip()
    
    # Remove markdown code fence if present
    if "```json" in cleaned:
        cleaned = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL).group(1)
    elif "```" in cleaned:
        cleaned = re.search(r"```\s*(.*?)\s*```", cleaned, re.DOTALL).group(1)
        
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Fallback regex extraction of outer JSON braces
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Could not parse valid JSON from model response: {raw_text}") from e


def extract_action_items_with_ollama(transcript: str, model: str = "llama3.2") -> list:
    """
    Uses Ollama's native JSON mode to guarantee valid JSON formatting.
    """
    if not OLLAMA_AVAILABLE:
        raise ImportError("The 'ollama' Python library is not installed. Run: pip install ollama")

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": build_action_item_prompt(transcript)}],
        format="json",  # Ollama forces constrained JSON decoding
        options={"temperature": 0.1}
    )

    data = clean_json_response(response["message"]["content"])
    return data.get("action_items", [])


def extract_action_items_with_huggingface(transcript: str, hf_token: str, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3") -> list:
    """
    Queries Hugging Face Inference API and parses the returned JSON string.
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
        raise RuntimeError(f"Hugging Face API Error ({response.status_code}): {response.text}")

    result = response.json()
    raw_text = result[0].get("generated_text", "") if isinstance(result, list) else str(result)
    
    data = clean_json_response(raw_text)
    return data.get("action_items", [])


def extract_action_items(transcript: str, provider: str = "ollama", model_name: str = "llama3.2", hf_token: str = None) -> list:
    """
    Unified entry point for Step 3.
    Returns a Python list of action item dictionaries.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Cannot extract action items from an empty transcript.")

    if provider.lower() == "ollama":
        return extract_action_items_with_ollama(transcript, model=model_name)
    elif provider.lower() == "huggingface":
        if not hf_token:
            raise ValueError("Hugging Face API token is required when choosing Hugging Face provider.")
        return extract_action_items_with_huggingface(transcript, hf_token=hf_token, model_id=model_name)
    else:
        raise ValueError(f"Unknown provider: '{provider}'. Supported: 'ollama', 'huggingface'.")


if __name__ == "__main__":
    print("Step 3 module loaded successfully. Run app.py or call extract_action_items(transcript).")

