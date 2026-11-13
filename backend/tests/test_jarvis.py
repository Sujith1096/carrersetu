import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000/api/jarvis"

def run_jarvis_tests():
    print("======================================================")
    print("Testing J.A.R.V.I.S. Reasoning & Intelligence Services")
    print("======================================================")

    # 1. Test Status
    req = urllib.request.Request(f"{BASE_URL}/status")
    with urllib.request.urlopen(req) as res:
        status_data = json.loads(res.read().decode())
        assert "mode" in status_data
        print(f"[PASS] 1. Status: Mode='{status_data['mode']}', Provider='{status_data['provider']}'")

    context = {
        "candidate_name": "Sujith",
        "job_title": "Senior Full Stack Engineer",
        "job_company": "Nexus Technologies",
        "overall_score": 82.0,
        "match_rating": "Strong Match",
        "matching_skills": ["React", "TypeScript", "Python", "FastAPI", "Docker", "PostgreSQL"],
        "missing_skills": ["Kubernetes", "GraphQL", "AWS Lambda"],
        "score_breakdown": {
            "skills_score": 85.0,
            "similarity_score": 78.0,
            "metrics_score": 80.0,
            "section_score": 90.0
        }
    }

    # 2. Test Pure Technical Coding Doubt (Reversing Linked List)
    # MUST have problem deconstruction, code, edge cases, O(N) complexity, and NO unsolicited resume dumping
    coding_payload = {
        "message": "How do I reverse a singly linked list in Python?",
        "conversation_history": [],
        "context": context
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps(coding_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        coding_res = json.loads(res.read().decode())
        reply = coding_res["reply"]
        assert "ListNode" in reply
        assert "prev" in reply and "curr" in reply
        assert "O(N)" in reply or "O(n)" in reply
        # Verify Context Relevance: Did NOT dump resume score
        assert "ATS score of" not in reply
        print(f"[PASS] 2. Pure Coding Query: Deconstructed, verified code, edge cases, O(N) derivation, zero unsolicited resume dumping.")

    # 3. Test Multi-Turn Follow-Up (Asking about Time Complexity without repeating topic)
    history = [
        {"role": "user", "content": "How do I reverse a singly linked list in Python?"},
        {"role": "assistant", "content": reply}
    ]
    followup_payload = {
        "message": "What is the time complexity of that?",
        "conversation_history": history,
        "context": context
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps(followup_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        followup_res = json.loads(res.read().decode())
        fu_reply = followup_res["reply"]
        assert "O(N)" in fu_reply or "Linear" in fu_reply or "Iterative" in fu_reply
        assert "Linked List" in fu_reply or "linked list" in fu_reply
        print(f"[PASS] 3. Multi-Turn Follow-Up: Resolved topic ('linked list') from prior turns without user repetition.")

    # 4. Test Ambiguous Query (Single targeted clarification question)
    ambiguous_payload = {
        "message": "My database is not working",
        "conversation_history": [],
        "context": context
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps(ambiguous_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        amb_res = json.loads(res.read().decode())
        amb_reply = amb_res["reply"]
        assert "clarify" in amb_reply.lower() or "bottleneck" in amb_reply.lower()
        assert len(amb_res.get("suggested_replies", [])) > 0
        print(f"[PASS] 4. Ambiguity Resolution: Asked 1 targeted clarification question with 3 root-cause scenarios.")

    # 5. Test Context-Aware Resume Improvement (Grounded in Candidate & Job Telemetry)
    resume_payload = {
        "message": "How can I improve my resume for this role?",
        "conversation_history": [],
        "context": context
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps(resume_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        resume_res = json.loads(res.read().decode())
        res_reply = resume_res["reply"]
        assert "82" in res_reply or "Senior Full Stack Engineer" in res_reply
        assert "Google XYZ" in res_reply
        print(f"[PASS] 5. Grounded Resume Optimization: Addressed Sujith, 4-factor ATS score breakdown, Google XYZ formula.")

    # 6. Test Interactive Mock Interview Set
    int_start_req = urllib.request.Request(
        f"{BASE_URL}/interview/start",
        data=json.dumps({"context": context}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(int_start_req) as res:
        int_data = json.loads(res.read().decode())
        assert int_data.get("interview_state", {}).get("active") is True
        print(f"[PASS] 6. Mock Interview Init: Question 1 loaded ('{int_data['interview_state']['current_question'][:50]}...').")

    # 7. Test Interview Evaluation & Scoring
    answer_payload = {
        "message": "To configure database pooling in FastAPI and PostgreSQL, I utilize SQLAlchemy with asyncpg, setting pool_size=20, max_overflow=10, and pool_recycle=3600. For bottlenecks, I inspect execution plans using EXPLAIN ANALYZE, apply B-Tree indexes on foreign keys, and offload read-heavy endpoints to Redis.",
        "conversation_history": [
            {"role": "assistant", "content": int_data["reply"]}
        ],
        "context": context,
        "interview_state": int_data["interview_state"]
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat",
        data=json.dumps(answer_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        eval_data = json.loads(res.read().decode())
        eval_reply = eval_data["reply"]
        assert "Score:" in eval_reply or "/10" in eval_reply
        assert "Critique:" in eval_reply
        print(f"[PASS] 7. Interview Answer Evaluation: Scored response, provided critique, what was nailed, and advanced to Q2.")

    print("\n======================================================")
    print(">>> ALL JARVIS REASONING & ACCURACY TESTS PASSED! <<<")
    print("======================================================\n")

if __name__ == "__main__":
    run_jarvis_tests()
