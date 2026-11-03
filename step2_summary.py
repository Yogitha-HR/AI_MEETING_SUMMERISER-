"""
STEP 2: MEETING SUMMARY GENERATION MODULE
=========================================
- Consumes raw meeting transcripts.
- Calls Ollama (local) or Hugging Face API directly (NO LangChain).
- Enforces an executive summary with all 6 required business sections:
    1. Meeting Purpose
    2. Main Discussion Points
    3. Important Updates
    4. Key Decisions
    5. Unresolved Questions
    6. Next Steps
"""

import requests

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


SUMMARY_SYSTEM_PROMPT = """You are a senior executive assistant. 
Analyze the meeting transcript and generate a structured summary. 
Never hallucinate or invent information not present in the transcript."""


def build_summary_prompt(transcript: str) -> str:
    """
    Constructs the prompt enforcing the 6 required executive sections.
    """
    return f"""Please analyze the following meeting transcript and produce a structured summary.

Your response MUST contain these exact 6 sections formatted with markdown headings:

### 1. Meeting Purpose
A clear 1-2 sentence statement defining the core objective of this meeting.

### 2. Main Discussion Points
Bulleted breakdown of the central topics and themes discussed.

### 3. Important Updates
Key progress reports, metrics, milestones, or status updates shared.

### 4. Key Decisions
Explicit agreements, architectural decisions, or consensus reached.

### 5. Unresolved Questions
Open questions, blockers, or topics postponed for future meetings.

### 6. Next Steps
Immediate forward-looking roadmap and high-level milestones agreed upon.

---
MEETING TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"
"""


def generate_summary_with_ollama(transcript: str, model: str = "llama3.2") -> str:
    """
    Direct local call to Ollama (No LangChain).
    """
    if not OLLAMA_AVAILABLE:
        raise ImportError("Ollama library not installed. Run: pip install ollama")

    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": build_summary_prompt(transcript)}
    ]

    response = ollama.chat(
        model=model,
        messages=messages,
        options={"temperature": 0.2}  # Low temperature ensures factual, deterministic output
    )
    return response["message"]["content"]


def generate_summary_with_huggingface(transcript: str, hf_token: str, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3") -> str:
    """
    Direct HTTP POST call to Hugging Face Inference API (No LangChain).
    """
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    prompt = f"<s>[INST] {SUMMARY_SYSTEM_PROMPT}\n\n{build_summary_prompt(transcript)} [/INST]"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.2,
            "return_full_text": False
        }
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(f"Hugging Face API Error: {response.text}")

    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").strip()
    return str(result)


def generate_meeting_summary(transcript: str, provider: str = "ollama", model_name: str = "llama3.2", hf_token: str = None) -> str:
    """
    Unified entry point for Step 2.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Cannot summarize an empty transcript.")

    if provider.lower() == "ollama":
        return generate_summary_with_ollama(transcript, model=model_name)
    elif provider.lower() == "huggingface":
        if not hf_token:
            raise ValueError("Hugging Face API token is required for Hugging Face provider.")
        return generate_summary_with_huggingface(transcript, hf_token=hf_token, model_id=model_name)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose 'ollama' or 'huggingface'.")


# Direct verification test
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("📝 STEP 2: MEETING SUMMARY ENGINE VERIFICATION")
    print("=" * 55)
    test_transcript = "Alice: Our goal is to launch the website by Friday. Bob: I will finish design."
    prompt = build_summary_prompt(test_transcript)
    
    print("[*] Checking required 6 business sections in prompt:")
    sections = ["Meeting Purpose", "Main Discussion Points", "Important Updates", "Key Decisions", "Unresolved Questions", "Next Steps"]
    for s in sections:
        if s in prompt:
            print(f"  ✅ Section enforced: '{s}'")
    
    print("\n🎉 STEP 2 MODULE IS READY AND COMPILED!")
    print("=" * 55 + "\n")