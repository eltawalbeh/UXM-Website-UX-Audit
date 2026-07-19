from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

from backend.storage import AuditRepository


class OperatorAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {"UXM_OPERATOR_EMAIL": "operator@example.test", "UXM_OPERATOR_PASSWORD": "test-password"},
            clear=False,
        )
        self.environment.start()
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.static_root = root / "static"
        self.static_root.mkdir()
        for name in ("index.html", "login.html", "request-audit.html", "report.html", "workspace.html", "operations.html"):
            (self.static_root / name).write_text(f"<h1>{name}</h1>", encoding="utf-8")
        (self.static_root / "artifacts" / "exports").mkdir(parents=True)
        (self.static_root / "artifacts" / "exports" / "private-report.pdf").write_bytes(b"private report")
        (self.static_root / "evidence").mkdir()
        (self.static_root / "evidence" / "private-proof.png").write_bytes(b"private proof")
        (self.static_root / ".env").write_text("must-not-be-served", encoding="utf-8")
        self.repo = AuditRepository(root / "uxm-audit.db", root / "backups")
        self.repo.upsert_audit({"id": "shared_report", "client": "Public", "url": "https://example.test", "findings": []})
        from backend.api_server import create_server

        self.server = create_server(self.repo, self.static_root, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp.cleanup()
        self.environment.stop()

    def request(self, path, payload=None, headers=None):
        request = Request(
            self.base_url + path,
            data=None if payload is None else json.dumps(payload).encode("utf-8"),
            headers=headers or {},
            method="POST",
        )
        return urlopen(request)

    def login(self):
        with self.request("/api/auth/login", {"email": "operator@example.test", "password": "test-password"}, {"Content-Type": "application/json"}) as response:
            self.assertEqual(response.status, 200)
            cookie = response.headers["Set-Cookie"]
            self.assertIn("HttpOnly", cookie)
            self.assertIn("SameSite=Strict", cookie)
            self.assertNotIn("Secure", cookie)
            return cookie.split(";", 1)[0]


    def test_rejects_failed_credentials_without_issuing_a_session(self):
        with self.assertRaises(HTTPError) as raised:
            self.request("/api/auth/login", {"email": "operator@example.test", "password": "wrong"}, {"Content-Type": "application/json"})

        self.assertEqual(raised.exception.code, 401)
        self.assertIsNone(raised.exception.headers.get("Set-Cookie"))

    def test_unauthenticated_operator_workspace_and_mutation_are_protected(self):
        for path, payload in (("/workspace.html", None), ("/api/backups", {})):
            with self.subTest(path=path), self.assertRaises(HTTPError) as raised:
                if payload is None:
                    urlopen(self.base_url + path)
                else:
                    self.request(path, payload, {"Content-Type": "application/json"})
            self.assertEqual(raised.exception.code, 401)

    def test_login_session_persists_for_protected_requests_and_session_state(self):
        cookie = self.login()
        headers = {"Cookie": cookie}

        with urlopen(Request(self.base_url + "/api/auth/session", headers=headers)) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"authenticated": True})
        with self.request("/api/backups", {}, {"Content-Type": "application/json", **headers}) as response:
            self.assertEqual(response.status, 201)

    def test_loopback_http_login_cookie_is_stored_and_sent_by_a_real_cookie_jar(self):
        jar = CookieJar()
        opener = build_opener(HTTPCookieProcessor(jar))
        request = Request(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": "operator@example.test", "password": "test-password"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with opener.open(request) as response:
            self.assertEqual(response.status, 200)
            self.assertNotIn("Secure", response.headers["Set-Cookie"])
        self.assertEqual(len(jar), 1)
        with opener.open(self.base_url + "/api/audits") as response:
            self.assertEqual(response.status, 200)

    def test_non_loopback_context_keeps_the_session_cookie_secure(self):
        request = Request(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": "operator@example.test", "password": "test-password"}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Host": "operator.example.test"},
            method="POST",
        )

        with urlopen(request) as response:
            self.assertIn("Secure", response.headers["Set-Cookie"])

    def test_logout_invalidates_session_and_clears_cookie(self):
        cookie = self.login()
        headers = {"Cookie": cookie}
        with self.request("/api/auth/logout", {}, headers) as response:
            self.assertEqual(response.status, 204)
            self.assertIn("Max-Age=0", response.headers["Set-Cookie"])
        with urlopen(Request(self.base_url + "/api/auth/session", headers=headers)) as response:
            self.assertEqual(json.load(response), {"authenticated": False})
        with self.assertRaises(HTTPError) as raised:
            self.request("/api/backups", {}, {"Content-Type": "application/json", **headers})
        self.assertEqual(raised.exception.code, 401)

    def test_public_routes_and_report_remain_available_without_a_session(self):
        for path in ("/", "/login.html", "/request-audit.html", "/report.html"):
            with self.subTest(path=path), urlopen(self.base_url + path) as response:
                self.assertEqual(response.status, 200)

    def test_audit_detail_and_readiness_require_an_operator_session(self):
        for path in ("/api/audits/shared_report", "/api/audits/shared_report/readiness"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as raised:
                    urlopen(self.base_url + path)
                self.assertEqual(raised.exception.code, 401)

    def test_sensitive_static_artifacts_and_evidence_require_an_operator_session(self):
        for path in ("/artifacts/exports/private-report.pdf", "/evidence/private-proof.png"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as raised:
                    urlopen(self.base_url + path)
                self.assertEqual(raised.exception.code, 401)

    def test_environment_files_are_never_served(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen(self.base_url + "/.env")
        self.assertEqual(raised.exception.code, 404)

    def test_authenticated_operator_can_load_protected_audit_and_artifact_resources(self):
        headers = {"Cookie": self.login()}
        for path in (
            "/api/audits/shared_report",
            "/api/audits/shared_report/readiness",
            "/artifacts/exports/private-report.pdf",
            "/evidence/private-proof.png",
        ):
            with self.subTest(path=path), urlopen(Request(self.base_url + path, headers=headers)) as response:
                self.assertEqual(response.status, 200)
        with self.assertRaises(HTTPError) as raised:
            urlopen(Request(self.base_url + "/.env", headers=headers))
        self.assertEqual(raised.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
