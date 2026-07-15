import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

from backend.api_server import create_server
from backend.storage import AuditRepository


class ReportStaticTests(unittest.TestCase):
    def test_serves_dedicated_report_document_and_assets(self):
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repository = AuditRepository(root / "audits.db", root / "backups")
            server = create_server(repository, project_root, host="127.0.0.1", port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"
            try:
                with urlopen(base_url + "/report.html") as response:
                    report_html = response.read().decode("utf-8")
                with urlopen(base_url + "/report-print.css") as response:
                    print_css = response.read().decode("utf-8")
            finally:
                server.shutdown()
                thread.join()
                server.server_close()

        self.assertIn('id="report-app"', report_html)
        self.assertIn('report.js', report_html)
        self.assertIn('@page', print_css)
        self.assertIn('A4 landscape', print_css)


if __name__ == "__main__":
    unittest.main()
