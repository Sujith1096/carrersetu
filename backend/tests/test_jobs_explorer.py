import json
import urllib.request
import urllib.parse
import unittest

BASE_URL = "http://127.0.0.1:8000"

def get_json(path):
    req = urllib.request.Request(f"{BASE_URL}{path}", headers={"User-Agent": "TestClient/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post_json(path, data):
    encoded = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}", 
        data=encoded, 
        headers={"User-Agent": "TestClient/1.0", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

class TestLiveJobsExplorer(unittest.TestCase):
    def test_health(self):
        data = get_json("/api/health")
        self.assertEqual(data.get("status"), "healthy")

    def test_filter_options(self):
        data = get_json("/api/jobs/filters/options")
        self.assertIn("roles", data)
        self.assertIn("companies", data)
        self.assertIn("locations", data)
        self.assertIn("work_modes", data)
        self.assertTrue(len(data["roles"]) > 0)

    def test_jobs_list_and_search(self):
        data = get_json("/api/jobs?limit=5")
        self.assertIn("jobs", data)
        self.assertTrue(data["total"] > 0)
        self.assertTrue(len(data["jobs"]) <= 5)

        # Search test
        search_data = get_json("/api/jobs?search=engineer&limit=5")
        self.assertTrue(search_data["total"] > 0)

    def test_job_detail(self):
        data = get_json("/api/jobs?limit=1")
        job_id = data["jobs"][0]["id"]
        job = get_json(f"/api/jobs/{job_id}")
        self.assertEqual(job["id"], job_id)
        self.assertIn("title", job)
        self.assertIn("description", job)

    def test_companies_and_detail(self):
        data = get_json("/api/companies?limit=5")
        self.assertIn("companies", data)
        self.assertTrue(data["total"] > 0)
        comp_id = data["companies"][0]["id"]
        
        detail = get_json(f"/api/companies/{comp_id}")
        self.assertIn("company", detail)
        self.assertIn("jobs", detail)
        self.assertEqual(detail["company"]["id"], comp_id)

    def test_analyze_direct(self):
        jobs_data = get_json("/api/jobs?limit=1")
        job = jobs_data["jobs"][0]
        resume = get_json("/api/samples/resume")["resume_text"]

        report = post_json("/api/analyze/text", {
            "resume_text": resume,
            "job_title": job["title"],
            "job_company": job["company"],
            "job_description": job["description"]
        })
        self.assertIn("overall_score", report)
        self.assertTrue(0 <= report["overall_score"] <= 100)
        self.assertIn("matching_skills", report)
        self.assertIn("missing_skills", report)

if __name__ == "__main__":
    unittest.main()
