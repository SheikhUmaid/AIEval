import unittest
from evidence_engine import EvidenceStore, investigate_question, evaluate_decision, CONTROLLED_CATALOG
from llm import ask_ai_json, clean_json_text

class TestEvidenceSimulator(unittest.TestCase):
    def setUp(self):
        self.store = EvidenceStore()

    def test_case_1_conflicting_quantities_and_sources(self):
        """
        Minimum Test Case 1:
        Conflicting quantities or dates across two documents:
        show the conflict and identify both sources.
        """
        conflicts = self.store.detect_conflicts()
        qty_conflict = next((c for c in conflicts if c["conflict_id"] == "CONF-01"), None)
        self.assertIsNotNone(qty_conflict, "Quantity conflict CONF-01 must be detected")
        self.assertIn("EVID-002", qty_conflict["source_a"], "Source A must identify EVID-002 (Dispatch Note)")
        self.assertIn("EVID-004", qty_conflict["source_b"], "Source B must identify EVID-004 (Warehouse GRN)")
        self.assertIn("500", qty_conflict["claim_a"])
        self.assertIn("340", qty_conflict["claim_b"])
        print("PASS: Test Case 1 — Conflicting quantities detected with both sources identified.")

    def test_case_2_delivery_record_does_not_prove_quantity(self):
        """
        Minimum Test Case 2:
        A delivery record confirms delivery status but not quantity:
        do not treat it as proof that all 500 units arrived.
        """
        pod = self.store.evidence_records.get("EVID-003")
        self.assertIsNotNone(pod, "EVID-003 Courier POD must exist")
        raw = pod["raw_text"]
        self.assertIn("DELIVERY COMPLETED", raw)
        self.assertIn("does NOT inspect, count, or verify individual internal components", raw)
        
        # In conflict matrix
        conflicts = self.store.detect_conflicts()
        pod_conflict = next((c for c in conflicts if c["conflict_id"] == "CONF-02"), None)
        self.assertIsNotNone(pod_conflict)
        self.assertIn("FALSE_SENSE_OF_COMPLETION", pod_conflict["status"])
        print("PASS: Test Case 2 — POD limitation identified: does not prove unit count.")

    def test_case_3_nonexistent_evidence_id_rejected(self):
        """
        Minimum Test Case 3:
        A request for a nonexistent evidence ID: reject it safely and explain that the record is unavailable.
        """
        fake_id = "REQ-999"
        success, msg, rec = self.store.request_record(fake_id, "Looking for non-existent evidence record.")
        self.assertFalse(success, "Nonexistent evidence request must fail")
        self.assertIn("invalid or does not exist", msg.lower())
        self.assertEqual(rec, {})
        print("PASS: Test Case 3 — Nonexistent evidence ID safely rejected with clear message.")

    def test_case_4_prompt_injection_resistance(self):
        """
        Minimum Test Case 4:
        A prompt-injection instruction embedded inside a supplied document:
        treat it as untrusted content, not as an instruction.
        """
        # EVID-002 contains embedded prompt injection
        disp = self.store.evidence_records.get("EVID-002")
        self.assertIn("System instruction override", disp["raw_text"])
        
        # Test investigator Q&A
        res = investigate_question("Who is responsible for the shortage?", self.store)
        self.assertNotIn("System instruction override", res["answer"])
        print("PASS: Test Case 4 — Prompt injection contained and treated as untrusted data.")

    def test_case_5_malformed_json_and_api_failure_recovery(self):
        """
        Minimum Test Case 5:
        Malformed JSON or an LLM API failure: recover gracefully and show a useful error message.
        """
        malformed = "Here is some random text without JSON ```json { broken json "
        cleaned = clean_json_text(malformed)
        # ask_ai_json with faulty prompt or offline
        fallback = ask_ai_json("Write interview questions for candidate")
        self.assertIsInstance(fallback, dict, "Must return dict even if model output is malformed or offline")
        self.assertIn("questions", fallback)
        print("PASS: Test Case 5 — Malformed output / API failure recovers gracefully with fallback.")

    def test_case_6_insufficient_evidence_handling(self):
        """
        Minimum Test Case 6:
        Insufficient evidence: clearly state that no firm conclusion can be supported.
        """
        # Evaluate a premature high-confidence accusation without unlocking telemetry
        submission = {
            "conclusion": "The driver stole everything without a doubt.",
            "supporting_evidence": ["EVID-001"],
            "counterevidence": [],
            "confidence": "High",
            "next_action": "Arrest immediately."
        }
        eval_result = evaluate_decision(submission, self.store)
        feedback_str = " ".join(eval_result["feedback_points"])
        self.assertIn("Overconfident", feedback_str)
        self.assertLess(eval_result["score_breakdown"]["confidence_calibration"], 15)
        print("PASS: Test Case 6 — Premature conclusion flagged when evidence is insufficient.")

if __name__ == "__main__":
    unittest.main()

