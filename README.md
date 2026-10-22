# AI Practical Tasks & Internship Assignment Suite

This repository contains full implementations for three applications:
1. **AI Interview Coach (Day 3 Practicals)** — `app.py` & `coach.py`
2. **AI-Powered Text Summarizer (Day 2 Practical)** — `text_summarizer.py`
3. **AI Evidence-to-Decision Simulator (Internship Selection Assignment)** — `simulator_app.py` & `evidence_engine.py`

---

## 🛠️ Environment Setup

A virtual environment `coach_env` has been created with all dependencies installed (`streamlit`, `google-generativeai`, `pypdf`, `reportlab`, `python-dotenv`).

To activate `coach_env` in your terminal:
```bash
cd /home/sheikh/Desktop/zahid
source coach_env/bin/activate
```

### API Key Configuration
Set your Google Gemini API key in `.env`:
```bash
GEMINI_API_KEY="your_api_key_here"
```
*(Alternatively, enter your API key directly in the sidebar input within any of the Streamlit apps. Even without an API key, the apps feature built-in offline fallbacks to allow testing UI and state workflows.)*

---

## 1. 🎯 AI Interview Coach (`app.py` & `coach.py`)

Implements all Day 3 Practicals:
- **Step 4.3**: Connect profile analysis to `app.py` (displays role, match score %, summary, matching & missing skills, and raw JSON expander).
- **Step 5**: Dynamic interview question generation (`generate_questions()` in `coach.py` with custom question count slider 3–10).
- **Step 6**: Live interview flow with chat input (`st.chat_input`), real-time progress indicator (`st.progress`), and question-by-question conversation state.
- **Step 7**: Evaluation & feedback (`evaluate_answers()` evaluating relevance, depth, clarity, and examples), personal improvement plan (`final_report()`), readiness badge, rubric progress bars, and downloadable scorecard (`interview_scorecard.txt`).

### To Run:
```bash
source coach_env/bin/activate
streamlit run app.py
```
> **Sample Resume**: A pre-generated PDF resume is available at `sample_resume.pdf` for immediate testing.

---

## 2. 📝 AI-Powered Text Summarizer (`text_summarizer.py`)

A Streamlit application that accepts arbitrary text, articles, or paragraphs and uses Gemini via `llm.py` to produce structured summaries.
- Validates user input (displays warning if submitted empty).
- Allows choosing summary formats (Concise, Executive Brief, or Detailed).

### To Run:
```bash
source coach_env/bin/activate
streamlit run text_summarizer.py
```

---

## 3.   AI Evidence-to-Decision Simulator (`simulator_app.py`)

An investigative decision simulator for the Missing Electronic Shipment Case (PO-8841, ₹18 Lakh, 160 units missing).

### Key Features:
- **Evidence Extraction & Traceability**: Extracts structured records and text from PDFs, invoices, courier PODs, and emails.
- **Conflict Detection Matrix**: Identifies contradictions across sources (e.g. 500 units dispatched in `EVID-002` vs 340 units received in `EVID-004`; courier POD limitations in `EVID-003`; seal tampering).
- **Grounded Investigator Q&A**: Answers questions by strictly citing evidence IDs (`[EVID-xxx]`) and defends against prompt injections embedded in untrusted documents.
- **Controlled Evidence Requests**: Sensitive records (GPS telematics `REQ-001`, warehouse weighbridge logs `REQ-002`, supplier CCTV `REQ-003`) remain sealed until requested with valid justification. Nonexistent IDs (`REQ-999`) are safely rejected.
- **Decision Submission & 100-Point Rubric**: Evaluates evidence grounding (25), contradiction handling (25), confidence calibration (20), counterevidence rigor (15), and actionability (15).
- **Adaptive Retries & History**: Stores all attempts in session state, compares revisions, and exports the complete forensic dossier.

### To Run:
```bash
source coach_env/bin/activate
streamlit run simulator_app.py
```

### Running Automated Test Suite:
Run the unit test suite covering all minimum test cases:
```bash
coach_env/bin/python test_simulator.py
coach_env/bin/python test_coach.py
```
Both test suites verify:
- Conflicting quantities and source tracking across documents
- Courier POD limitation validation
- Rejection of nonexistent evidence IDs
- Untrusted content & prompt injection resistance
- JSON repair and API failure recovery
- Insufficient evidence / premature conclusion detection

