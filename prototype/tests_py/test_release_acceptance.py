"""Release-hardening acceptance coverage against an isolated real HTTP server."""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from backend.api_server import create_server
from backend.storage import AuditRepository


PNG = b"\x89PNG\r\n\x1a\nrelease-proof"


class ReleaseAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.static_root = Path(__file__).resolve().parents[1]
        self.repository = AuditRepository(self.root / "audits.db", self.root / "backups", self.root / "evidence")
        self.audit = {
            "id": "release_demo",
            "client": "Release Demo",
            "url": "https://release.example/service",
            "locale": "en",
            "assessments": {"NAV-01": "pass"},
            "findings": [{
                "id": "UXM-901", "severity": "high", "category": "usability",
                "page": "Service", "journey": "Complete", "url": "https://release.example/service",
                "title": "Required field guidance is unclear", "observed": "The form does not identify required input before submission.",
                "impact": "People can abandon a failed submission.", "recommendation": "Mark required fields before data entry.",
                "evidence": {"alt": "Service form missing required indicators"},
            }],
        }
        self.repository.upsert_audit(self.audit, source="pilot")
        self.server = create_server(self.repository, self.static_root, host="127.0.0.1", port=0, require_auth=False)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp.cleanup()

    def get_json(self, path):
        with urlopen(self.base_url + path) as response:
            return response.status, json.load(response)

    def post(self, path, body, headers=None):
        request = Request(self.base_url + path, data=body, headers=headers or {}, method="POST")
        with urlopen(request) as response:
            return response.status, json.load(response)

    def test_persist_edit_reload_evidence_ready_report_and_backup_release_path(self):
        status, audits = self.get_json("/api/audits")
        self.assertEqual(status, 200)
        self.assertEqual(audits[0]["id"], "release_demo")

        status, selected = self.get_json("/api/audits/release_demo")
        self.assertEqual(status, 200)
        selected["assessments"]["NAV-01"] = "issue"
        selected["findings"] = []
        self.assertEqual(self.post("/api/audits", json.dumps(selected).encode(), {"Content-Type": "application/json"})[0], 201)

        _, reloaded = self.get_json("/api/audits/release_demo")
        self.assertEqual(reloaded["assessments"]["NAV-01"], "issue")
        for kind in ("source", "annotated"):
            status, attachment = self.post(
                f"/api/audits/release_demo/findings/UXM-901/evidence?kind={kind}", PNG,
                {"Content-Type": "image/png", "X-Original-Filename": f"{kind}.png", "X-Captured-At": "2026-07-14T12:00:00Z"},
            )
            self.assertEqual(status, 201)
            self.assertTrue((self.repository.evidence_dir / attachment["filename"]).is_file())

        # Uploading files alone is not a publication claim; an operator makes
        # the explicit, truthful completion decision after both are persisted.
        finding = self.repository.get_audit("release_demo")["findings"][0]
        finding["evidence"] |= {"capture": {"device": "Desktop Chrome"}, "capturedAt": "2026-07-14T12:00:00Z"}
        self.repository.upsert_audit(self.repository.get_audit("release_demo") | {"findings": [finding]})
        self.assertEqual(self.post("/api/audits/release_demo/findings/UXM-901/evidence-complete", b'{"evidenceComplete":true}', {"Content-Type": "application/json"})[0], 200)

        _, readiness = self.get_json("/api/audits/release_demo/readiness")
        self.assertTrue(readiness["ready"], readiness["blockers"])
        with urlopen(self.base_url + "/report.html?audit=release_demo") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b'id="report-app"', response.read())

        status, backup = self.post("/api/backups", b"{}")
        self.assertEqual(status, 201)
        self.assertTrue(Path(backup["path"]).is_file())
        self.assertEqual(AuditRepository(Path(backup["path"]), self.root / "verified-backups").get_audit("release_demo")["assessments"]["NAV-01"], "issue")

    def test_workspace_keeps_backup_api_out_of_the_primary_header(self):
        workspace = self.static_root / "app.js"
        source = workspace.read_text(encoding="utf-8")

        self.assertNotIn('data-action="backup"', source)
        self.assertNotIn("/api/backups", source)
        self.assertNotIn("Create backup", source)

    def test_workspace_uses_design_system_selects_upload_controls_and_direct_pdf_export(self):
        source = (self.static_root / "app.js").read_text(encoding="utf-8")
        css = (self.static_root / "styles.css").read_text(encoding="utf-8")

        self.assertIn('class="form-field"', source)
        self.assertIn('class="file-upload"', source)
        self.assertIn('data-action="export-pdf"', source)
        self.assertIn('/export-pdf', source)
        self.assertIn('.form-select', css)
        self.assertIn('.file-upload-button', css)


if __name__ == "__main__":
    unittest.main()
