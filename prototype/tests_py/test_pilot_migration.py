"""End-to-end regression coverage for legacy pilot readiness migration."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from backend.storage import AuditRepository

PROTOTYPE_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = PROTOTYPE_ROOT.parent


def load_migration_module():
    script = AUDIT_ROOT / "scripts" / "import_pilots_to_prototype.py"
    spec = importlib.util.spec_from_file_location("import_pilots_to_prototype", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PilotMigrationTests(unittest.TestCase):
    def test_migration_makes_every_supported_finding_publication_ready_and_omits_excluded_findings(self):
        migration = load_migration_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repository = AuditRepository(root / "uxm-audit.db", root / "backups", root / "evidence")

            imported = migration.import_pilots(AUDIT_ROOT / "pilots", repository, AUDIT_ROOT)

            self.assertEqual(imported, {
                "pilot_ammancity_eservices_20260715": 5,
                "pilot_jordan_gov_onyourservice_20260714": 5,
                "pilot_tawasal_bekhedmetcom_20260714": 4,
            })
            amman = repository.get_audit("pilot_ammancity_eservices_20260715")
            self.assertEqual(amman["findings"][0]["arabic"]["title"], "مرشح القطاع يرسل إشارات متناقضة حول إلزامية الإدخال")
            self.assertGreaterEqual(len(amman["scope"]["included"]), 5)
            self.assertGreaterEqual(len(amman["scope"]["journeys"]), 3)
            self.assertGreaterEqual(len(amman["scope"]["pagesVisited"]), 4)
            for audit_id, expected_findings in imported.items():
                audit = repository.get_audit(audit_id)
                self.assertEqual(len(audit["findings"]), expected_findings)
                self.assertFalse(any(finding.get("excludedFromPublication") for finding in audit["findings"]))
                self.assertTrue(repository.publication_readiness(audit_id)["ready"])
                for finding in audit["findings"]:
                    with self.subTest(audit=audit_id, finding=finding["id"]):
                        self.assertTrue(finding["page"])
                        self.assertTrue(finding["journey"])
                        self.assertTrue(finding["url"])
                        self.assertTrue(all(finding["arabic"][field] for field in ("title", "observed", "impact", "recommendation")))
                        evidence = finding["evidence"]
                        self.assertTrue(evidence["capturedAt"])
                        for image_field in ("sourceImage", "annotatedImage"):
                            image = evidence[image_field]
                            self.assertIsInstance(image, dict)
                            self.assertTrue(image["filename"])
                            self.assertTrue((repository.evidence_dir / image["filename"]).is_file())

    def test_root_pilots_use_readiness_schema_and_keep_only_tawasal_unsupported_findings_excluded(self):
        excluded = set()
        supported = 0
        for audit_path in sorted((AUDIT_ROOT / "pilots").glob("*/audit.json")):
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            for finding in audit["findings"]:
                evidence = finding["evidence"]
                if finding.get("excludedFromPublication"):
                    excluded.add((audit["id"], finding["id"]))
                    continue
                supported += 1
                self.assertTrue(finding["page"])
                self.assertTrue(finding["journey"])
                self.assertTrue(finding["url"])
                self.assertTrue(evidence["capturedAt"])
                self.assertIsInstance(evidence["sourceImage"], dict)
                self.assertIsInstance(evidence["annotatedImage"], dict)

        self.assertEqual(supported, 14)
        self.assertEqual(excluded, {
            ("pilot_tawasal_bekhedmetcom_20260714", "UXM-003"),
            ("pilot_tawasal_bekhedmetcom_20260714", "UXM-006"),
        })

    def test_excluded_finding_never_blocks_readiness_or_appears_in_imported_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repository = AuditRepository(root / "uxm-audit.db", root / "backups", root / "evidence")
            repository.upsert_audit({
                "id": "only_excluded", "client": "Demo", "url": "https://example.test", "locale": "ar",
                "findings": [{"id": "UXM-003", "excludedFromPublication": True, "evidence": {"status": "pending"}}],
            })

            readiness = repository.publication_readiness("only_excluded")

            self.assertTrue(readiness["ready"])
            self.assertEqual(readiness["blockers"], [])


if __name__ == "__main__":
    unittest.main()
