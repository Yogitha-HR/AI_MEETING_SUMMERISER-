# 🎙️ AI Meeting Summarizer & Action-Item Extractor

An enterprise-ready AI tool built in **Python** that processes meeting recordings or transcripts, converts speech to text, synthesizes executive summaries, and extracts structured action items into machine-readable JSON.

---

## 🧭 Project Architecture Overview

```
                        [ Meeting Recording (.mp3, .wav, .m4a) ]
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Audio Upload & Transcription (Whisper ASR)                               │
│ - Validates file format, size (>1KB), and corruption                            │
│ - Automatic Speech Recognition using OpenAI Whisper ('base' model)              │
│ - Generates clean verbatim text transcript                                      │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼ [Verbatim Transcript]
                     ┌───────────────────┴───────────────────┐
                     │                                       │
                     ▼                                       ▼
┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐
│ STEP 2: Meeting Summary Engine         │ │ STEP 3: Action-Item Extractor          │
│ - Meeting Purpose                      │ │ - Task Description                     │
│ - Main Discussion Points               │ │ - Responsible Person (Assignee)        │
│ - Important Updates                    │ │ - Deadline / Timeframe                 │
│ - Key Decisions                        │ │ - Priority (High / Medium / Low)       │
│ - Unresolved Questions                 │ │ - Transcript Excerpt (Ground Truth)    │
│ - Next Steps                           │ │                                        │
│ Model: Ollama / Hugging Face           │ │ Output: Strictly Validated JSON Schema │
└────────────────────────────────────────┘ └────────────────────────────────────────┘
```

---

## 📂 Project Directory Structure

```
meeting_summarizer/
│
├── step1_transcription.py   # Step 1: File integrity validation & Whisper speech-to-text
├── step2_summary.py         # Step 2: 6-section executive summary generation
├── step3_action_items.py    # Step 3: Structured JSON action item extraction & parsing
├── app.py                   # Streamlit web interface with drag-and-drop & download buttons
├── test_pipeline.py         # Unit tests validating safeguards, prompts & JSON parsers
├── sample_meeting.txt       # Pre-loaded sample transcript for instant testing
├── requirements.txt         # Project dependencies (Zero LangChain)
└── README.md                # Documentation and Leader Presentation Guide
```

---

## 🗣️ How to Present This Project to Your Team Leader

When you demonstrate this project to your team lead or manager, follow this 4-minute presentation framework:

### 1. The Opening Pitch (30 seconds)
> *"Hello! Today I am presenting our **AI Meeting Summarizer and Action-Item Extractor**. In modern engineering and corporate teams, up to 30% of meeting time is lost because teams forget what was decided or miss follow-up deadlines. I built a modular 3-step pipeline in Python that turns raw audio recordings into structured, actionable items ready for ticketing systems like Jira or Asana."*

---

### 2. Walkthrough of the 3 Steps (2 minutes)

#### **Step 1: Audio Upload & Defensive Transcription**
* **What you say:**
  > *"First, in `step1_transcription.py`, we handle the audio ingestion. Before sending audio to an expensive AI model, our system performs defensive validation checks: it verifies that the file is not empty (0 bytes), confirms that the extension is supported (`.mp3`, `.wav`, `.m4a`), and ensures the audio stream is uncorrupted. Once validated, we use **Whisper**, an automatic speech recognition model, which produces an accurate transcript with proper punctuation."*

#### **Step 2: Executive Summary Generation**
* **What you say:**
  > *"Next, in `step2_summary.py`, we pass the transcript into our LLM using direct API calls. We avoid heavy abstractions like LangChain to keep the latency low and code maintainable. Our prompt enforces 6 standardized business sections: Meeting Purpose, Main Discussion Points, Updates, Key Decisions, Unresolved Questions, and Next Steps."*

#### **Step 3: Structured JSON Action-Item Extraction**
* **What you say:**
  > *"Finally, in `step3_action_items.py`, we extract all commitments. For each action item, the engine extracts the task description, owner, deadline, priority rating, and the exact supporting transcript quote as proof. We use Ollama's native JSON mode or Hugging Face schema parsing to guarantee valid JSON output that can be directly piped into Jira, GitHub Issues, or Slack."*

---

### 3. Answers to Tough Leader Questions

| Expected Question from Leader | Your Winning Answer |
| :--- | :--- |
| **"Why did you choose Whisper for Step 1?"** | *"Whisper is trained on 680,000 hours of multilingual audio. It handles background noise, accents, and technical jargon significantly better than legacy speech-to-text engines, and can run locally without recurring cloud costs."* |
| **"Why did you avoid using LangChain?"** | *"LangChain introduces unnecessary abstraction layers, heavy dependencies, and frequent breaking changes. By using direct native clients (`ollama` / `requests`), our code is lightweight, faster, easier to debug, and transparent in code reviews."* |
| **"How do you handle hallucinations in action items?"** | *"Our schema strictly mandates a `transcript_excerpt` field. The model must quote the exact words from the conversation that justified the task, ensuring full grounding and auditability."* |
| **"Can this run locally for privacy and compliance?"** | *"Yes! Both Whisper and Ollama run completely offline on our own machines. Sensitive company meeting recordings never leave our infrastructure."* |

---

## 🚀 Setup & Installation Guide

### Prerequisites
1. **Python 3.10+** installed on your system.
2. **Ollama** installed: Download from [ollama.com](https://ollama.com).
   - Pull the fast model: `ollama run llama3.2`

### Installation Steps
```bash
# 1. Navigate to the project directory
cd meeting_summarizer

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. (Optional) Run automated tests to verify code integrity
python test_pipeline.py

# 4. Launch the web application
streamlit run app.py
```

---

## 📊 Output Schema Example (Step 3)

```json
[
  {
    "task_description": "Deploy hotfix for billing token synchronization failure",
    "responsible_person": "Dave",
    "deadline": "Thursday by 5 PM",
    "priority": "High",
    "transcript_excerpt": "I will take ownership of this bug and deploy a hotfix by this Thursday at 5 PM."
  },
  {
    "task_description": "Draft complete migration architecture guide",
    "responsible_person": "Alex",
    "deadline": "Friday by 2 PM",
    "priority": "Medium",
    "transcript_excerpt": "I will draft the architecture guide and submit it to the team for review before Friday at 2 PM."
  }
]
```

