import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.storage import AuditRepository


class RequestAuditApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.static_root = root / "static"
        self.static_root.mkdir()
        self.repo = AuditRepository(root / "uxm-audit.db", root / "backups")
        from backend.api_server import create_server
        self.server = create_server(self.repo, self.static_root, host="127.0.0.1", port=0, require_auth=False)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        self.payload = {
            "name": "Lina Haddad",
            "email": "lina@example.com",
            "company": "Example Organization",
            "website": "https://example.com/service",
            "service": "UX audit",
            "scopeNote": "Review the public service application journey.",
            "preferredContact": "Email",
            "locale": "en",
        }

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp.cleanup()

    def request(self, path, payload, *, headers=None):
        request = Request(self.base_url + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
        with urlopen(request) as response:
            return response.status, json.load(response)

    def get_json(self, path):
        with urlopen(self.base_url + path) as response:
            return response.status, json.load(response)

    def test_public_submission_persists_validated_request_without_creating_audit(self):
        status, response = self.request("/api/request-audits", self.payload)

        self.assertEqual(status, 202)
        self.assertEqual(response["status"], "received")
        self.assertNotIn("requestId", response)
        self.assertEqual(self.repo.list_audits(), [])
        requests = self.repo.list_request_audits()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["email"], "lina@example.com")
        self.assertEqual(requests[0]["status"], "received")

    def test_public_submission_rejects_missing_required_fields_and_invalid_url(self):
        invalid = {**self.payload, "name": "", "email": "invalid", "website": "not-a-url", "service": "", "preferredContact": ""}

        with self.assertRaises(HTTPError) as raised:
            self.request("/api/request-audits", invalid)

        self.assertEqual(raised.exception.code, 400)
        error = json.load(raised.exception)["error"]
        self.assertIn("Name", error)
        self.assertEqual(self.repo.list_request_audits(), [])

    def test_duplicate_and_honeypot_submission_do_not_create_extra_intake(self):
        first_status, first = self.request("/api/request-audits", self.payload)
        duplicate_status, duplicate = self.request("/api/request-audits", self.payload)
        spam_status, spam = self.request("/api/request-audits", {**self.payload, "contactWebsite": "https://bot.example"})

        self.assertEqual(first_status, 202)
        self.assertEqual(duplicate_status, 202)
        self.assertEqual(spam_status, 202)
        self.assertEqual(first, duplicate)
        self.assertEqual(duplicate, spam)
        self.assertNotIn("requestId", first)
        self.assertEqual(len(self.repo.list_request_audits()), 1)

    def test_public_submission_rejects_oversized_json_body(self):
        with self.assertRaises(HTTPError) as raised:
            self.request("/api/request-audits", {**self.payload, "scopeNote": "x" * (65 * 1024)})

        self.assertEqual(raised.exception.code, 413)

    def test_public_submission_throttles_excess_requests_with_a_neutral_error(self):
        for index in range(5):
            status, _ = self.request("/api/request-audits", {**self.payload, "email": f"lina{index}@example.com"})
            self.assertEqual(status, 202)

        with self.assertRaises(HTTPError) as raised:
            self.request("/api/request-audits", {**self.payload, "email": "limited@example.com"})

        self.assertEqual(raised.exception.code, 429)
        self.assertEqual(json.load(raised.exception), {"error": "Please try again later."})

    def test_operator_can_explicitly_convert_received_request_once_without_ai_first_pass(self):
        self.request("/api/request-audits", self.payload)
        status, queue = self.get_json("/api/request-audits")

        self.assertEqual(status, 200)
        request_id = queue[0]["id"]
        status, converted = self.request(f"/api/request-audits/{request_id}/create-audit", {})
        self.assertEqual(status, 201)
        self.assertEqual(converted["request"]["status"], "converted")
        self.assertEqual(converted["audit"]["status"], "draft")
        self.assertEqual(converted["audit"]["findings"], [])
        self.assertNotIn("aiFirstPass", converted["audit"])
        self.assertEqual(converted["client"]["phone"], "")
        self.assertIn("Preferred contact: Email", converted["client"]["notes"])
        self.assertEqual(len(self.repo.list_clients()), 1)
        self.assertEqual(len(self.repo.list_projects()), 1)
        self.assertEqual(len(self.repo.list_audits()), 1)

        with self.assertRaises(HTTPError) as raised:
            self.request(f"/api/request-audits/{request_id}/create-audit", {})
        self.assertEqual(raised.exception.code, 409)

    def test_concurrent_request_conversion_creates_one_client_project_and_audit(self):
        created, duplicate = self.repo.create_audit_request(self.payload)
        self.assertFalse(duplicate)
        barrier = threading.Barrier(2)
        successes, failures = [], []

        def convert():
            try:
                barrier.wait(timeout=5)
                successes.append(self.repo.convert_audit_request(created["id"]))
            except Exception as error:
                failures.append(error)

        threads = [threading.Thread(target=convert) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], ValueError)
        self.assertEqual(len(self.repo.list_clients()), 1)
        self.assertEqual(len(self.repo.list_projects()), 1)
        self.assertEqual(len(self.repo.list_audits()), 1)


if __name__ == "__main__":
    unittest.main()
