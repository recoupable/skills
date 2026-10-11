"""Exercise shipped shell/Python examples with mocked responses, never the network."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


def blocks(name):
    return re.findall(r'```bash\n([\s\S]*?)\n```', (ROOT / 'references' / name).read_text())


class ResearchExamples(unittest.TestCase):
    def run_helper(self, status, retry_after=None):
        text = (ROOT / 'references/research-context.md').read_text()
        helper = re.search(r'research_get\(\) \{[\s\S]*?\n\}', text).group()
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'calls'
            headers = '' if retry_after is None else f'''while [ "$#" -gt 0 ]; do
  if [ "$1" = -D ]; then printf 'Retry-After: {retry_after}\\r\\n' > "$2"; break; fi
  shift
done'''
            mock = f'''BASE=https://example.invalid/api; AUTH=()
curl() {{ echo call >> {log}; {headers}
printf '%s\\n%s' '{{"billingUrl":"https://example.invalid/billing"}}' '{status}'; }}
sleep() {{ :; }}
'''
            result = subprocess.run(['bash', '-c', mock + helper + '\nresearch_get "metrics?id=verified"'], capture_output=True, text=True)
            return result, len(log.read_text().splitlines())

    def test_billing_failure_stops_and_surfaces_recovery_without_retry(self):
        result, calls = self.run_helper(402)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('https://example.invalid/billing', result.stderr)
        self.assertEqual(calls, 1)

    def test_transient_failure_has_bounded_retries(self):
        result, calls = self.run_helper(503)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, 3)

    def test_rate_limit_defers_reads_without_automatic_retry(self):
        result, calls = self.run_helper(429)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Retry-After', result.stderr)
        self.assertEqual(calls, 1)

    def test_rate_limit_surfaces_server_retry_interval(self):
        result, calls = self.run_helper(429, retry_after=120)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, 1)
        self.assertIn('Retry-After: 120', result.stderr)

    def test_optional_audio_failure_continues_without_fabricated_values(self):
        audio = next(block for block in blocks('research-context.md') if 'AUDIO=' in block)
        code = '''AUTH=(); BASE=https://example.invalid/api; TRACK_ID=verified
curl() { return 22; }
research_get() { echo 'Research unavailable' >&2; return 1; }
''' + audio + '\nprintf "continued:%s" "$TEMPO"'
        result = subprocess.run(['bash', '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('continued:', result.stdout)
        self.assertNotIn('continued:0', result.stdout)


class AccountExamples(unittest.TestCase):
    def run_resolver(self, email, artists):
        block = next(block for block in blocks('account-resolver.md') if 'IDENTITY=' in block)
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'calls'
            responses = {
                '*/accounts/id': {'accountId': 'account_1'},
                '*/accounts/account_1': {'account': {'email': email}},
                '*/artists': {'artists': artists},
            }
            cases = '\n'.join(f"{url}) printf '%s' '{json.dumps(data)}';;" for url, data in responses.items())
            mock = f'''AUTH=(); ARTIST_NAME=Artist; RECOUP_ORG_ID=
curl() {{ echo "${{@: -1}}" >> {log}; case "${{@: -1}}" in
{cases}
esac; }}
'''
            result = subprocess.run(['bash', '-c', mock + block + '\nprintf "resolved:%s" "$ARTIST_ROW_ID"'], capture_output=True, text=True)
            return result, log.read_text()

    def test_disposable_identity_stops_before_roster_resolution(self):
        result, calls = self.run_resolver('agent+demo@recoupable.dev', [])
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('/artists', calls)

    def test_real_identity_resolves_one_artist(self):
        result, calls = self.run_resolver('person@example.invalid', [{'name': 'Artist', 'id': 'row_1', 'account_id': 'artist_1'}])
        self.assertEqual(result.returncode, 0)
        self.assertIn('resolved:row_1', result.stdout)
        self.assertIn('/artists', calls)

    def test_ambiguous_names_require_selection(self):
        artists = [{'name': 'Artist', 'id': 'row_1', 'account_id': 'artist_1'}, {'name': 'Artist', 'id': 'row_2', 'account_id': 'artist_2'}]
        result, _ = self.run_resolver('person@example.invalid', artists)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Multiple', result.stderr)

    def test_missing_artist_stops_before_downstream_calls(self):
        result, _ = self.run_resolver('person@example.invalid', [])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No visible artist', result.stderr)
        self.assertNotIn('resolved:', result.stdout)

    def test_incomplete_artist_identifiers_stop(self):
        result, _ = self.run_resolver('person@example.invalid', [{'name': 'Artist', 'id': 'row_1'}])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing required identifiers', result.stderr)


class EstimatorExamples(unittest.TestCase):
    def run_api(self, payload):
        path = ROOT / 'skills/recoup-catalog-estimate-value/scripts/estimate.py'
        spec = importlib.util.spec_from_file_location('estimate', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        response = subprocess.CompletedProcess([], 0, payload, '')
        with patch.object(module, 'auth_header', return_value=[]), patch.object(module.subprocess, 'run', return_value=response):
            return module.api('research/track/stats')

    def test_empty_404_remains_missing_data(self):
        self.assertEqual(self.run_api('\n404'), {})

    def test_html_gateway_error_preserves_http_status(self):
        with self.assertRaisesRegex(SystemExit, 'research HTTP 503'):
            self.run_api('<html>Unavailable</html>\n503')

    def test_non_json_billing_error_still_identifies_billing(self):
        with self.assertRaisesRegex(SystemExit, 'billing \\(402\\)'):
            self.run_api('\n402')

    def test_billing_url_exits_instead_of_returning_missing_counts(self):
        path = ROOT / 'skills/recoup-catalog-estimate-value/scripts/estimate.py'
        spec = importlib.util.spec_from_file_location('estimate', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        response = subprocess.CompletedProcess([], 0, '{"error":"insufficient_credits","billingUrl":"https://example.invalid/billing"}\n402', '')
        with patch.object(module, 'auth_header', return_value=[]), patch.object(module.subprocess, 'run', return_value=response):
            with self.assertRaisesRegex(SystemExit, 'https://example.invalid/billing'):
                module.api('research/track/stats')


if __name__ == '__main__':
    unittest.main()
