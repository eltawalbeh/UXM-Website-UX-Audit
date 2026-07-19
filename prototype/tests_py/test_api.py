import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.storage import AuditRepository, EvidenceCompletionConflict


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

        self.server = create_server(self.repo, static_root, host="127.0.0.1", port=0, require_auth=False)
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

    def test_posted_audit_round_trips_assessments_without_writing_findings(self):
        audit = {
            "id": "workspace_demo", "client": "Workspace", "url": "https://workspace.example",
            "locale": "en", "assessments": {"NAV-01": "issue"}, "findings": [],
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
        self.assertEqual(reloaded["findings"], [])

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

    def test_evidence_upload_normalizes_the_operator_selected_timestamp_and_rejects_invalid_timestamps_before_persisting(self):
        png = b"\x89PNG\r\n\x1a\nproof"
        status, evidence = self.request(
            "/api/audits/pilot_demo/findings/UXM-001/evidence?kind=source",
            png,
            {"Content-Type": "image/png", "X-Original-Filename": "capture.png", "X-Captured-At": "2026-07-14T15:00:00+03:00"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(evidence["capturedAt"], "2026-07-14T12:00:00Z")
        stored = self.repo.get_audit("pilot_demo")["findings"][0]["evidence"]
        self.assertEqual(stored["capturedAt"], "2026-07-14T12:00:00Z")

        with self.assertRaises(HTTPError) as rejected:
            self.request(
                "/api/audits/pilot_demo/findings/UXM-001/evidence?kind=annotated",
                png,
                {"Content-Type": "image/png", "X-Original-Filename": "annotated.png", "X-Captured-At": "2026-07-14T12:00:00"},
            )
        self.assertEqual(rejected.exception.code, 400)
        persisted = self.repo.get_audit("pilot_demo")["findings"][0]["evidence"]
        self.assertNotIn("annotatedImage", persisted)

    def test_invalid_persisted_capture_timestamp_cannot_complete_evidence(self):
        self.repo.upsert_audit({
            "id": "invalid_capture", "client": "Invalid capture", "url": "https://example.com", "locale": "en",
            "findings": [{"id": "UXM-INVALID", "evidence": {
                "capturedAt": "2026-07-14T12:00:00", "capture": {"device": "Desktop Chrome"},
                "sourceImage": {"filename": "source.png"}, "annotatedImage": {"filename": "annotated.png"},
            }}],
        })
        (self.repo.evidence_dir / "source.png").write_bytes(b"source")
        (self.repo.evidence_dir / "annotated.png").write_bytes(b"annotated")

        with self.assertRaises(HTTPError) as rejected:
            self.request(
                "/api/audits/invalid_capture/findings/UXM-INVALID/evidence-complete",
                json.dumps({"evidenceComplete": True}).encode(), {"Content-Type": "application/json"},
            )

        self.assertEqual(rejected.exception.code, 400)
        persisted = self.repo.get_audit("invalid_capture")["findings"][0]
        self.assertNotEqual(persisted["evidence"].get("status"), "complete")
        self.assertNotIn("evidenceComplete", persisted)

    def test_completion_conflicts_when_an_attachment_is_replaced_after_its_decision_started(self):
        png = b"\x89PNG\r\n\x1a\nproof"
        self.request("/api/audits/pilot_demo/findings/UXM-001/evidence?kind=source", png,
                     {"Content-Type": "image/png", "X-Original-Filename": "source.png", "X-Captured-At": "2026-07-14T12:00:00Z"})
        self.request("/api/audits/pilot_demo/findings/UXM-001/evidence?kind=annotated", png,
                     {"Content-Type": "image/png", "X-Original-Filename": "annotated.png", "X-Captured-At": "2026-07-14T12:00:00Z"})

        baseline_read, allow_completion, outcome = threading.Event(), threading.Event(), []
        original_get_audit = self.repo.get_audit
        wait_for_first_snapshot = [True]

        def snapshot_then_wait(audit_id):
            snapshot = original_get_audit(audit_id)
            if wait_for_first_snapshot[0]:
                wait_for_first_snapshot[0] = False
                baseline_read.set()
                self.assertTrue(allow_completion.wait(2), "completion did not wait for the concurrent replacement")
            return snapshot

        self.repo.get_audit = snapshot_then_wait
        def complete():
            try:
                outcome.append(self.request(
                    "/api/audits/pilot_demo/findings/UXM-001/evidence-complete",
                    json.dumps({"evidenceComplete": True}).encode(), {"Content-Type": "application/json"},
                ))
            except HTTPError as error:
                outcome.append((error.code, json.load(error)))

        completion = threading.Thread(target=complete)
        completion.start()
        self.assertTrue(baseline_read.wait(2), "completion did not capture its evidence decision")
        self.request("/api/audits/pilot_demo/findings/UXM-001/evidence?kind=annotated", b"\x89PNG\r\n\x1a\nreplacement",
                     {"Content-Type": "image/png", "X-Original-Filename": "replacement.png", "X-Captured-At": "2026-07-14T12:00:00Z"})
        allow_completion.set()
        completion.join(2)
        self.repo.get_audit = original_get_audit

        self.assertEqual(outcome[0][0], 409)
        self.assertEqual(outcome[0][1]["error"], "Evidence changed while completion was pending; review and confirm it again")
        persisted = original_get_audit("pilot_demo")["findings"][0]
        self.assertEqual(persisted["evidence"]["annotatedImage"]["originalFilename"], "replacement.png")
        self.assertEqual(persisted["evidence"]["status"], "draft")
        self.assertNotIn("evidenceComplete", persisted)

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
        self.server = create_server(self.repo, self.temp.name, host="127.0.0.1", port=0, pdf_exporter=fake_exporter, require_auth=False)
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
                "capturedAt": "2026-07-14T12:00:00Z", "status": "complete",
                "sourceImage": {"filename": "source.png"}, "annotatedImage": {"filename": "annotated.png"},
            }, "evidenceComplete": True}],
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
    def test_client_project_management_api_creates_links_and_updates_status(self):
        status, client = self.request("/api/clients", json.dumps({"name": "API Client", "contactName": "Lina"}).encode("utf-8"), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)
        status, project = self.request("/api/projects", json.dumps({"clientId": client["id"], "name": "Website", "baseUrl": "https://example.com", "owner": "Abdullah"}).encode("utf-8"), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)

        status, linked = self.request(f"/api/projects/{project['id']}/audits/pilot_demo", b"{}", {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(linked["projectId"], project["id"])
        status, updated = self.request(f"/api/projects/{project['id']}/status", json.dumps({"status": "ready_for_client"}).encode("utf-8"), {"Content-Type": "application/json"})
        self.assertEqual(updated["status"], "ready_for_client")

        _, clients = self.get_json("/api/clients")
        _, projects = self.get_json(f"/api/projects?clientId={client['id']}")
        self.assertEqual(clients[0]["auditCount"], 1)
        self.assertEqual(projects[0]["auditCount"], 1)
    def test_template_api_creates_a_clean_project_linked_audit(self):
        status, templates = self.get_json("/api/audit-templates")
        self.assertEqual(status, 200)
        government = next(item for item in templates if item["id"] == "government-civic-v1")
        client = self.repo.create_client({"name": "Template Client"})
        project = self.repo.create_project({"clientId": client["id"], "name": "Service Portal", "baseUrl": "https://service.example.gov/", "productType": "government_civic"})

        status, audit = self.request(
            f"/api/projects/{project['id']}/audits/from-template",
            json.dumps({"templateId": government["id"], "title": "Service Portal Baseline"}).encode(),
        )

        self.assertEqual(status, 201)
        self.assertEqual(audit["projectId"], project["id"])
        self.assertEqual(audit["templateId"], government["id"])
        self.assertEqual(audit["url"], project["baseUrl"])
        self.assertEqual(audit["source"], f"template:{government['id']}")
        self.assertEqual(set(audit["assessments"]), set(government["checkpointIds"]))
        self.assertEqual(set(audit["assessments"].values()), {"not_verified"})
        self.assertEqual(audit["findings"], [])
        self.assertEqual(audit["journeys"], government["journeys"])
        self.assertEqual(audit["scope"]["bundle"], government["defaultBundle"])
        self.assertEqual(self.repo.list_projects(client["id"])[0]["auditCount"], 1)

    def test_template_creation_rejects_unknown_template_without_creating_an_audit(self):
        client = self.repo.create_client({"name": "Unknown Template Client"})
        project = self.repo.create_project({"clientId": client["id"], "name": "Portal", "baseUrl": "https://example.com"})
        before = len(self.repo.list_audits())
        with self.assertRaises(HTTPError) as raised:
            self.request(
                f"/api/projects/{project['id']}/audits/from-template",
                json.dumps({"templateId": "not-real"}).encode(),
            )
        self.assertEqual(raised.exception.code, 404)
        body = json.load(raised.exception)
        self.assertIn("template", body["error"].lower())
        self.assertEqual(len(self.repo.list_audits()), before)

    def test_operator_finding_draft_and_explicit_evidence_completion_are_separate_api_actions(self):
        draft = {
            "id": "UXM-EDITOR", "checkpoint": "NAV-02", "url": "https://example.com/pricing", "page": "Pricing",
            "journey": "Understand", "severity": "high", "effort": "medium", "title": "Plan limits are unclear",
            "observed": "Plan labels omit the limits.", "impact": "Buyers cannot compare plans.",
            "recommendation": "Show limits beside each plan.",
            "evidence": {"alt": "Mobile pricing table", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Mobile Safari"}},
        }
        status, saved = self.request("/api/audits/pilot_demo/findings", json.dumps(draft).encode(), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)
        self.assertEqual(saved["evidence"]["status"], "draft")

        with self.assertRaises(HTTPError) as blocked:
            self.request("/api/audits/pilot_demo/findings/UXM-EDITOR/evidence-complete", json.dumps({"evidenceComplete": True}).encode(), {"Content-Type": "application/json"})
        self.assertEqual(blocked.exception.code, 400)

        for kind in ("source", "annotated"):
            self.request(f"/api/audits/pilot_demo/findings/UXM-EDITOR/evidence?kind={kind}", b"\x89PNG\r\n\x1a\nproof", {"Content-Type": "image/png", "X-Original-Filename": f"{kind}.png", "X-Captured-At": "2026-07-19T10:30:00Z"})
        status, complete = self.request("/api/audits/pilot_demo/findings/UXM-EDITOR/evidence-complete", json.dumps({"evidenceComplete": True}).encode(), {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertTrue(complete["evidenceComplete"])
        self.assertEqual(complete["evidence"]["status"], "complete")

    def test_cross_finding_attachment_metadata_cannot_complete_new_finding_evidence(self):
        owner = {
            "id": "UXM-OWNER", "checkpoint": "NAV-02", "url": "https://example.com/owner", "page": "Owner",
            "journey": "Understand", "severity": "high", "effort": "medium", "title": "Owner evidence finding",
            "observed": "This finding owns the uploaded proof.", "impact": "Proof must not be borrowable.",
            "recommendation": "Keep attachment ownership with its finding.",
            "evidence": {"alt": "Owner evidence on the pricing page", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Desktop Chrome"}},
        }
        status, _ = self.request("/api/audits/pilot_demo/findings", json.dumps(owner).encode(), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)
        for kind in ("source", "annotated"):
            self.request(f"/api/audits/pilot_demo/findings/UXM-OWNER/evidence?kind={kind}", b"\x89PNG\r\n\x1a\nproof", {"Content-Type": "image/png", "X-Original-Filename": f"owner-{kind}.png", "X-Captured-At": "2026-07-19T10:30:00Z"})

        owner_evidence = next(finding for finding in self.repo.get_audit("pilot_demo")["findings"] if finding["id"] == "UXM-OWNER")["evidence"]
        borrowed = {
            "id": "UXM-BORROWER", "checkpoint": "NAV-03", "url": "https://example.com/borrower", "page": "Borrower",
            "journey": "Understand", "severity": "medium", "effort": "low", "title": "Borrowed evidence finding",
            "observed": "The client submits another finding's attachment metadata.", "impact": "Evidence completion could be spoofed.",
            "recommendation": "Use only attachments persisted for this finding.",
            "evidence": {"alt": "Borrower evidence on a different page", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Desktop Chrome"},
                         "sourceImage": owner_evidence["sourceImage"], "annotatedImage": owner_evidence["annotatedImage"]},
        }
        status, saved = self.request("/api/audits/pilot_demo/findings", json.dumps(borrowed).encode(), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)
        self.assertNotIn("sourceImage", saved["evidence"])
        self.assertNotIn("annotatedImage", saved["evidence"])

        with self.assertRaises(HTTPError) as blocked:
            self.request("/api/audits/pilot_demo/findings/UXM-BORROWER/evidence-complete", json.dumps({"evidenceComplete": True}).encode(), {"Content-Type": "application/json"})
        self.assertEqual(blocked.exception.code, 400)

    def test_accepted_ai_draft_saves_through_protected_endpoint_and_survives_generic_save_reload(self):
        # This models the post-review browser flow: AI text becomes an operator
        # draft, then only the protected finding endpoint may make it official.
        reviewed_draft = {
            "id": "UXM-AI-REVIEWED", "checkpoint": "NAV-02", "url": "https://example.com/navigation", "page": "Home",
            "journey": "Discover", "severity": "high", "effort": "medium", "title": "Navigation labels obscure tasks",
            "observed": "Navigation labels use internal terminology.", "impact": "Visitors cannot predict where links lead.",
            "recommendation": "Use task-oriented labels.",
            "evidence": {"alt": "Reviewed navigation labels on the public home page", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Desktop Chrome"}},
        }
        status, saved = self.request("/api/audits/pilot_demo/findings", json.dumps(reviewed_draft).encode(), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)
        self.assertEqual(saved["id"], "UXM-AI-REVIEWED")
        self.assertNotIn("candidateId", saved)

        generic_save = {
            "id": "pilot_demo", "client": "Demo after reviewed draft", "url": "https://example.com",
            "locale": "en", "assessments": {"NAV-01": "issue"}, "findings": [],
        }
        status, _ = self.request("/api/audits", json.dumps(generic_save).encode(), {"Content-Type": "application/json"})
        self.assertEqual(status, 201)

        status, reloaded = self.get_json("/api/audits/pilot_demo")
        self.assertEqual(status, 200)
        self.assertEqual(reloaded["client"], "Demo after reviewed draft")
        self.assertEqual([finding["id"] for finding in reloaded["findings"]], ["UXM-001", "UXM-AI-REVIEWED"])

    def test_duplicate_finding_draft_returns_conflict_without_overwriting_persisted_finding(self):
        draft = {
            "id": "UXM-001", "checkpoint": "NAV-02", "url": "https://example.com/pricing", "page": "Pricing",
            "journey": "Understand", "severity": "high", "effort": "medium", "title": "Attempted overwrite",
            "observed": "Plan labels omit the limits.", "impact": "Buyers cannot compare plans.",
            "recommendation": "Show limits beside each plan.",
            "evidence": {"alt": "Mobile pricing table", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Mobile Safari"}},
        }

        with self.assertRaises(HTTPError) as blocked:
            self.request("/api/audits/pilot_demo/findings", json.dumps(draft).encode(), {"Content-Type": "application/json"})

        self.assertEqual(blocked.exception.code, 409)
        self.assertEqual(self.repo.get_audit("pilot_demo")["findings"][0], {"id": "UXM-001"})

    def test_concurrent_new_nonsequential_finding_id_returns_one_conflict_and_preserves_winner(self):
        start = threading.Barrier(3)
        results = []
        results_lock = threading.Lock()

        def submit(title):
            draft = {
                "id": "UXM-909", "checkpoint": "NAV-02", "url": "https://example.com/pricing", "page": "Pricing",
                "journey": "Understand", "severity": "high", "effort": "medium", "title": title,
                "observed": f"{title} observation.", "impact": "Buyers cannot compare plans.",
                "recommendation": "Show limits beside each plan.",
                "evidence": {"alt": "Mobile pricing table", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Mobile Safari"}},
            }
            start.wait()
            request = Request(
                self.base_url + "/api/audits/pilot_demo/findings", data=json.dumps(draft).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            )
            try:
                with urlopen(request, timeout=5) as response:
                    result = (response.status, json.load(response))
            except HTTPError as error:
                result = (error.code, json.load(error))
            with results_lock:
                results.append(result)

        threads = [threading.Thread(target=submit, args=(title,)) for title in ("Concurrent winner A", "Concurrent winner B")]
        for thread in threads:
            thread.start()
        start.wait()
        for thread in threads:
            thread.join(timeout=5)
        self.assertFalse(any(thread.is_alive() for thread in threads))

        self.assertEqual(sorted(status for status, _ in results), [201, 409])
        winner = next(body for status, body in results if status == 201)
        self.assertEqual(self.repo.get_audit("pilot_demo")["findings"][-1], winner)
        self.assertEqual(winner["id"], "UXM-909")

    def test_concurrent_evidence_replacement_wins_and_invalidates_stale_completion(self):
        # Arrange a fully complete finding, then force both operations to make their
        # pre-write decisions from the same persisted revision.  The replacement
        # must win even when the stale completion reaches persistence last.
        for kind in ("source", "annotated"):
            self.repo.attach_evidence(
                "pilot_demo", "UXM-001", kind, b"old-" + kind.encode(), "image/png", f"old-{kind}.png",
                "2026-07-19T10:30:00Z",
            )
        audit = self.repo.get_audit("pilot_demo")
        finding = audit["findings"][0]
        finding["evidence"]["capture"] = {"device": "Desktop Chrome"}
        self.repo.upsert_audit(audit)
        self.repo.mark_evidence_complete("pilot_demo", "UXM-001")
        old_annotated = self.repo.get_audit("pilot_demo")["findings"][0]["evidence"]["annotatedImage"]["filename"]

        attachment_read = threading.Event()
        completion_read = threading.Event()
        attachment_lock_acquired = threading.Event()
        original_get_audit = self.repo.get_audit
        original_connect = self.repo._connect

        class AttachmentConnection:
            def __init__(self, connection):
                self.connection = connection

            def execute(self, statement, parameters=()):
                result = self.connection.execute(statement, parameters)
                if statement == "BEGIN IMMEDIATE":
                    attachment_lock_acquired.set()
                return result

            def __getattr__(self, name):
                return getattr(self.connection, name)

        def staged_connect():
            connection = original_connect()
            return AttachmentConnection(connection) if threading.current_thread().name == "evidence-replacement" else connection

        def staged_get_audit(audit_id):
            audit = original_get_audit(audit_id)
            if threading.current_thread().name == "evidence-replacement":
                attachment_read.set()
                self.assertTrue(completion_read.wait(timeout=5))
            elif threading.current_thread().name == "evidence-completion":
                self.assertTrue(attachment_read.wait(timeout=5))
                completion_read.set()
                self.assertTrue(attachment_lock_acquired.wait(timeout=5))
            return audit

        self.repo.get_audit = staged_get_audit
        self.repo._connect = staged_connect
        replacement, completion = {}, {}
        try:
            attachment_thread = threading.Thread(
                target=lambda: replacement.setdefault("evidence", self.repo.attach_evidence(
                    "pilot_demo", "UXM-001", "annotated", b"replacement", "image/png", "replacement.png",
                    "2026-07-19T11:00:00Z",
                )),
                name="evidence-replacement",
            )
            def complete():
                try:
                    completion["finding"] = self.repo.mark_evidence_complete("pilot_demo", "UXM-001")
                except EvidenceCompletionConflict as error:
                    completion["error"] = error

            completion_thread = threading.Thread(target=complete, name="evidence-completion")
            attachment_thread.start()
            self.assertTrue(attachment_read.wait(timeout=5))
            completion_thread.start()
            self.assertTrue(completion_read.wait(timeout=5))
            attachment_thread.join(timeout=5)
            completion_thread.join(timeout=5)
            self.assertFalse(attachment_thread.is_alive())
            self.assertFalse(completion_thread.is_alive())
        finally:
            self.repo.get_audit = original_get_audit
            self.repo._connect = original_connect

        persisted = self.repo.get_audit("pilot_demo")["findings"][0]
        self.assertEqual(persisted["evidence"]["annotatedImage"]["filename"], replacement["evidence"]["filename"])
        self.assertNotEqual(persisted["evidence"]["annotatedImage"]["filename"], old_annotated)
        self.assertEqual(persisted["evidence"]["status"], "draft")
        self.assertNotIn("evidenceComplete", persisted)
        self.assertEqual(str(completion["error"]), "Evidence changed while completion was pending; review and confirm it again")

    def test_generic_audit_save_racing_new_finding_preserves_finding_and_nonfinding_changes(self):
        generic_save_started = threading.Event()
        allow_generic_save = threading.Event()
        original_save_audit = self.repo.save_audit_preserving_findings
        results = []

        def pause_generic_save(audit, source="workspace"):
            generic_save_started.set()
            self.assertTrue(allow_generic_save.wait(timeout=5))
            return original_save_audit(audit, source)

        generic_payload = {
            "id": "pilot_demo", "client": "Generic Save Client", "url": "https://generic-save.example",
            "locale": "ar", "assessments": {"NAV-01": "pass"}, "findings": [],
        }
        finding_payload = {
            "id": "UXM-RACE", "checkpoint": "NAV-02", "url": "https://example.com/pricing", "page": "Pricing",
            "journey": "Understand", "severity": "high", "effort": "medium", "title": "Concurrent finding",
            "observed": "The race must not discard this finding.", "impact": "Operators would lose work.",
            "recommendation": "Preserve findings in the write transaction.",
            "evidence": {"alt": "Desktop pricing page evidence", "capturedAt": "2026-07-19T10:30:00Z", "capture": {"device": "Desktop Chrome"}},
        }

        def save_generic_audit():
            request = Request(
                self.base_url + "/api/audits", data=json.dumps(generic_payload).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urlopen(request, timeout=5) as response:
                results.append((response.status, json.load(response)))

        self.repo.save_audit_preserving_findings = pause_generic_save
        generic_thread = threading.Thread(target=save_generic_audit, name="generic-audit-save")
        try:
            generic_thread.start()
            self.assertTrue(generic_save_started.wait(timeout=5))
            status, saved_finding = self.request(
                "/api/audits/pilot_demo/findings", json.dumps(finding_payload).encode(), {"Content-Type": "application/json"},
            )
            self.assertEqual(status, 201)
            self.assertEqual(saved_finding["id"], "UXM-RACE")
            allow_generic_save.set()
            generic_thread.join(timeout=5)
            self.assertFalse(generic_thread.is_alive())
        finally:
            allow_generic_save.set()
            generic_thread.join(timeout=5)
            self.repo.save_audit_preserving_findings = original_save_audit

        self.assertEqual(results[0][0], 201)
        stored = self.repo.get_audit("pilot_demo")
        self.assertEqual(stored["client"], "Generic Save Client")
        self.assertEqual(stored["url"], "https://generic-save.example")
        self.assertEqual(stored["locale"], "ar")
        self.assertEqual(stored["assessments"], {"NAV-01": "pass"})
        self.assertEqual([finding["id"] for finding in stored["findings"]], ["UXM-001", "UXM-RACE"])

    def test_generic_audit_save_cannot_create_findings_or_spoof_evidence_completion(self):
        payload = {
            "id": "pilot_demo", "client": "Demo", "url": "https://example.com", "locale": "en",
            "assessments": {"NAV-01": "issue"},
            "findings": [{"id": "UXM-INJECTED", "candidateId": "AIFP-7", "evidenceComplete": True,
                          "evidence": {"status": "complete"}}],
        }

        with self.assertRaises(HTTPError) as blocked:
            self.request("/api/audits", json.dumps(payload).encode(), {"Content-Type": "application/json"})

        self.assertEqual(blocked.exception.code, 400)
        stored = self.repo.get_audit("pilot_demo")
        self.assertEqual([finding["id"] for finding in stored["findings"]], ["UXM-001"])

    def test_finding_draft_and_evidence_completion_reject_malformed_or_oversized_json(self):
        endpoints = [
            "/api/audits/pilot_demo/findings",
            "/api/audits/pilot_demo/findings/UXM-001/evidence-complete",
        ]
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint, case="malformed"):
                with self.assertRaises(HTTPError) as malformed:
                    self.request(endpoint, b"{not json", {"Content-Type": "application/json"})
                self.assertEqual(malformed.exception.code, 400)
            with self.subTest(endpoint=endpoint, case="oversized"):
                with self.assertRaises(HTTPError) as oversized:
                    self.request(endpoint, b"{" + b"x" * (64 * 1024) + b"}", {"Content-Type": "application/json"})
                self.assertEqual(oversized.exception.code, 413)


if __name__ == "__main__":
    unittest.main()
