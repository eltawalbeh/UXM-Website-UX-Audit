import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from backend.storage import AuditRepository
from backend.ai_first_pass import load_checkpoint_library, normalize_provider_candidates


CANDIDATE = {
    "id": "AIFP-001", "pageUrl": "https://public.example/", "pageName": "Public home",
    "journey": "Service discovery", "checkpointId": "NAV-02", "reviewState": "Awaiting review",
    "duplicateRisk": "unknown", "title": "Navigation label may be unclear",
    "observation": "The captured page uses a generic Services label.",
    "impact": "Visitors may not recognize their task.", "recommendation": "Validate task-focused wording.",
    "suggestedSeverity": "medium", "confidence": "low", "reasons": ["Generic label in captured excerpt"],
    "evidenceRefs": ["https://public.example/"], "evidenceGaps": ["Confirm the destination labels in a screenshot."],
}


class AiFirstPassApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        static_root = root / "static"
        static_root.mkdir()
        (static_root / "index.html").write_text("<h1>UXM Audit</h1>", encoding="utf-8")
        self.repo = AuditRepository(root / "uxm-audit.db", root / "backups", root / "evidence")
        self.repo.upsert_audit({
            "id": "audit_demo", "client": "Demo", "url": "https://public.example/", "scope": "Public pages only",
            "assessments": {"NAV-02": "issue"}, "findings": [{"id": "UXM-001", "title": "Existing issue"}],
        })
        self.captured_contexts = []

        def explorer(url, scope_request=None):
            return {"status": "ready", "scope": {"requestedUrl": url, "visited": [{
                "url": "https://public.example/", "title": "Public home", "capturedAt": "2026-07-15T12:00:00Z",
                "textExcerpt": "Services are available from the navigation.", "capture": {"kind": "text", "url": "https://public.example/"},
            }], "skipped": [{"url": "https://public.example/login", "reason": "login or account route"}]}}

        def drafter(context):
            self.captured_contexts.append(context)
            return {"status": "ready", "candidates": [CANDIDATE]}

        from backend.api_server import create_server
        self.server = create_server(self.repo, static_root, host="127.0.0.1", port=0, ai_first_pass_explorer=explorer, ai_first_pass_drafter=drafter)
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

    def test_first_pass_returns_transient_candidates_and_honest_scope_contract_without_changing_audit(self):
        before = self.repo.get_audit("audit_demo")

        status, body = self.post_json("/api/audits/audit_demo/ai-first-pass", {"url": "https://public.example/", "productType": "government_civic", "bundle": "general_health_check"})

        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["scope"]["visited"][0]["url"], "https://public.example/")
        self.assertEqual(body["scope"]["productType"], "government_civic")
        self.assertEqual(body["scope"]["bundle"], "general_health_check")
        self.assertEqual(body["scope"]["checkpointCount"], 48)
        self.assertIn("not verified", " ".join(body["scope"]["exclusions"]).lower())
        self.assertEqual(body["candidates"][0]["evidenceRefs"], ["https://public.example/"])
        self.assertEqual(self.captured_contexts[0]["pages"][0]["title"], "Public home")
        self.assertEqual(self.captured_contexts[0]["scopeContract"]["bundle"], "general_health_check")
        self.assertEqual(self.repo.get_audit("audit_demo"), before)
        self.assertNotIn("candidates", self.repo.get_audit("audit_demo"))

    def test_product_and_bundle_are_required_and_selected_pages_are_same_origin(self):
        status, body = self.post_json("/api/audits/audit_demo/ai-first-pass", {"url": "https://public.example/"})
        self.assertEqual(status, 400)
        self.assertIn("product type", body["error"].lower())

        status, body = self.post_json("/api/audits/audit_demo/ai-first-pass", {"url": "https://public.example/", "productType": "ecommerce", "bundle": "selected_pages", "selectedPages": ["https://elsewhere.example/catalog"]})
        self.assertEqual(status, 400)
        self.assertIn("same public origin", body["error"])

    def test_selected_pages_contract_changes_the_explorer_request_and_candidate_scope(self):
        received = []
        self.server.shutdown(); self.thread.join(); self.server.server_close()
        from backend.api_server import create_server
        def scoped_explorer(url, scope_request):
            received.append(scope_request)
            return {"status": "ready", "scope": {"requestedUrl": url, "visited": [{"url": "https://public.example/pricing", "title": "Pricing", "textExcerpt": "Plans", "capturedAt": "2026-07-15T12:00:00Z", "capture": {"kind": "text", "url": "https://public.example/pricing"}}], "skipped": []}}
        candidate = {**CANDIDATE, "pageUrl": "https://public.example/pricing", "pageName": "Pricing", "journey": "Pricing evaluation", "checkpointId": "CONV-01", "evidenceRefs": ["https://public.example/pricing"]}
        self.server = create_server(self.repo, Path(self.temp.name) / "static", host="127.0.0.1", port=0, ai_first_pass_explorer=scoped_explorer, ai_first_pass_drafter=lambda context: {"status": "ready", "candidates": [candidate]})
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start(); self.base_url = f"http://127.0.0.1:{self.server.server_port}"

        status, body = self.post_json("/api/audits/audit_demo/ai-first-pass", {"url": "https://public.example/", "productType": "saas_digital_product", "bundle": "selected_pages", "selectedPages": ["/pricing"]})

        self.assertEqual(status, 200)
        self.assertEqual(received[0]["selectedPages"], ["https://public.example/pricing"])
        self.assertEqual(body["scope"]["includedUrls"], ["https://public.example/pricing"])
        self.assertEqual(body["candidates"][0]["checkpointId"], "CONV-01")

    def test_unsafe_url_is_rejected_before_fetch_or_model_call(self):
        status, body = self.post_json("/api/audits/audit_demo/ai-first-pass", {"url": "http://127.0.0.1/private", "productType": "government_civic", "bundle": "full_website"})
        self.assertEqual(status, 400)
        self.assertIn("public http(s)", body["error"])
        self.assertEqual(self.captured_contexts, [])

    def test_explorer_or_ai_failure_returns_no_fabricated_candidates_and_leaves_audit_unchanged(self):
        self.server.shutdown(); self.thread.join(); self.server.server_close()
        from backend.api_server import create_server
        self.server = create_server(self.repo, Path(self.temp.name) / "static", host="127.0.0.1", port=0,
                                    ai_first_pass_explorer=lambda url, scope: {"status": "unavailable", "message": "Could not safely fetch public pages."},
                                    ai_first_pass_drafter=lambda context: self.fail("model must not be called"))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start(); self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        status, body = self.post_json("/api/audits/audit_demo/ai-first-pass", {"url": "https://public.example/", "productType": "government_civic", "bundle": "full_website"})
        self.assertEqual(status, 503)
        self.assertEqual(body["status"], "unavailable")
        self.assertNotIn("candidates", body)
        self.assertEqual(len(self.repo.get_audit("audit_demo")["findings"]), 1)
    def test_nemotron_candidate_shape_is_normalized_without_weakening_evidence_or_checkpoint_rules(self):
        raw = [{
            "id": "C1", "pageUrl": "https://public.example/", "pageName": "Homepage",
            "journey": "Public discovery", "applicableCheckpointId": "HP-01",
            "evidenceRefs": [{"url": "https://public.example/", "kind": "text"}],
            "observation": "The page does not explain its purpose.", "impact": "Visitors may leave.",
            "recommendation": "State the purpose clearly.", "suggestedSeverity": "Medium",
            "confidence": "High", "evidenceGaps": [], "duplicateRisk": {"level": "Low", "matches": []},
            "reasons": "The captured text contains no value proposition.", "reviewState": "Awaiting review",
            "title": "Purpose is unclear",
        }, {
            **CANDIDATE, "id": "AIFP-002", "checkpointId": "CK-01",
        }]

        normalized = normalize_provider_candidates(raw, {"https://public.example/"}, {"HP-01", "NAV-02"})

        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]["id"], "AIFP-001")
        self.assertEqual(normalized[0]["checkpointId"], "HP-01")
        self.assertEqual(normalized[0]["evidenceRefs"], ["https://public.example/"])
        self.assertEqual(normalized[0]["suggestedSeverity"], "medium")
        self.assertEqual(normalized[0]["confidence"], "high")
        self.assertEqual(normalized[0]["duplicateRisk"], "low")
        self.assertEqual(normalized[0]["reasons"], ["The captured text contains no value proposition."])

    def test_checkpoint_library_is_the_real_272_source_for_first_pass(self):
        checkpoints = load_checkpoint_library()

        self.assertEqual(len(checkpoints), 272)
        self.assertEqual(checkpoints[0]["id"], "HP-01")
        self.assertTrue(all(item.get("id") and item.get("title") for item in checkpoints))
    def test_first_pass_context_uses_bundle_specific_subset_selected_from_all_272(self):
        from backend.ai_first_pass import build_first_pass_context
        scope = {
            "requestedUrl": "https://public.example/", "visited": [], "productType": "corporate_marketing",
            "productTypeLabel": "Corporate / marketing website", "bundle": "general_health_check",
            "bundleLabel": "General health check", "includedUrls": ["https://public.example/"],
            "includedJourneys": ["Public discovery"], "checkpointCount": 48, "exclusions": [],
            "candidateRule": "Human review required",
        }

        context = build_first_pass_context({"id": "audit_demo", "findings": []}, scope)

        self.assertEqual(len(context["checkpointLibrary"]), 48)
        self.assertTrue({item["id"] for item in context["checkpointLibrary"]}.issubset({item["id"] for item in load_checkpoint_library()}))


if __name__ == "__main__":
    unittest.main()
