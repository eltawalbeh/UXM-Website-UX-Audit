import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.storage import AuditRepository


class ApiServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        static_root = root / "static"
        static_root.mkdir()
        (static_root / "index.html").write_text("<h1>UXM Audit</h1>", encoding="utf-8")
        self.repo = AuditRepository(root / "uxm-audit.db", root / "backups")
        self.repo.upsert_audit({
            "id": "pilot_demo", "client": "Demo", "url": "https://example.com",
            "locale": "en", "findings": [{"id": "UXM-001"}],
        }, source="pilot")

        from backend.api_server import create_server

        self.server = create_server(self.repo, static_root, host="127.0.0.1", port=0)
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

    def request(self, path, body=b"", headers=None):
        request = Request(self.base_url + path, data=body, headers=headers or {}, method="POST")
        with urlopen(request) as response:
            return response.status, json.load(response)

    def test_lists_persisted_audits(self):
        status, audits = self.get_json("/api/audits")

        self.assertEqual(status, 200)
        self.assertEqual(audits[0]["id"], "pilot_demo")
        self.assertEqual(audits[0]["findingCount"], 1)

    def test_gets_audit_by_id(self):
        status, audit = self.get_json("/api/audits/pilot_demo")

        self.assertEqual(status, 200)
        self.assertEqual(audit["client"], "Demo")
        self.assertEqual(audit["findings"][0]["id"], "UXM-001")

    def test_creates_audit_and_returns_summary(self):
        audit = {
            "id": "workspace_demo", "client": "Workspace", "url": "https://workspace.example",
            "locale": "ar", "findings": [],
        }
        request = Request(
            self.base_url + "/api/audits", data=json.dumps(audit).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(request) as response:
            status, summary = response.status, json.load(response)

        self.assertEqual(status, 201)
        self.assertEqual(summary["id"], "workspace_demo")
        self.assertEqual(self.repo.get_audit("workspace_demo")["client"], "Workspace")

    def test_posted_full_audit_round_trips_assessments_and_findings(self):
        audit = {
            "id": "workspace_demo", "client": "Workspace", "url": "https://workspace.example",
            "locale": "en", "assessments": {"NAV-01": "issue"},
            "findings": [{"id": "UXM-007", "title": "Saved evidence", "evidence": {"alt": "Visible proof"}}],
        }
        request = Request(
            self.base_url + "/api/audits", data=json.dumps(audit).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urlopen(request) as response:
            self.assertEqual(response.status, 201)

        status, reloaded = self.get_json("/api/audits/workspace_demo")
        self.assertEqual(status, 200)
        self.assertEqual(reloaded["assessments"]["NAV-01"], "issue")
        self.assertEqual(reloaded["findings"][0]["id"], "UXM-007")
        self.assertEqual(reloaded["findings"][0]["evidence"]["alt"], "Visible proof")

    def test_creates_database_backup(self):
        request = Request(self.base_url + "/api/backups", data=b"{}", method="POST")
        with urlopen(request) as response:
            status, body = response.status, json.load(response)

        self.assertEqual(status, 201)
        self.assertTrue(body["path"].endswith(".db"))
        self.assertTrue(Path(body["path"]).exists())

    def test_uploads_png_and_attaches_generated_source_metadata_to_selected_finding(self):
        png = b"\x89PNG\r\n\x1a\nproof"

        status, evidence = self.request(
            "/api/audits/pilot_demo/findings/UXM-001/evidence?kind=source",
            png,
            {"Content-Type": "image/png", "X-Original-Filename": "capture.png", "X-Captured-At": "2026-07-14T12:00:00Z"},
        )

        self.assertEqual(status, 201)
        self.assertEqual(evidence["mimeType"], "image/png")
        self.assertEqual(evidence["capturedAt"], "2026-07-14T12:00:00Z")
        self.assertNotIn("..", evidence["filename"])
        self.assertTrue(evidence["filename"].endswith(".png"))
        stored = self.repo.get_audit("pilot_demo")["findings"][0]["evidence"]["sourceImage"]
        self.assertEqual(stored["filename"], evidence["filename"])
        self.assertTrue((self.repo.evidence_dir / evidence["filename"]).is_file())

    def test_rejects_unsafe_or_non_image_or_oversize_evidence_uploads(self):
        cases = [
            (b"\x89PNG\r\n\x1a\nproof", {"Content-Type": "image/png", "X-Original-Filename": "../proof.png"}),
            (b"not an image", {"Content-Type": "text/plain", "X-Original-Filename": "proof.txt"}),
            (b"\x89PNG\r\n\x1a\n" + b"x" * (5 * 1024 * 1024), {"Content-Type": "image/png", "X-Original-Filename": "large.png"}),
        ]
        for body, headers in cases:
            with self.subTest(headers=headers):
                request = Request(
                    self.base_url + "/api/audits/pilot_demo/findings/UXM-001/evidence?kind=source",
                    data=body, headers=headers, method="POST",
                )
                with self.assertRaises(HTTPError) as context:
                    urlopen(request)
                self.assertEqual(context.exception.code, 400)

    def test_readiness_lists_all_publication_blockers_for_publishable_findings(self):
        audit = {
            "id": "not_ready", "client": "Not ready", "url": "https://audit.example", "locale": "ar",
            "findings": [
                {"id": "UXM-010", "excludedFromPublication": True, "evidence": {"status": "pending"}},
                {"id": "UXM-011", "page": "", "journey": "", "url": "", "evidence": {"capturedAt": ""}},
            ],
        }
        self.repo.upsert_audit(audit)

        status, readiness = self.get_json("/api/audits/not_ready/readiness?locale=ar")

        self.assertEqual(status, 200)
        self.assertFalse(readiness["ready"])
        codes = {blocker["code"] for blocker in readiness["blockers"]}
        self.assertTrue({"missing_source_image", "missing_annotated_image", "missing_page", "missing_journey", "missing_url", "missing_capture_metadata", "missing_arabic_translation"}.issubset(codes))
        self.assertNotIn("excluded", codes)
        self.assertNotIn("pending_evidence", codes)

    def test_pdf_export_is_readiness_gated_and_returns_a_safe_artifact_download(self):
        calls = []
        def fake_exporter(audit_id, locale, output_path):
            calls.append((audit_id, locale, output_path))
            output_path.write_bytes(b"%PDF-1.4\nmock")

        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        from backend.api_server import create_server
        self.server = create_server(self.repo, self.temp.name, host="127.0.0.1", port=0, pdf_exporter=fake_exporter)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

        blocked_request = Request(self.base_url + "/api/audits/pilot_demo/export-pdf", data=b"{}", method="POST")
        with self.assertRaises(HTTPError) as context:
            urlopen(blocked_request)
        self.assertEqual(context.exception.code, 409)
        self.assertEqual(calls, [])

        self.repo.upsert_audit({
            "id": "pdf_ready", "client": "PDF Ready", "url": "https://example.com", "locale": "en",
            "findings": [{"id": "UXM-100", "page": "Home", "journey": "Complete", "url": "https://example.com", "evidence": {
                "capturedAt": "2026-07-14T12:00:00Z",
                "sourceImage": {"filename": "source.png"}, "annotatedImage": {"filename": "annotated.png"},
            }}],
        })
        (self.repo.evidence_dir / "source.png").write_bytes(b"source")
        (self.repo.evidence_dir / "annotated.png").write_bytes(b"annotated")
        status, exported = self.request("/api/audits/pdf_ready/export-pdf?locale=en", b"{}")

        self.assertEqual(status, 201)
        self.assertEqual(calls[0][0:2], ("pdf_ready", "en"))
        self.assertRegex(exported["filename"], r"^pdf-ready-uxm-client-report-\d{8}-\d{6}\.pdf$")
        self.assertEqual(exported["downloadUrl"], "/artifacts/exports/" + exported["filename"])
        self.assertTrue((Path(self.temp.name) / "artifacts" / "exports" / exported["filename"]).is_file())

    def test_returns_not_found_for_unknown_audit(self):
        with self.assertRaises(HTTPError) as context:
            urlopen(self.base_url + "/api/audits/missing")

        self.assertEqual(context.exception.code, 404)

    def test_serves_static_frontend(self):
        with urlopen(self.base_url + "/") as response:
            body = response.read().decode("utf-8")

        self.assertEqual(response.status, 200)
        self.assertIn("UXM Audit", body)


if __name__ == "__main__":
    unittest.main()
