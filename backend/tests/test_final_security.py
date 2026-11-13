import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, engine
from app.models import User, AnalysisRecord, JobListing, SyncMetadata
from app.services.jarvis_engine import jarvis_engine

client = TestClient(app)

class TestFinalSecurityAndProductionReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test database sessions
        cls.db = SessionLocal()
        cls.user_a_email = f"usera_{int(datetime.utcnow().timestamp())}@example.com"
        cls.user_b_email = f"userb_{int(datetime.utcnow().timestamp())}@example.com"
        cls.password = "SecurePassword123!"

        # Register User A upfront
        reg_a = client.post("/api/auth/register", json={
            "email": cls.user_a_email,
            "password": cls.password,
            "full_name": "Alice Engineer"
        })
        cls.user_a_token = reg_a.json()["access_token"]
        cls.user_a_id = reg_a.json()["user"]["id"]

        # Register User B upfront
        reg_b = client.post("/api/auth/register", json={
            "email": cls.user_b_email,
            "password": cls.password,
            "full_name": "Bob Analyst"
        })
        cls.user_b_token = reg_b.json()["access_token"]
        cls.user_b_id = reg_b.json()["user"]["id"]

    @classmethod
    def tearDownClass(cls):
        # Clean up created test users and related records
        try:
            users = cls.db.query(User).filter(User.email.in_([cls.user_a_email, cls.user_b_email])).all()
            for u in users:
                cls.db.query(AnalysisRecord).filter(AnalysisRecord.user_id == u.id).delete()
                cls.db.delete(u)
            cls.db.commit()
        except Exception:
            cls.db.rollback()
        finally:
            cls.db.close()

    # =========================================================================
    # 1. AUTHENTICATION & AUTHORIZATION TESTS
    # =========================================================================

    def test_01_user_registration_and_login(self):
        user_c_email = f"userc_{int(datetime.utcnow().timestamp())}@example.com"
        # 1. Register User C
        reg_res = client.post("/api/auth/register", json={
            "email": user_c_email,
            "password": self.password,
            "full_name": "Charlie Tester"
        })
        self.assertEqual(reg_res.status_code, 201)
        data = reg_res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], user_c_email)
        self.assertEqual(data["user"]["full_name"], "Charlie Tester")

        # Duplicate registration rejected with 400
        dup_res = client.post("/api/auth/register", json={
            "email": user_c_email,
            "password": self.password,
            "full_name": "Charlie Duplicate"
        })
        self.assertEqual(dup_res.status_code, 400)

        # 2. Login User A
        login_res = client.post("/api/auth/login", json={
            "email": self.user_a_email,
            "password": self.password
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("access_token", login_res.json())

        # Invalid password rejected with 401
        bad_login = client.post("/api/auth/login", json={
            "email": self.user_a_email,
            "password": "WrongPassword999"
        })
        self.assertEqual(bad_login.status_code, 401)

        # 3. Demo Login test
        demo_res = client.post("/api/auth/demo-login")
        self.assertEqual(demo_res.status_code, 200)
        demo_data = demo_res.json()
        self.assertIn("access_token", demo_data)
        self.assertTrue(demo_data["user"]["is_demo"])

        # 4. /api/auth/me test
        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {self.user_a_token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], self.user_a_email)

        # Clean up user_c
        u_c = self.db.query(User).filter(User.email == user_c_email).first()
        if u_c:
            self.db.delete(u_c)
            self.db.commit()

    # =========================================================================
    # 2. HISTORY ISOLATION & PERMISSION ENFORCEMENT
    # =========================================================================

    def test_02_history_isolation_and_authorization(self):
        # 1. Anonymous user cannot access /api/history without token
        anon_res = client.get("/api/history")
        self.assertEqual(anon_res.status_code, 401)

        # 2. User A creates an analysis report
        resume_text = """
        Alice Engineer
        alice@example.com | 9876543210
        Summary: Experienced Senior Backend Engineer with Python, FastAPI, Docker, and PostgreSQL expertise.
        Experience:
        Senior Software Engineer at Alpha Tech. Architected microservices reducing latency by 45%.
        Built automated CI/CD pipelines with Kubernetes and AWS.
        Skills: Python, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, Git, CI/CD.
        """
        jd_text = """
        Target Role: Senior Backend Engineer
        Company: CloudScale Systems
        Requirements: Python, FastAPI, PostgreSQL, Docker, Redis, Kubernetes.
        """

        analysis_res = client.post(
            "/api/analyze/text",
            headers={"Authorization": f"Bearer {self.user_a_token}"},
            json={
                "resume_text": resume_text,
                "job_description": jd_text,
                "job_title": "Senior Backend Engineer",
                "job_company": "CloudScale Systems",
                "file_name": "alice_resume.txt"
            }
        )
        self.assertEqual(analysis_res.status_code, 200)
        report_data = analysis_res.json()
        report_id = report_data.get("id")
        self.assertIsNotNone(report_id)

        # 3. User A queries /api/history -> must see report_id
        hist_a = client.get("/api/history", headers={"Authorization": f"Bearer {self.user_a_token}"})
        self.assertEqual(hist_a.status_code, 200)
        history_a_list = hist_a.json()
        user_a_record_ids = [item["id"] for item in history_a_list]
        self.assertIn(report_id, user_a_record_ids)

        # 4. User B queries /api/history -> MUST NOT see User A's report!
        hist_b = client.get("/api/history", headers={"Authorization": f"Bearer {self.user_b_token}"})
        self.assertEqual(hist_b.status_code, 200)
        history_b_list = hist_b.json()
        user_b_record_ids = [item["id"] for item in history_b_list]
        self.assertNotIn(report_id, user_b_record_ids)

        # 5. User B attempts GET /api/history/{report_id} of User A's report -> HTTP 403 Forbidden!
        unauthorized_view = client.get(
            f"/api/history/{report_id}",
            headers={"Authorization": f"Bearer {self.user_b_token}"}
        )
        self.assertEqual(unauthorized_view.status_code, 403)
        self.assertIn("Access forbidden", unauthorized_view.json().get("detail", ""))

        # 6. User B attempts DELETE /api/history/{report_id} of User A's report -> HTTP 403 Forbidden!
        unauthorized_delete = client.delete(
            f"/api/history/{report_id}",
            headers={"Authorization": f"Bearer {self.user_b_token}"}
        )
        self.assertEqual(unauthorized_delete.status_code, 403)
        self.assertIn("Access forbidden", unauthorized_delete.json().get("detail", ""))

        # 7. User B calls DELETE /api/history (bulk clear) -> does NOT touch User A's record
        bulk_del_b = client.delete(
            "/api/history",
            headers={"Authorization": f"Bearer {self.user_b_token}"}
        )
        self.assertEqual(bulk_del_b.status_code, 200)

        # User A's report is still intact!
        hist_a_after = client.get(
            f"/api/history/{report_id}",
            headers={"Authorization": f"Bearer {self.user_a_token}"}
        )
        self.assertEqual(hist_a_after.status_code, 200)
        self.assertEqual(hist_a_after.json()["id"], report_id)

        # 8. User A deletes their own record -> succeeds
        del_a = client.delete(
            f"/api/history/{report_id}",
            headers={"Authorization": f"Bearer {self.user_a_token}"}
        )
        self.assertEqual(del_a.status_code, 200)

    # =========================================================================
    # 3. DASHBOARD STATS ISOLATION & GUEST PRIVACY
    # =========================================================================

    def test_03_dashboard_stats_isolation(self):
        # 1. Unauthenticated guest accessing /api/stats receives clean empty response (no personal data leaked)
        guest_stats = client.get("/api/stats")
        self.assertEqual(guest_stats.status_code, 200)
        data_guest = guest_stats.json()
        self.assertEqual(data_guest["total_analyses"], 0)
        self.assertEqual(data_guest["recent_history"], [])
        self.assertEqual(data_guest["average_score"], 0.0)

        # 2. User A creates a private analysis record
        client.post(
            "/api/analyze/text",
            headers={"Authorization": f"Bearer {self.user_a_token}"},
            json={
                "resume_text": "Alice Private Resume with Python and Docker",
                "job_description": "Looking for Python Engineer",
                "job_title": "Python Engineer",
                "job_company": "Secret Corp",
                "file_name": "alice_private.txt"
            }
        )

        # 3. User A queries /api/stats -> sees User A's private analysis
        stats_a = client.get("/api/stats", headers={"Authorization": f"Bearer {self.user_a_token}"})
        self.assertEqual(stats_a.status_code, 200)
        data_a = stats_a.json()
        self.assertGreaterEqual(data_a["total_analyses"], 1)
        self.assertTrue(any(item["job_company"] == "Secret Corp" for item in data_a["recent_history"]))

        # 4. Guest queries /api/stats -> STILL sees 0 records and NEVER sees User A's report!
        guest_stats_after = client.get("/api/stats")
        self.assertEqual(guest_stats_after.status_code, 200)
        self.assertEqual(guest_stats_after.json()["total_analyses"], 0)
        self.assertEqual(guest_stats_after.json()["recent_history"], [])

        # 5. User B queries /api/stats -> total_analyses == 0, never sees User A's report!
        stats_b = client.get("/api/stats", headers={"Authorization": f"Bearer {self.user_b_token}"})
        self.assertEqual(stats_b.status_code, 200)
        data_b = stats_b.json()
        self.assertEqual(data_b["total_analyses"], 0)
        self.assertEqual(data_b["recent_history"], [])

    # =========================================================================
    # 4. JARVIS AI PROVIDER VALIDATION & SESSION ISOLATION
    # =========================================================================

    def test_04_jarvis_provider_validation_and_session_isolation(self):
        # 1. Config validation rejects unsupported provider with HTTP 400
        res_bad_provider = client.post("/api/jarvis/config", json={
            "provider": "unsupported_provider_xyz",
            "api_key": "valid_length_key_1234567890"
        })
        self.assertEqual(res_bad_provider.status_code, 400)
        self.assertIn("Unsupported AI provider", res_bad_provider.json().get("detail", ""))

        # 2. Config validation rejects short key with HTTP 400
        res_short_key = client.post("/api/jarvis/config", json={
            "provider": "gemini",
            "api_key": "short"
        })
        self.assertEqual(res_short_key.status_code, 400)
        self.assertIn("too short", res_short_key.json().get("detail", ""))

        # 3. Config validation succeeds for valid provider & key format
        res_ok_config = client.post("/api/jarvis/config", json={
            "provider": "gemini",
            "api_key": "AIzaSyFakeKeyForSessionTesting12345678"
        })
        self.assertEqual(res_ok_config.status_code, 200)
        self.assertEqual(res_ok_config.json()["status"], "configured")
        # Global server state must NOT have stored this key
        self.assertIsNone(jarvis_engine.custom_api_key)

        # 4. Interview start rejects unsupported provider
        res_interview_bad = client.post("/api/jarvis/interview/start", json={
            "client_provider": "claude",
            "client_api_key": "fake_key_1234567890123456"
        })
        self.assertEqual(res_interview_bad.status_code, 400)

        # 5. Interview start with valid provider selection works
        res_interview_ok = client.post("/api/jarvis/interview/start", json={
            "context": {"job_title": "Frontend Engineer", "candidate_name": "Test Candidate"},
            "client_provider": "gemini",
            "client_api_key": "fake_key_for_offline_test"
        })
        self.assertEqual(res_interview_ok.status_code, 200)
        data = res_interview_ok.json()
        self.assertIn("reply", data)
        self.assertIsNotNone(data.get("interview_state"))
        self.assertTrue(data["interview_state"]["active"])

        # 6. Global server state check: personal credentials never persist globally
        self.assertIsNone(jarvis_engine.custom_api_key)

    # =========================================================================
    # 5. DATABASE RESILIENCE & HEALTH ENDPOINT (HTTP 503 ON FAILURE)
    # =========================================================================

    def test_05_health_endpoint_healthy_and_503_on_failure(self):
        # 1. Normal state: healthy 200
        health_res = client.get("/api/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertEqual(health_res.json()["status"], "healthy")
        self.assertEqual(health_res.json()["database"], "connected")

        # 2. Simulated critical database disconnection
        with patch.object(engine, "connect", side_effect=Exception("Database connection timeout")):
            down_res = client.get("/api/health")
            self.assertEqual(down_res.status_code, 503)
            down_data = down_res.json()
            self.assertEqual(down_data["status"], "unhealthy")
            self.assertIn("Critical database connectivity failure", down_data["error"])

    # =========================================================================
    # 6. JOBS EXPLORER EXPIRY & PERSISTENT SYNC COOLDOWN
    # =========================================================================

    def test_06_jobs_sync_persistent_cooldown_and_expiry(self):
        # 1. Direct call to sync
        sync_res = client.post("/api/jobs/sync")
        self.assertEqual(sync_res.status_code, 200)
        sync_data = sync_res.json()
        self.assertIn(sync_data["status"], ["success", "cached"])

        # 2. Calling sync immediately again triggers persistent rate limiting
        second_sync = client.post("/api/jobs/sync")
        self.assertEqual(second_sync.status_code, 200)
        second_data = second_sync.json()
        self.assertEqual(second_data["status"], "cached")
        self.assertIn("cooldown: 60s", second_data["message"])

        # 3. Verify SyncMetadata table record exists in DB
        db = SessionLocal()
        try:
            meta = db.query(SyncMetadata).filter(SyncMetadata.id == "jobs_sync").first()
            self.assertIsNotNone(meta)
            self.assertIsNotNone(meta.last_sync_time)

            # 4. Expiry detection test
            # Create a mock expired job
            expired_job_id = f"test_expired_{int(datetime.utcnow().timestamp())}"
            exp_job = JobListing(
                id=expired_job_id,
                title="Expired Test Job",
                company="Old Corp",
                description="Testing vacancy expiry logic",
                location="Remote",
                url="https://example.com/expired",
                expires_at=datetime.utcnow() - timedelta(days=2),
                is_active=True,
                is_demo=False
            )
            db.add(exp_job)
            db.commit()

            # Reset sync_meta timestamp to allow sync run
            meta.last_sync_time = datetime.utcnow() - timedelta(seconds=120)
            db.commit()

            # Run sync again
            third_sync = client.post("/api/jobs/sync")
            self.assertEqual(third_sync.status_code, 200)

            # Verify the job is now deactivated (is_active = False)
            db.refresh(exp_job)
            self.assertFalse(exp_job.is_active)

            # Clean up mock job
            db.delete(exp_job)
            db.commit()
        finally:
            db.close()

    # =========================================================================
    # 7. JWT SECRET PRODUCTION ENFORCEMENT & DEV FALLBACK
    # =========================================================================

    def test_07_jwt_secret_production_enforcement(self):
        from app.services.auth import get_jwt_secret

        # 1. Missing secret in production raises RuntimeError
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "JWT_SECRET": ""}, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                get_jwt_secret()
            self.assertIn("JWT_SECRET environment variable is missing", str(ctx.exception))

        # 2. Too short secret in production raises RuntimeError (<32 chars)
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "JWT_SECRET": "too_short_key"}, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                get_jwt_secret()
            self.assertIn("JWT_SECRET environment variable is missing", str(ctx.exception))

        # 3. Valid production secret succeeds (>= 32 chars)
        prod_secret = "a_super_secure_production_secret_key_1234567890"
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "JWT_SECRET": prod_secret}, clear=False):
            self.assertEqual(get_jwt_secret(), prod_secret)

        # 4. In development mode without explicit key, dev fallback key is returned safely
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "JWT_SECRET": "", "RENDER": ""}, clear=False):
            dev_key = get_jwt_secret()
            self.assertTrue(len(dev_key) >= 32)
            self.assertIn("dev_", dev_key)

    # =========================================================================
    # 8. ALEMBIC FRESH DATABASE BASELINE & IDEMPOTENCY
    # =========================================================================

    def test_08_alembic_fresh_database_baseline(self):
        import sqlite3
        from alembic.config import Config
        from alembic import command
        from app.database import init_db

        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_db_path = os.path.join(backend_dir, "test_alembic_fresh_baseline.db")
        clean_url_path = temp_db_path.replace("\\", "/")
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

        try:
            # 1. Run Alembic upgrade head on completely fresh, empty database
            alembic_cfg_path = os.path.join(backend_dir, "alembic.ini")
            cfg = Config(alembic_cfg_path)
            cfg.set_main_option("sqlalchemy.url", f"sqlite:///{clean_url_path}")
            command.upgrade(cfg, "head")

            # 2. Verify all 5 tables are created
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]

            self.assertIn("users", tables)
            self.assertIn("company_profiles", tables)
            self.assertIn("job_listings", tables)
            self.assertIn("analysis_records", tables)
            self.assertIn("sync_metadata", tables)
            self.assertIn("alembic_version", tables)

            # 3. Verify job_listings required columns
            cursor.execute("PRAGMA table_info(job_listings)")
            cols = [r[1] for r in cursor.fetchall()]
            self.assertIn("is_demo", cols)
            self.assertIn("last_synced_at", cols)
            self.assertIn("expires_at", cols)

            conn.close()

            # 4. Verify init_db() executes safely without conflicts or wiping records
            init_db()

        finally:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)


if __name__ == "__main__":
    unittest.main()
