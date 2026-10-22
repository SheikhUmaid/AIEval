import unittest
from coach import analyze_profile, generate_questions, evaluate_answers, final_report

class TestCoachApp(unittest.TestCase):
    def setUp(self):
        self.resume_text = """
        Rajesh Varma - Senior Python Backend Engineer
        Skills: Python, FastAPI, Django, PostgreSQL, Docker, Redis.
        Experience: 5 years developing scalable REST APIs and microservices.
        """
        self.job_description = """
        Looking for a Senior Python Developer with experience in REST APIs, PostgreSQL, and Kubernetes.
        """

    def test_analyze_profile(self):
        analysis = analyze_profile(self.resume_text, self.job_description)
        self.assertIsInstance(analysis, dict)
        self.assertIn("role", analysis)
        self.assertIn("match_score", analysis)
        self.assertIn("matching_skills", analysis)
        self.assertIn("missing_skills", analysis)
        print("PASS: analyze_profile returned required schema:", analysis["role"], f"Score: {analysis['match_score']}%")

    def test_generate_questions(self):
        analysis = analyze_profile(self.resume_text, self.job_description)
        questions_data = generate_questions(analysis, self.resume_text, self.job_description, num_questions=5)
        self.assertIsInstance(questions_data, dict)
        questions = questions_data.get("questions", [])
        self.assertTrue(len(questions) > 0)
        q1 = questions[0]
        self.assertIn("question", q1)
        self.assertIn("type", q1)
        self.assertIn("skill", q1)
        print(f"PASS: generate_questions generated {len(questions)} questions.")

    def test_evaluate_answers_and_final_report(self):
        analysis = analyze_profile(self.resume_text, self.job_description)
        mock_answers = [
            {
                "question": "Can you describe a challenging Python project you built?",
                "type": "project",
                "skill": "Python",
                "answer": "I architected an order processing microservice using FastAPI and PostgreSQL handling 50k transactions daily."
            },
            {
                "question": "How would you approach container orchestration with Kubernetes?",
                "type": "missing_skill",
                "skill": "Kubernetes",
                "answer": "I have used Docker containers extensively and am currently learning Kubernetes pods, deployments, and Helm charts."
            }
        ]
        evals_result = evaluate_answers(mock_answers, analysis.get("role", "Developer"))
        self.assertIsInstance(evals_result, dict)
        evals = evals_result.get("evaluations", [])
        self.assertTrue(len(evals) > 0)
        e1 = evals[0]
        self.assertIn("relevance", e1)
        self.assertIn("depth", e1)
        self.assertIn("clarity", e1)
        self.assertIn("examples", e1)
        self.assertIn("score", e1)

        # Test final report
        report = final_report(analysis, mock_answers, evals)
        self.assertIsInstance(report, dict)
        self.assertIn("strengths", report)
        self.assertIn("improvements", report)
        self.assertIn("study_plan", report)
        self.assertIn("message", report)
        print("PASS: evaluate_answers and final_report completed successfully.")

if __name__ == "__main__":
    unittest.main()

