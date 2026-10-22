import streamlit as st
import os
from evidence_engine import (
    EvidenceStore,
    CONTROLLED_CATALOG,
    investigate_question,
    evaluate_decision
)

st.set_page_config(
    page_title="AI Evidence-to-Decision Simulator",
    page_icon="🔍",
    layout="wide"
)

# Initialize Session State
if "evidence_store" not in st.session_state:
    st.session_state.evidence_store = EvidenceStore()

if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "decision_attempts" not in st.session_state:
    st.session_state.decision_attempts = []

store: EvidenceStore = st.session_state.evidence_store

# Sidebar
with st.sidebar:
    st.title("🛡️ Case Control Panel")
    st.caption("Missing Shipment Forensic Investigation")
    
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
    active_evids = store.get_active_evidence()
    st.metric("Active Evidence Records", len(active_evids))
    st.metric("Controlled Requests Released", len(store.unlocked_requests))
    st.metric("Decision Attempts", len(st.session_state.decision_attempts))

    st.markdown("---")
    st.markdown("**Case Metadata:**")
    st.write("• **PO Number:** PO-8841")
    st.write("• **Consignment:** 500 MCU Modules")
    st.write("• **Total Value:** ₹18,00,000 (18 Lakh)")
    st.write("• **Discrepancy:** 160 units missing")
    st.write("• **Estimated Loss:** ₹5,76,000")

    if st.button("Reset Case Simulation", type="secondary"):
        st.session_state.evidence_store = EvidenceStore()
        st.session_state.qa_history = []
        st.session_state.decision_attempts = []
        st.rerun()

# Main Header
st.title("  AI Evidence-to-Decision Simulator")
st.subheader("Case Dossier: The Discrepant Electronic Consignment (PO-8841)")

# Tabs for workflow stages
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    " Case Workspace & Documents",
    "Evidence Register & Timeline",
    "Conflict Detection",
    "Grounded Investigator Q&A",
    "Controlled Record Requests",
    "Decision Submission & Rubric"
])

# ==========================================
# TAB 1: Case Workspace & Documents
# ==========================================
with tab1:
    st.markdown("###   Case Overview & Scenario")
    st.info(
        "**Scenario Brief:** Apex Technologies ordered 500 units of high-precision MCU modules (NC-9020) worth ₹18 lakh from NovaCore Electronics. "
        "The supplier claims all 500 units were packed and dispatched in 5 cartons. The courier (SwiftRoute Express) recorded 'DELIVERY COMPLETED' at Peenya Warehouse. "
        "However, warehouse inward inspection recorded receiving only 340 units — Cartons #4 and #5 had been slit open, filled with ballast paper, and resealed with clear cellophane tape. "
        "In addition, an email requested a last-minute address change to Whitefield. As the lead corporate investigator, you must establish what the records support, "
        "uncover what remains uncertain, request confidential telemetry records, and submit a grounded decision."
    )

    st.markdown("---")
    st.subheader(" Document Evidence Extractor & Viewer")
    
    col_sel, col_filter = st.columns([2, 1])
    active_docs = store.get_active_evidence()
    doc_keys = list(active_docs.keys())
    
    with col_sel:
        selected_id = st.selectbox(
            "Select an Evidence Document to inspect:",
            doc_keys,
            format_func=lambda k: f"{k} — {active_docs[k]['title']} ({active_docs[k]['doc_type']})"
        )
    
    if selected_id:
        doc = active_docs[selected_id]
        c1, c2, c3 = st.columns(3)
        c1.metric("Evidence ID", doc["id"])
        c2.metric("Date / Timestamp", doc["date"])
        c3.metric("Source / Origin", doc["source"])
        
        st.markdown(f"**Document Type:** `{doc['doc_type']}`")
        st.markdown("**Key Claims:**")
        for claim in doc["key_claims"]:
            st.markdown(f"- {claim}")
            
        with st.expander(" View Extracted Text / Raw Document Content", expanded=True):
            st.code(doc["raw_text"], language="text")

# ==========================================
# TAB 2: Evidence Register & Timeline
# ==========================================
with tab2:
    st.subheader(" Structured Evidence Register")
    reg_data = []
    for eid, edata in store.get_active_evidence().items():
        reg_data.append({
            "Evidence ID": eid,
            "Document Title": edata["title"],
            "Source": edata["source"],
            "Date": edata["date"],
            "Type": edata["doc_type"]
        })
    st.dataframe(reg_data, use_container_width=True)

    st.markdown("---")
    st.subheader(" Chronological Case Timeline")
    timeline = store.get_timeline()
    for item in timeline:
        v_badge = " Confirmed Fact" if item.get("verified", True) else " Disputed / Unverified"
        with st.container(border=True):
            st.markdown(f"#### {item['date']} {item['time']} — {item['party']} (`{item['evidence_id']}`)")
            st.markdown(f"**Event:** {item['event']}")
            st.caption(f"Status: {v_badge} | Reference: {item['evidence_id']}")
            if "note" in item:
                st.warning(f"Note: {item['note']}")

# ==========================================
# TAB 3: Conflict Detection
# ==========================================
with tab3:
    st.subheader(" Cross-Record Contradictions & Conflict Matrix")
    st.write("The system continuously analyzes active documents to highlight direct contradictions and anomalies:")

    conflicts = store.detect_conflicts()
    for conf in conflicts:
        with st.container(border=True):
            c_header, c_status = st.columns([3, 1])
            with c_header:
                st.markdown(f"### {conf['conflict_id']}: {conf['title']}")
            with c_status:
                st.error(conf["status"])

            colA, colB = st.columns(2)
            with colA:
                st.markdown(f"**Claim A from {conf['source_a']}:**")
                st.info(conf["claim_a"])
            with colB:
                st.markdown(f"**Claim B from {conf['source_b']}:**")
                st.warning(conf["claim_b"])

            st.markdown(f"**Investigative Significance:** {conf['discrepancy']}")

# ==========================================
# TAB 4: Grounded Investigator Q&A
# ==========================================
with tab4:
    st.subheader(" Evidence-Grounded Case Assistant")
    st.caption("Ask questions about the case. The AI is restricted to citing active evidence IDs and defending against prompt injections.")

    q_input = st.text_input(
        "Enter your investigation question:",
        placeholder="e.g. Does the courier POD confirm that all 500 units arrived? What explains the clear tape on Cartons #4 and #5?"
    )

    if st.button("Ask Assistant", type="primary"):
        if not q_input.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Analyzing active evidence records..."):
                res = investigate_question(q_input, store)
                st.session_state.qa_history.insert(0, res)

    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("#### Inquiry History")
        for item in st.session_state.qa_history:
            with st.chat_message("user"):
                st.write(item["question"])
            with st.chat_message("assistant"):
                st.markdown(item["answer"])
                st.caption(f"Answered based on {item['active_evidence_count']} active records at {item['timestamp']}")

# ==========================================
# TAB 5: Controlled Evidence Requests
# ==========================================
with tab5:
    st.subheader("Controlled / Confidential Evidence Release Desk")
    st.info(
        "Certain sensitive operational records are sealed. To obtain access, specify the Request ID and provide an investigative justification. "
        "Hidden records are strictly excluded from the LLM context until officially released."
    )

    st.markdown("#### Sealed Record Catalog")
    cat_items = []
    for req_id, meta in CONTROLLED_CATALOG.items():
        is_rel = req_id in store.unlocked_requests
        cat_items.append({
            "Request ID": req_id,
            "Record Name": meta["title"],
            "Source System": meta["source"],
            "Status": " RELEASED" if is_rel else "🔒 SEALED",
            "Assigned ID": meta["assigned_id"]
        })
    st.dataframe(cat_items, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Request a Sealed Record")
    with st.form("request_form"):
        req_id_input = st.text_input("Enter Request ID (e.g. REQ-001, REQ-002, REQ-003):", placeholder="REQ-001")
        justification_input = st.text_area(
            "Investigative Justification (explain why this record is necessary):",
            placeholder="We need vehicle telematics to establish whether the delivery van made unscheduled stops before reaching the warehouse..."
        )
        submit_req = st.form_submit_button("Submit Evidence Request")

    if submit_req:
        success, msg, rec = store.request_record(req_id_input, justification_input)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    if store.request_audit_log:
        st.markdown("---")
        st.markdown("#### Request Audit Trail")
        st.dataframe(store.request_audit_log, use_container_width=True)

# ==========================================
# TAB 6: Decision Submission & Rubric
# ==========================================
with tab6:
    st.subheader(" Submit Investigative Decision & Evaluation")
    st.caption("Formulate your formal finding based on verified facts, conflicts, and released evidence.")

    with st.form("decision_form"):
        st.markdown("##### 1. Primary Conclusion & Findings")
        conclusion_input = st.text_area(
            "State your conclusion regarding what occurred with PO-8841:",
            height=120,
            placeholder="Explain where the shortfall occurred, whether theft took place in transit, and the role of the courier/supplier..."
        )

        col_ev, col_cnt = st.columns(2)
        with col_ev:
            st.markdown("##### 2. Supporting Evidence IDs")
            active_list = list(store.get_active_evidence().keys())
            supp_input = st.multiselect(
                "Select supporting Evidence IDs:",
                active_list,
                default=[eid for eid in ["EVID-001", "EVID-002", "EVID-004"] if eid in active_list]
            )

        with col_cnt:
            st.markdown("##### 3. Counterevidence IDs")
            cnt_input = st.multiselect(
                "Select counterevidence or contradictory records:",
                active_list,
                default=[eid for eid in ["EVID-003"] if eid in active_list]
            )

        col_conf, col_act = st.columns([1, 2])
        with col_conf:
            st.markdown("##### 4. Confidence Level")
            conf_input = st.select_slider(
                "Confidence:",
                options=["Low", "Medium", "High"],
                value="Medium"
            )

        with col_act:
            st.markdown("##### 5. Recommended Next Action")
            act_input = st.text_input(
                "Action items:",
                placeholder="e.g. Question courier driver Surendra Pal regarding the 70-min halt at Mahadevapura garage; file police complaint for transit theft."
            )

        submit_decision = st.form_submit_button("Evaluate Decision Against Rubric", type="primary")

    if submit_decision:
        if not conclusion_input.strip():
            st.warning("Please provide a conclusion before submitting.")
        else:
            submission_payload = {
                "conclusion": conclusion_input,
                "supporting_evidence": supp_input,
                "counterevidence": cnt_input,
                "confidence": conf_input,
                "next_action": act_input
            }
            evaluation = evaluate_decision(submission_payload, store)
            attempt_record = {
                "attempt_number": len(st.session_state.decision_attempts) + 1,
                "submission": submission_payload,
                "evaluation": evaluation
            }
            st.session_state.decision_attempts.append(attempt_record)
            st.rerun()

    # Display Attempt History & Results
    if st.session_state.decision_attempts:
        st.markdown("---")
        st.subheader(" Decision Evaluation Scorecard")

        latest = st.session_state.decision_attempts[-1]
        ev = latest["evaluation"]
        sc = ev["score_breakdown"]

        c_score, c_grade = st.columns([1, 2])
        with c_score:
            st.metric("Total Score (out of 100)", f"{ev['total_score']} / 100")
        with c_grade:
            st.subheader(ev["assessment"])

        st.markdown("#### Rubric Criterion Breakdown")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.write(f"• **Evidence Grounding:** {sc['evidence_grounding']} / 25")
            st.progress(sc['evidence_grounding'] / 25)
            st.write(f"• **Contradiction Handling:** {sc['contradiction_handling']} / 25")
            st.progress(sc['contradiction_handling'] / 25)
            st.write(f"• **Confidence Calibration:** {sc['confidence_calibration']} / 20")
            st.progress(sc['confidence_calibration'] / 20)
        with col_r2:
            st.write(f"• **Counterevidence Rigor:** {sc['counterevidence_rigor']} / 15")
            st.progress(sc['counterevidence_rigor'] / 15)
            st.write(f"• **Actionability:** {sc['actionability']} / 15")
            st.progress(sc['actionability'] / 15)

        st.markdown("#### Qualitative Feedback & Improvement Areas")
        for fb in ev["feedback_points"]:
            st.write("-", fb)

        # Attempt Comparison Matrix
        if len(st.session_state.decision_attempts) > 1:
            st.markdown("---")
            st.markdown("#### Adaptive Retry & Attempt Comparison")
            comp_data = []
            for att in st.session_state.decision_attempts:
                comp_data.append({
                    "Attempt #": att["attempt_number"],
                    "Score": att["evaluation"]["total_score"],
                    "Confidence": att["submission"]["confidence"],
                    "Citations": ", ".join(att["submission"]["supporting_evidence"]),
                    "Assessment": att["evaluation"]["assessment"]
                })
            st.dataframe(comp_data, use_container_width=True)

        # Final Report Export
        st.markdown("---")
        st.subheader(" Export Final Forensic Dossier")
        report_text = f"""================================================================================
AI EVIDENCE-TO-DECISION FORENSIC INVESTIGATION REPORT
Case: Missing Electronic Modules PO-8841 (Loss Value: Rs. 5.76 Lakh)
Date Generated: {ev['timestamp']}
================================================================================

1. EXECUTIVE SUMMARY & VERIFIED FACTS:
- Order Reference: PO-8841 issued by Apex Technologies to NovaCore Electronics for 500 units NC-9020 (Rs. 18 Lakh).
- Dispatched: 500 units in 5 cartons via SwiftRoute Express on 15-Oct-2026.
- Delivered: SwiftRoute POD signed for 5 packages on 16-Oct-2026 at Peenya Warehouse.
- Discrepancy: Apex GRN-1044 recorded only 340 units received. Cartons #4 and #5 had been slit open and resealed with clear tape, missing 160 units.

2. DETECTED CONFLICTS:
- Dispatched Quantity (500 units) vs Received Quantity (340 units).
- Carrier POD marked 'Completed' only certifies 5 cardboard boxes, not the internal 500 units.
- Factory Holographic Seals vs Clear Cellophane Tape on Cartons #4 & #5.
- Address redirection email came from unverified domain (priya.sharma@apex-tech-support.com).

3. FINAL INVESTIGATOR FINDINGS (Attempt #{latest['attempt_number']}):
- Overall Score: {ev['total_score']} / 100 ({ev['assessment']})
- Primary Conclusion: {latest['submission']['conclusion']}
- Confidence Level: {latest['submission']['confidence']}
- Supporting Evidence Cites: {', '.join(latest['submission']['supporting_evidence'])}
- Counterevidence Cites: {', '.join(latest['submission']['counterevidence'])}
- Recommended Next Actions: {latest['submission']['next_action']}

4. RUBRIC PERFORMANCE:
- Evidence Grounding: {sc['evidence_grounding']} / 25
- Contradiction Handling: {sc['contradiction_handling']} / 25
- Confidence Calibration: {sc['confidence_calibration']} / 20
- Counterevidence Rigor: {sc['counterevidence_rigor']} / 15
- Actionability: {sc['actionability']} / 15

5. FORENSIC NEXT STEPS:
- Interrogate courier driver Surendra Pal regarding unauthorized 70-min stop in Mahadevapura.
- Inspect auto-garage premises near Mahadevapura Ring Road for stolen electronics stock.
- File formal cargo theft FIR with Bangalore Cyber/Crime Police against suspect transit operators.
================================================================================
"""
        st.download_button(
            label=" Download Complete Case Report (.txt)",
            data=report_text,
            file_name="investigation_report_PO-8841.txt",
            mime="text/plain"
        )

