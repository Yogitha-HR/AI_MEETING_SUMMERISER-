# 🎙️ AI Meeting Summarizer & Action-Item Extractor

An end-to-end Python pipeline that processes meeting recordings, performs speech-to-text transcription via Whisper, generates structured 6-point executive summaries, and extracts action items into verified JSON (Zero LangChain).

---

## 🏗️ Architecture

```
[Audio Recording / Transcript]
              │
              ▼
┌──────────────────────────────────────────────┐
│ STEP 1: Audio Validation & Whisper ASR       │
│ - Rejects empty (0-byte) or corrupted files  │
│ - Transcribes spoken speech to text          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ STEP 2: Executive Summary   │ │ STEP 3: Action-Item Engine  │
│ - Meeting Purpose           │ │ - Task Description          │
│ - Main Discussion Points    │ │ - Responsible Person        │
│ - Important Updates         │ │ - Deadline                  │
│ - Key Decisions             │ │ - Priority (High/Med/Low)   │
│ - Unresolved Questions      │ │ - Ground Truth Quote        │
│ - Next Steps                │ │ ➔ Machine-Readable JSON     │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

## 🚀 How to Run the Project

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Execute the end-to-end pipeline:**
   ```bash
   python run_demo.py
   ```

3. **Outputs generated:**
   * `output_summary.md`: Structured executive summary across 6 business categories.
   * `output_action_items.json`: Parsed action items with priorities, assignees, and transcript quotes.

---

## 🛠️ Key Technical Highlights
* **Zero LangChain Dependency:** Direct native calls to Ollama & REST APIs for maximum speed, transparency, and minimal dependency bloat.
* **Anti-Hallucination Grounding:** Every extracted action item mandates a verbatim `transcript_excerpt` to prove the task was committed to in conversation.
* **Defensive Ingestion:** Validates audio headers, file formats, and sizes before executing expensive speech recognition models.