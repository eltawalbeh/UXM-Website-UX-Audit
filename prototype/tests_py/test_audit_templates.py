import unittest

from backend.audit_templates import load_audit_templates
from backend.ai_first_pass import load_checkpoint_library


class AuditTemplateCatalogTests(unittest.TestCase):
    def test_catalog_has_five_complete_templates_using_only_official_checkpoint_ids(self):
        templates = load_audit_templates()
        official_ids = {item["id"] for item in load_checkpoint_library()}

        self.assertEqual({item["productType"] for item in templates}, {
            "government_civic", "corporate_marketing", "ecommerce", "saas_digital_product", "content_publisher",
        })
        self.assertEqual(len(templates), 5)
        for template in templates:
            self.assertTrue(template["id"])
            self.assertTrue(template["name"])
            self.assertTrue(template["journeys"])
            self.assertGreaterEqual(len(template["checkpointIds"]), 30)
            self.assertTrue(set(template["checkpointIds"]).issubset(official_ids))
            self.assertEqual(len(template["checkpointIds"]), len(set(template["checkpointIds"])))
            self.assertIn("annotated_screenshot", template["evidenceRequirements"])
            self.assertIn("findings", template["reportSections"])


if __name__ == "__main__":
    unittest.main()
