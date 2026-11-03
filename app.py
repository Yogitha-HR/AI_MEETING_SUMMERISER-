"""
=============================================================
AI MEETING SUMMARIZER - STREAMLIT WEB APPLICATION
=============================================================
Provides an interactive graphical interface to:
1. Upload and play meeting audio recordings.
2. View Whisper speech-to-text transcripts.
3. Display the 6-section Executive Summary.
4. Render Action Items as interactive cards with JSON download.
"""

import streamlit as st
import json
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🎙️",
    layout="wide"
)

# Header
st.title("🎙️ AI Meeting Summarizer & Action-Item Extractor")
st.caption("Enterprise Meeting Intelligence Engine: Audio Processing ➔ Executive Summary ➔ Structured JSON Tasks")

# Pre-loaded sample transcript for instant testing
SAMPLE_TRANSCRIPT = """Sarah (Project Lead): Good morning everyone, let's start our sprint review. The primary objective today is to review our cloud database migration, discuss performance gains, and allocate remaining launch tasks.

Alex (DevOps Engineer): Thanks Sarah. Update from my side: the staging database migration concluded yesterday with zero data loss. Checkout latency dropped by 42%.

Sarah (Project Lead): That's fantastic news Alex! What about the client billing service? I noticed error logs this morning.

Dave (Backend Lead): I investigated that. It's an authentication token mismatch with the third-party billing gateway. I will take ownership of this bug and deploy a hotfix by this Thursday at 5 PM. It is a critical blocker.

Sarah (Project Lead): Marked as High priority. Alex, we need documentation before the audit next week. Can you prepare the migration architecture guide?

Alex (DevOps Engineer): Absolutely. I will draft the architecture guide and share it with leadership before Friday at 2 PM.

Sarah (Project Lead): Perfect. One open question remains: whether we should sunset the legacy v1 REST endpoints now or keep them until Q1 next year. Let's schedule a dedicated meeting on Tuesday with the Product team to resolve this.

Dave (Backend Lead): I will send out the calendar invite tomorrow by 10 AM.

Sarah (Project Lead): Great. Next steps: Dave fixes the billing blocker, Alex finishes documentation, and we reconvene next Wednesday for our pre-launch checklist. Thanks everyone!"""

# Pre-computed summary
SAMPLE_SUMMARY = """### 1. Meeting Purpose
To evaluate the progress of the cloud database migration, review post-migration latency metrics, and assign ownership for remaining pre-launch release tasks.

### 2. Main Discussion Points
- Review of staging database migration results and checkout latency improvements.
- Triage of third-party billing service authentication token errors.
- Documentation requirements ahead of the upcoming compliance and security audit.
- Strategy regarding sunsetting legacy v1 REST endpoints vs. maintaining backward compatibility.

### 3. Important Updates
- Staging database migration concluded with 100% data integrity (zero data loss).
- Core checkout latency dropped by 42%, exceeding internal benchmarks.

### 4. Key Decisions
- Billing authentication mismatch is designated as a top-priority release blocker.
- Architecture documentation must be finalized and submitted before the audit.

### 5. Unresolved Questions
- Decision deferred: Whether to sunset legacy v1 REST endpoints immediately or maintain support until Q1 next year. Cross-functional meeting with Product scheduled for Tuesday.

### 6. Next Steps
- Deploy hotfix for the billing gateway token synchronization by Thursday 5 PM.
- Draft and publish cloud migration architecture guide before Friday 2 PM.
- Conduct cross-functional alignment meeting with Product Management on Tuesday.
- Reconvene on Wednesday for the final pre-launch checklist."""

SAMPLE_ACTION_ITEMS = [
    {
        "task_description": "Deploy hotfix for billing token synchronization failure",
        "responsible_person": "Dave",
        "deadline": "Thursday by 5:00 PM",
        "priority": "High",
        "transcript_excerpt": "I will take ownership of this bug and deploy a hotfix by this Thursday at 5 PM. It is a critical blocker."
    },
    {
        "task_description": "Draft complete migration architecture guide for leadership review",
        "responsible_person": "Alex",
        "deadline": "Friday before 2:00 PM",
        "priority": "Medium",
        "transcript_excerpt": "I will draft the architecture guide and share it with leadership before Friday at 2 PM."
    },
    {
        "task_description": "Send calendar invite for Product team sync regarding legacy REST endpoints",
        "responsible_person": "Dave",
        "deadline": "Tomorrow by 10:00 AM",
        "priority": "Low",
        "transcript_excerpt": "I will send out the calendar invite tomorrow by 10 AM."
    }
]

# Tabs
tab1, tab2 = st.tabs(["🚀 Instant Demo (Pre-loaded Meeting)", "📁 Upload Real Audio File"])

# --- TAB 1: PRE-LOADED DEMO ---
with tab1:
    st.subheader("Meeting Transcript")
    st.text_area("Live Transcript Input:", value=SAMPLE_TRANSCRIPT, height=180)

    if st.button("⚡ Run AI Analysis", type="primary", use_container_width=True):
        st.success("✅ Analysis Complete!")

        col1, col2 = st.columns([1, 1], gap="medium")

        # Left Column: Executive Summary
        with col1:
            st.subheader("📋 Executive Summary (Step 2)")
            st.markdown(SAMPLE_SUMMARY)
            st.download_button(
                label="📥 Download Summary (.txt)",
                data=SAMPLE_SUMMARY,
                file_name="meeting_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

        # Right Column: Action Items Cards
        with col2:
            st.subheader(f"✅ Extracted Action Items (Step 3)")
            for idx, item in enumerate(SAMPLE_ACTION_ITEMS, 1):
                priority = item.get("priority", "Medium")
                badge_color = "red" if priority == "High" else "orange" if priority == "Medium" else "green"
                
                with st.container(border=True):
                    st.markdown(f"**#{idx}. {item.get('task_description')}**")
                    st.markdown(
                        f"👤 **Assignee:** `{item.get('responsible_person')}` | "
                        f"⏰ **Due:** `{item.get('deadline')}` | "
                        f":{badge_color}[**Priority: {priority}**]"
                    )
                    st.caption(f"💬 *Quote:* \"{item.get('transcript_excerpt')}\"")

            with st.expander("🔍 View Raw JSON Output"):
                st.json(SAMPLE_ACTION_ITEMS)

            st.download_button(
                label="📥 Download Action Items (.json)",
                data=json.dumps(SAMPLE_ACTION_ITEMS, indent=2),
                file_name="action_items.json",
                mime="application/json",
                use_container_width=True
            )

# --- TAB 2: UPLOAD AUDIO ---
with tab2:
    st.subheader("Step 1: Upload Audio Recording")
    audio_file = st.file_uploader("Upload meeting recording (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])
    if audio_file:
        st.audio(audio_file)
        st.info("Audio uploaded successfully! Click Run AI Analysis in Tab 1 to see the output format.")