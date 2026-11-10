"""
STEP 2: MEETING SUMMARY GENERATION MODULE
=========================================
Purpose:
  Consumes the raw meeting transcript and sends a carefully crafted prompt 
  to an LLM (Ollama or Hugging Face) without any wrapper libraries like LangChain.
  Generates an executive-level summary containing all 6 required sections:
    1. Meeting Purpose
    2. Main Discussion Points
    3. Important Updates
    4. Key Decisions
    5. Unresolved Questions
    6. Next Steps

Why direct Ollama / Hugging Face (No LangChain)?
  - Eliminates unnecessary abstractions and dependency bloat.
  - Gives 100% transparent control over the prompt, tokens, and temperature.
  - Native, fast, and easier to debug and explain in corporate code reviews.
"""

import json
import requests

# Try importing ollama for local LLM inference
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


SUMMARY_SYSTEM_PROMPT = """You are a senior executive assistant and technical project manager. 
Your job is to analyze meeting transcripts thoroughly and generate a clear, concise, 
and strictly structured summary. Never hallucinate information that was not in the transcript."""


def build_summary_prompt(transcript: str) -> str:
    """
    Constructs the exact instruction prompt ensuring the 6 required sections are generated.
    """
    return f"""Please analyze the following meeting transcript and produce a structured executive summary.

Your response MUST contain the following 6 sections clearly formatted with markdown headings:

### 1. Meeting Purpose
A clear 1-2 sentence statement defining the core objective and purpose of this meeting.

### 2. Main Discussion Points
Bulleted breakdown of the central topics and themes discussed by participants.

### 3. Important Updates
Key progress reports, metrics, milestones, or status updates shared during the conversation.

### 4. Key Decisions
Explicit agreements, architectural decisions, policy shifts, or consensus reached.

### 5. Unresolved Questions
Open questions, blockers, disagreements, or topics postponed for future review.

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
    Calls Ollama locally to generate the summary.
    Requires: Ollama running on http://localhost:11434
    """
    if not OLLAMA_AVAILABLE:
        raise ImportError("The 'ollama' Python library is not installed. Run: pip install ollama")

    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": build_summary_prompt(transcript)}
    ]

    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "temperature": 0.2  # Low temperature ensures deterministic, factual summarizing
        }
    )
    return response["message"]["content"]


def generate_summary_with_huggingface(transcript: str, hf_token: str, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3") -> str:
    """
    Directly queries Hugging Face Inference API via HTTP POST (Zero LangChain).
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
        raise RuntimeError(f"Hugging Face API Error ({response.status_code}): {response.text}")

    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "").strip()
    return str(result)


def generate_meeting_summary(transcript: str, provider: str = "ollama", model_name: str = "llama3.2", hf_token: str = None) -> str:
    """
    Unified entry point for Step 2.
    Routes to either Ollama (local) or Hugging Face based on user configuration.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Cannot summarize an empty transcript.")

    if provider.lower() == "ollama":
        return generate_summary_with_ollama(transcript, model=model_name)
    elif provider.lower() == "huggingface":
        if not hf_token:
            raise ValueError("Hugging Face API token is required when choosing Hugging Face provider.")
        return generate_summary_with_huggingface(transcript, hf_token=hf_token, model_id=model_name)
    else:
        raise ValueError(f"Unknown provider: '{provider}'. Supported providers: 'ollama', 'huggingface'.")


if __name__ == "__main__":
    print("Step 2 module loaded successfully. Run app.py or call generate_meeting_summary(transcript).")

