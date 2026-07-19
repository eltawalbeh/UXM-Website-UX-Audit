import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.storage import AuditRepository


class AuditCopilotApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        static_root = root / "static"
        static_root.mkdir()
        (static_root / "index.html").write_text("<h1>UXM Audit</h1>", encoding="utf-8")
        self.repo = AuditRepository(root / "uxm-audit.db", root / "backups", root / "evidence")
        self.repo.upsert_audit({
            "id": "audit_demo", "client": "Demo", "url": "https://example.com", "scope": "Apply journey / desktop",
            "assessments": {"NAV-02": "issue"},
            "findings": [{"id": "UXM-001", "title": "Existing issue", "category": "navigation", "journey": "Discover", "page": "Home", "observed": "Existing wording."}],
        })
        self.calls = []

        def drafter(context):
            self.calls.append(context)
            return {"status": "ready", "draft": {
                "observation": "The selected evidence shows a label mismatch.",
                "impact": "Visitors may not identify the right destination.",
                "recommendation": "Use the visitor's task language.",
                "suggestedSeverity": "medium", "confidence": "medium",
                "missingEvidenceChecks": ["Confirm the issue on mobile."],
                "duplicateRisk": {"level": "possible", "matches": ["UXM-001"]},
            }}

        from backend.api_server import create_server
        self.server = create_server(self.repo, static_root, host="127.0.0.1", port=0, ai_drafter=drafter, require_auth=False)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp.cleanup()

    def post_json(self, path, data):
        request = Request(self.base_url + path, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def test_draft_request_uses_audit_context_and_never_persists_or_changes_scores(self):
        request = {
            "criterionId": "NAV-02", "category": "navigation", "journey": "Discover", "page": "Home",
            "notes": "The primary label says General Services while the screenshot exposes applications.",
            "evidence": {"alt": "Header navigation screenshot", "capturedAt": "2026-07-15T12:00:00Z", "sourceImage": {"path": "evidence/source.png", "mimeType": "image/png"}},
        }

        status, body = self.post_json("/api/audits/audit_demo/ai-draft", request)

        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["draft"]["suggestedSeverity"], "medium")
        self.assertEqual(self.calls[0]["scope"], "Apply journey / desktop")
        self.assertEqual(self.calls[0]["checkpoint"], "NAV-02")
        self.assertEqual(self.calls[0]["notes"], request["notes"])
        self.assertEqual(self.calls[0]["evidence"]["alt"], "Header navigation screenshot")
        self.assertEqual(self.calls[0]["existingFindings"][0]["id"], "UXM-001")
        stored = self.repo.get_audit("audit_demo")
        self.assertEqual(len(stored["findings"]), 1)
        self.assertEqual(stored["assessments"]["NAV-02"], "issue")

    def test_unavailable_ai_returns_clear_state_without_fabricated_draft(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        from backend.api_server import create_server
        self.server = create_server(self.repo, Path(self.temp.name) / "static", host="127.0.0.1", port=0, ai_drafter=lambda context: {"status": "unavailable", "message": "AI connection unavailable. Configure UXM_AI_ENDPOINT and UXM_AI_API_KEY, then try again."}, require_auth=False)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

        status, body = self.post_json("/api/audits/audit_demo/ai-draft", {"notes": "Keep this note."})

        self.assertEqual(status, 503)
        self.assertEqual(body["status"], "unavailable")
        self.assertNotIn("draft", body)
        self.assertIn("AI connection unavailable", body["message"])
        self.assertEqual(self.repo.get_audit("audit_demo")["findings"][0]["title"], "Existing issue")


if __name__ == "__main__":
    unittest.main()
