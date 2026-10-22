import streamlit as st
from coach import analyze_profile, generate_questions, evaluate_answers, final_report
from pypdf import PdfReader
import os

st.set_page_config(page_title="AI Interview Coach", layout="wide")

st.title("AI Interview Coach")
st.caption("Personalized mock interviews, real-time feedback, and preparation analytics powered by Gemini.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_key_input = st.text_input(
        "Gemini API Key (optional if in .env)",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Enter your Google Gemini API key if not configured in the .env file."
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input
        os.environ["GEMINI_API_KEY"] = api_key_input

    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Upload your resume (PDF).")
    st.markdown("2. Paste the target job description.")
    st.markdown("3. Analyze your profile to see skill match.")
    st.markdown("4. Generate questions & conduct mock interview.")
    st.markdown("5. Review evaluations & download scorecard.")

# Step 4: Resume upload and text extraction
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Upload Resume")
    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    resume_text = ""
    if resume_file:
        try:
            reader = PdfReader(resume_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    resume_text += extracted + "\n"
            if resume_text.strip():
                st.success(f"Resume loaded ({len(reader.pages)} page(s) parsed).")
            else:
                st.warning("Could not extract text from this PDF (it might be scanned).")
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

with col_right:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=180,
        placeholder="We are looking for a Senior Python Developer with experience in REST APIs, Docker, and SQL..."
    )

# Step 4.3: Connect profile analysis to app.py
if resume_file and resume_text.strip():
    if st.button("Analyze my profile"):
        if job_description.strip() == "":
            st.warning("Please paste a job description first.")
        else:
            with st.spinner("Analyzing your profile..."):
                st.session_state.pop("questions", None)
                st.session_state.resume_text = resume_text
                st.session_state.job_description = job_description
                st.session_state.analysis = analyze_profile(
                    resume_text,
                    job_description
                )

if "analysis" in st.session_state:
    a = st.session_state.analysis
    st.header(f"Profile analysis: {a.get('role', 'Role')}")
    st.metric("Match score", f"{a.get('match_score', 0)}%")
    st.write(a.get("summary", ""))
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Matching skills")
        for skill in a.get("matching_skills", []):
            st.write("-", skill)
    with col2:
        st.subheader("Missing skills")
        for skill in a.get("missing_skills", []):
            st.write("-", skill)
    with st.expander("See raw JSON from the AI"):
        st.json(a)

# Step 5: Generate interview questions
if "analysis" in st.session_state:
    st.divider()
    st.header("Interview questions")
    num = st.slider("How many questions?", 3, 10, 5)
    if st.button("Generate questions"):
        st.session_state.interview_started = False
        with st.spinner("Writing questions for you..."):
            result = generate_questions(
                st.session_state.analysis,
                st.session_state.resume_text,
                st.session_state.job_description,
                num,
            )
            st.session_state.questions = result.get("questions", [])

if "questions" in st.session_state and st.session_state.questions:
    for i, q in enumerate(st.session_state.questions, start=1):
        st.markdown(f"**Q{i}.** {q.get('question')}")
        st.caption(f"Type: {q.get('type')} | Skill: {q.get('skill')}")

    # Step 6 Part 1: Start a fresh interview
    if st.button("Start interview"):
        st.session_state.pop("evaluations", None)
        st.session_state.pop("report", None)
        first_q = st.session_state.questions[0]["question"]
        st.session_state.interview_started = True
        st.session_state.current_q = 0
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"**Q1.** {first_q}"
        }]
        st.session_state.answers = []
        st.rerun()

# Step 6 Part 2: Add the interview flow
if "questions" in st.session_state and st.session_state.get("interview_started"):
    st.divider()
    st.header("Interview")
    questions = st.session_state.questions
    current = st.session_state.current_q
    total = len(questions)
    st.progress(current / total, text=f"Answered {current} of {total}")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if current < total:
        answer = st.chat_input("Type your answer...")
        if answer:
            q = questions[current]
            st.session_state.messages.append({"role": "user", "content": answer})
            st.session_state.answers.append({
                "question": q.get("question"),
                "type": q.get("type"),
                "skill": q.get("skill"),
                "answer": answer,
            })
            st.session_state.current_q += 1
            nxt = st.session_state.current_q
            if nxt < total:
                next_text = f"**Q{nxt + 1}.** {questions[nxt]['question']}"
            else:
                next_text = "That's the end of the interview. Thank you!"
            st.session_state.messages.append({"role": "assistant", "content": next_text})
            st.rerun()
    else:
        st.success("Interview complete! Your answers are saved.")

# Step 7 Part 5: Add the evaluation button and results
if (
    st.session_state.get("interview_started")
    and st.session_state.get("answers")
    and st.session_state.current_q >= len(st.session_state.questions)
):
    if st.button("Evaluate my answers"):
        with st.spinner("Evaluating your answers..."):
            result = evaluate_answers(
                st.session_state.answers,
                st.session_state.analysis.get("role", "this role")
            )
            st.session_state.evaluations = result.get("evaluations", [])

if "evaluations" in st.session_state:
    st.divider()
    st.header("Interview feedback")
    for i, item in enumerate(st.session_state.evaluations, start=1):
        st.subheader(f"Question {i}")
        st.write(f"Relevance: {item.get('relevance', 0)}/10")
        st.write(f"Depth: {item.get('depth', 0)}/10")
        st.write(f"Clarity: {item.get('clarity', 0)}/10")
        st.write(f"Examples: {item.get('examples', 0)}/10")
        st.write(item.get("feedback", ""))
        st.info(item.get("better_answer_tip", ""))

# Step 7 Part 6: Display the final scorecard and improvement plan
if st.session_state.get("interview_started") and "evaluations" in st.session_state:
    st.divider()
    st.header("Final scorecard")
    evals = st.session_state.evaluations
    overall = round(sum(e.get("score", sum(e.get(k, 0) for k in ["relevance", "depth", "clarity", "examples"]) / 4) for e in evals) / len(evals), 1) if evals else 0
    if overall >= 7.5:
        readiness = "Ready for interviews"
    elif overall >= 5:
        readiness = "Almost ready; more practice recommended"
    else:
        readiness = "More practice needed"
    col1, col2 = st.columns(2)
    col1.metric("Interview score", f"{overall}/10")
    col2.metric(
        "Resume match",
        f"{st.session_state.analysis.get('match_score', 0)}%"
    )
    st.subheader(readiness)
    st.markdown("#### Score by rubric area")
    for area in ["relevance", "depth", "clarity", "examples"]:
        avg = sum(e.get(area, 0) for e in evals) / len(evals) if evals else 0
        st.write(f"{area.title()}: {avg:.1f}/10")
        st.progress(min(avg / 10, 1.0))
    if st.button("Get my improvement plan"):
        with st.spinner("Preparing your personal feedback..."):
            st.session_state.report = final_report(
                st.session_state.analysis,
                st.session_state.answers,
                evals,
            )
    if "report" in st.session_state:
        report = st.session_state.report
        st.markdown("#### Strengths")
        for item in report.get("strengths", []):
            st.write("-", item)
        st.markdown("#### Areas to improve")
        for item in report.get("improvements", []):
            st.write("-", item)
        st.markdown("#### Study plan")
        for item in report.get("study_plan", []):
            st.write("-", item)
        st.success(report.get("message", ""))
        lines = [
            "AI INTERVIEW COACH - SCORECARD",
            f"Role: {st.session_state.analysis.get('role', '')}",
            f"Interview score: {overall}/10",
            f"Resume match: {st.session_state.analysis.get('match_score', 0)}%",
            f"Readiness: {readiness}",
            "", "STRENGTHS:",
            *[f"- {x}" for x in report.get("strengths", [])],
            "", "AREAS TO IMPROVE:",
            *[f"- {x}" for x in report.get("improvements", [])],
            "", "STUDY PLAN:",
            *[f"- {x}" for x in report.get("study_plan", [])],
        ]
        st.download_button(
            "Download scorecard",
            "\n".join(lines),
            file_name="interview_scorecard.txt",
        )

