import json
import urllib.request
import urllib.parse
import urllib.error
import unittest

BASE_URL = "http://127.0.0.1:8000"

def get_json(path, headers=None):
    req_headers = {"User-Agent": "TestClient/1.0"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=req_headers)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8")), dict(resp.headers)

def post_json(path, data, headers=None):
    req_headers = {"User-Agent": "TestClient/1.0", "Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    encoded = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=encoded, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return e.code, body

class TestProductionAudit(unittest.TestCase):
    def test_health_check(self):
        status_code, data, _ = get_json("/api/health")
        self.assertEqual(status_code, 200)
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("database"), "connected")
        self.assertIn("version", data)
        self.assertIn("environment", data)

    def test_jarvis_status_security(self):
        status_code, data, _ = get_json("/api/jarvis/status")
        self.assertEqual(status_code, 200)
        self.assertIn("mode", data)
        self.assertIn("provider", data)
        # Verify secret keys are NEVER exposed in response
        self.assertNotIn("api_key", data)
        self.assertNotIn("key", data)
        self.assertIn("has_server_key", data)

    def test_jarvis_config_validation(self):
        # 1. Test short/invalid key rejection
        status_code, err = post_json("/api/jarvis/config", {
            "provider": "gemini",
            "api_key": "short_key"
        })
        self.assertEqual(status_code, 400)
        self.assertIn("too short or invalid", err.get("detail", ""))

        # 2. Test valid key format acceptance for session storage
        status_code, res = post_json("/api/jarvis/config", {
            "provider": "gemini",
            "api_key": "AIzaSyTestValidLengthKey1234567890"
        })
        self.assertEqual(status_code, 200)
        self.assertEqual(res.get("status"), "configured")

        # 3. Test clear key
        status_code, res = post_json("/api/jarvis/config", {
            "provider": "gemini",
            "api_key": ""
        })
        self.assertEqual(status_code, 200)
        self.assertEqual(res.get("status"), "reset")

    def test_jarvis_session_isolated_chat(self):
        # Verify chat functions with client session parameters
        status_code, res = post_json("/api/jarvis/chat", {
            "message": "What is time complexity of quicksort?",
            "conversation_history": [],
            "client_provider": "gemini",
            "client_api_key": ""  # Should fall back cleanly to local intelligence
        })
        self.assertEqual(status_code, 200)
        self.assertIn("reply", res)
        self.assertTrue(len(res["reply"]) > 20)

    def test_text_analysis_validation_edge_cases(self):
        # 1. Empty resume text
        status_code, err = post_json("/api/analyze/text", {
            "resume_text": "",
            "job_description": "We need a Senior Full Stack Software Engineer with Python and React."
        })
        self.assertEqual(status_code, 400)

        # 2. Resume text too short
        status_code, err = post_json("/api/analyze/text", {
            "resume_text": "Too short",
            "job_description": "We need a Senior Full Stack Software Engineer with Python and React."
        })
        self.assertEqual(status_code, 422)
        self.assertIn("too short", err.get("detail", "").lower())

        # 3. Empty job description
        status_code, err = post_json("/api/analyze/text", {
            "resume_text": "Experienced Python Software Engineer with React, Docker, and AWS skills building APIs.",
            "job_description": ""
        })
        self.assertEqual(status_code, 400)

    def test_jobs_sync_rate_limit_cooldown(self):
        # 1. First sync trigger
        status_code, res1 = post_json("/api/jobs/sync", {})
        self.assertEqual(status_code, 200)
        self.assertIn(res1.get("status"), ["success", "cached"])

        # 2. Immediate second sync trigger MUST be throttled by 60s cooldown
        status_code, res2 = post_json("/api/jobs/sync", {})
        self.assertEqual(status_code, 200)
        self.assertEqual(res2.get("status"), "cached")
        self.assertIn("rate-limit active", res2.get("message", "").lower())
        self.assertEqual(res2.get("fetched"), 0)

    def test_database_url_normalization(self):
        from app.database import RAW_DATABASE_URL
        # Ensure database URL starts with valid dialect
        from app.database import DATABASE_URL
        self.assertTrue(DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("sqlite:///"))

if __name__ == "__main__":
    unittest.main()
