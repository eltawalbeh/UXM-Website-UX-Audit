import tempfile
import unittest
from pathlib import Path

from backend.storage import AuditRepository


class FindingEditorPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.repo = AuditRepository(root / "uxm-audit.db", root / "backups")
        self.repo.upsert_audit({
            "id": "editor_audit", "client": "Editor Client", "url": "https://example.test", "locale": "en",
            "findings": [],
        })

    def tearDown(self):
        self.temp.cleanup()

    def finding(self):
        return {
            "id": "UXM-101", "checkpoint": "NAV-02", "url": "https://example.test/pricing",
            "page": "Pricing", "journey": "Understand", "severity": "high", "effort": "medium",
            "title": "Pricing labels hide plan differences",
            "observed": "Plan labels do not explain included limits.",
            "impact": "Buyers cannot compare plans confidently.",
            "recommendation": "State limits beside each plan label.",
            "evidence": {"alt": "Mobile pricing comparison.", "capture": {"device": "Mobile Safari"}, "capturedAt": "2026-07-19T10:30:00Z"},
        }

    def test_save_finding_draft_persists_structured_metadata_but_never_claims_completion(self):
        saved = self.repo.save_finding_draft("editor_audit", self.finding())

        self.assertEqual(saved["checkpoint"], "NAV-02")
        self.assertEqual(saved["effort"], "medium")
        self.assertEqual(saved["evidence"]["capture"]["device"], "Mobile Safari")
        self.assertEqual(saved["evidence"]["status"], "draft")
        self.assertNotIn("evidenceComplete", saved)
        self.assertEqual(self.repo.get_audit("editor_audit")["findings"][0]["id"], "UXM-101")

    def test_evidence_completion_requires_both_uploaded_images_and_truthful_capture_metadata(self):
        self.repo.save_finding_draft("editor_audit", self.finding())

        with self.assertRaisesRegex(ValueError, "source image"):
            self.repo.mark_evidence_complete("editor_audit", "UXM-101")

        self.repo.attach_evidence("editor_audit", "UXM-101", "source", b"source", "image/png", "source.png", "2026-07-19T10:30:00Z")
        with self.assertRaisesRegex(ValueError, "annotated image"):
            self.repo.mark_evidence_complete("editor_audit", "UXM-101")

        self.repo.attach_evidence("editor_audit", "UXM-101", "annotated", b"annotated", "image/png", "annotated.png", "2026-07-19T10:30:00Z")
        complete = self.repo.mark_evidence_complete("editor_audit", "UXM-101")

        self.assertEqual(complete["evidence"]["status"], "complete")
        self.assertTrue(complete["evidenceComplete"])
        self.assertTrue(self.repo.publication_readiness("editor_audit")["ready"])

    def test_candidate_payload_cannot_be_persisted_as_an_official_finding(self):
        candidate = self.finding() | {"candidateId": "AIFP-1"}
        with self.assertRaisesRegex(ValueError, "candidate"):
            self.repo.save_finding_draft("editor_audit", candidate)
        self.assertEqual(self.repo.get_audit("editor_audit")["findings"], [])

    def test_duplicate_finding_id_is_rejected_without_overwriting_the_original_finding(self):
        original = self.repo.save_finding_draft("editor_audit", self.finding())
        duplicate = self.finding() | {"title": "Attempted overwrite"}

        with self.assertRaisesRegex(ValueError, "already exists"):
            self.repo.save_finding_draft("editor_audit", duplicate)

        stored = self.repo.get_audit("editor_audit")["findings"]
        self.assertEqual(stored, [original])

    def test_save_finding_draft_normalizes_capture_timestamp_to_utc_iso(self):
        finding = self.finding()
        finding["evidence"]["capturedAt"] = "2026-07-19T13:30:00+03:00"

        saved = self.repo.save_finding_draft("editor_audit", finding)

        self.assertEqual(saved["evidence"]["capturedAt"], "2026-07-19T10:30:00Z")

    def test_replacing_an_attachment_resets_completion_until_the_operator_reconfirms_it(self):
        self.repo.save_finding_draft("editor_audit", self.finding())
        self.repo.attach_evidence("editor_audit", "UXM-101", "source", b"source", "image/png", "source.png", "2026-07-19T10:30:00Z")
        self.repo.attach_evidence("editor_audit", "UXM-101", "annotated", b"annotated", "image/png", "annotated.png", "2026-07-19T10:30:00Z")
        self.repo.mark_evidence_complete("editor_audit", "UXM-101")

        self.repo.attach_evidence("editor_audit", "UXM-101", "annotated", b"new annotated", "image/png", "new-annotated.png", "2026-07-19T10:30:00Z")
        stored = self.repo.get_audit("editor_audit")["findings"][0]

        self.assertEqual(stored["evidence"]["status"], "draft")
        self.assertNotIn("evidenceComplete", stored)

    def test_readiness_requires_explicit_completion_even_when_both_images_exist(self):
        self.repo.save_finding_draft("editor_audit", self.finding())
        self.repo.attach_evidence("editor_audit", "UXM-101", "source", b"source", "image/png", "source.png", "2026-07-19T10:30:00Z")
        self.repo.attach_evidence("editor_audit", "UXM-101", "annotated", b"annotated", "image/png", "annotated.png", "2026-07-19T10:30:00Z")

        readiness = self.repo.publication_readiness("editor_audit")

        self.assertFalse(readiness["ready"])
        self.assertIn("evidence_not_explicitly_complete", {blocker["code"] for blocker in readiness["blockers"]})

    def test_finding_draft_rejects_invalid_enums_urls_lengths_and_non_descriptive_alt(self):
        cases = [
            ("severity", "urgent", "severity"),
            ("effort", "now", "effort"),
            ("url", "javascript:alert(1)", "URL"),
            ("title", "x" * 241, "title"),
            ("observed", "x" * 4001, "observed"),
            ("evidence.alt", "photo", "descriptive"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                finding = self.finding()
                if field == "evidence.alt":
                    finding["evidence"]["alt"] = value
                else:
                    finding[field] = value
                with self.assertRaisesRegex(ValueError, error):
                    self.repo.save_finding_draft("editor_audit", finding)


if __name__ == "__main__":
    unittest.main()
