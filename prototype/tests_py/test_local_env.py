import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend import auth
from backend.local_env import load_operator_env


class LocalOperatorEnvTests(unittest.TestCase):
    def test_load_operator_env_accepts_only_explicit_operator_keys_without_overwriting_process_values(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / '.env'
            env_file.write_text(
                'UXM_OPERATOR_EMAIL= a.tawalbeh@uxmosaic.com\n'
                'UXM_OPERATOR_PASSWORD="local-test-password"\n'
                'UNRELATED_SECRET=must-not-load\n',
                encoding='utf-8',
            )
            with patch.dict(os.environ, {'UXM_OPERATOR_EMAIL': 'process@example.com'}, clear=False):
                os.environ.pop('UXM_OPERATOR_PASSWORD', None)
                os.environ.pop('UNRELATED_SECRET', None)
                load_operator_env(env_file)

                self.assertEqual(os.environ['UXM_OPERATOR_EMAIL'], 'process@example.com')
                self.assertEqual(os.environ['UXM_OPERATOR_PASSWORD'], 'local-test-password')
                self.assertNotIn('UNRELATED_SECRET', os.environ)

    def test_load_operator_env_ignores_missing_file_and_malformed_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / '.env'
            env_file.write_text('not an assignment\nUXM_OPERATOR_EMAIL=admin@example.com\n', encoding='utf-8')
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop('UXM_OPERATOR_EMAIL', None)
                load_operator_env(env_file)
                self.assertEqual(os.environ['UXM_OPERATOR_EMAIL'], 'admin@example.com')
                load_operator_env(Path(directory) / 'missing.env')

    def test_configured_operator_loads_only_the_local_operator_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / '.env'
            env_file.write_text('UXM_OPERATOR_EMAIL=admin@example.com\nUXM_OPERATOR_PASSWORD=test-only-value\n', encoding='utf-8')
            with patch.dict(os.environ, {}, clear=False), patch.object(auth, 'OPERATOR_ENV_PATH', env_file):
                os.environ.pop('UXM_OPERATOR_EMAIL', None)
                os.environ.pop('UXM_OPERATOR_PASSWORD', None)
                self.assertEqual(auth.configured_operator(), ('admin@example.com', 'test-only-value'))


if __name__ == '__main__':
    unittest.main()
