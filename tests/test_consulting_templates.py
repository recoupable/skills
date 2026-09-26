"""Offline behavior checks for the generic proposal and provider adapter templates."""
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


render = module('proposal_render', 'skills/recoup-internal-consulting-proposal-designer/assets/render.py')
http = module('http_template', 'skills/recoup-internal-consulting-integration-scaffolder/assets/http_client.py')


class TemplateTests(unittest.TestCase):
    def test_public_copy_policy_regressions(self):
        script = ROOT / "skills/recoup-internal-consulting-copy-writer/scripts/test_public_copy.py"
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_proposal_refuses_unfilled_fields_before_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'proposal.html'
            path.write_text('<p>{{TIER_1_PRICE}}</p>')
            with self.assertRaisesRegex(ValueError, 'TIER_1_PRICE'):
                render.validate_html(path)
            path.write_text('<p>Fictional scope with terms still to be agreed.</p>')
            self.assertEqual(render.validate_html(path), path.resolve())

    def test_provider_auth_cannot_be_forwarded_to_a_different_origin(self):
        client = http.ReadOnlyClient('https://api.example.test/v1/', 'TEST_PROVIDER_KEY', token='synthetic-token')
        with self.assertRaisesRegex(ValueError, 'configured provider origin'):
            client.get('https://other.example.test/records')
        with self.assertRaisesRegex(ValueError, 'configured provider origin'):
            client.get('//other.example.test/records')

    def test_adapter_rejects_insecure_or_embedded_credential_base_urls(self):
        for url in ['http://api.example.test', 'https://user:password@api.example.test']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                http.ReadOnlyClient(url, 'TEST_PROVIDER_KEY', token='synthetic-token')

    def test_redirects_do_not_implicitly_forward_credentials(self):
        self.assertIsNone(http.NoRedirect().redirect_request(None,None,302,'',{},'https://other.example.test'))


if __name__ == '__main__':
    unittest.main()
