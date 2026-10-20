"""Exercise shipped shell/Python examples with mocked responses, never the network."""
import importlib.util
import json
import os
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
        result, calls = self.run_resolver('person@example.invalid', [{'name': 'Artist', 'id': 'artist_1', 'account_id': 'artist_1'}])
        self.assertEqual(result.returncode, 0)
        self.assertIn('resolved:artist_1', result.stdout)
        self.assertIn('/artists', calls)

    def test_ambiguous_names_require_selection(self):
        artists = [{'name': 'Artist', 'id': 'artist_1', 'account_id': 'artist_1'}, {'name': 'Artist', 'id': 'artist_2', 'account_id': 'artist_2'}]
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


class RosterOnboardingExamples(unittest.TestCase):
    helper = ROOT / 'skills/recoup-roster-add-artist/scripts/onboarding_examples.sh'
    spotify_id = '0123456789ABCDEFGHIJKL'
    org_id = '00000000-0000-4000-8000-000000000001'
    artist_id = '00000000-0000-4000-8000-000000000002'

    def run_example(self, command, status=201, payload=None, transport_exit=0):
        if payload is None:
            payload = {'artist': {'id': self.artist_id, 'account_id': self.artist_id}}
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            log = directory / 'calls.jsonl'
            curl = directory / 'curl'
            curl.write_text('''#!/usr/bin/env python3
import json, os, sys
with open(os.environ['MOCK_CALLS'], 'a') as output:
    output.write(json.dumps(sys.argv[1:]) + '\\n')
if int(os.environ['MOCK_EXIT']) == 0:
    print(os.environ['MOCK_PAYLOAD'] + '\\n' + os.environ['MOCK_STATUS'], end='')
sys.exit(int(os.environ['MOCK_EXIT']))
''')
            curl.chmod(0o755)
            environment = {**os.environ, 'PATH': str(directory) + os.pathsep + os.environ['PATH'],
                           'RECOUP_API_KEY': 'fixture-only', 'RECOUP_ACCESS_TOKEN': '',
                           'MOCK_CALLS': str(log), 'MOCK_PAYLOAD': json.dumps(payload),
                           'MOCK_STATUS': str(status), 'MOCK_EXIT': str(transport_exit)}
            result = subprocess.run(['bash', '-c', 'source "$1"\n' + command, 'fixture', str(self.helper)],
                                    env=environment, capture_output=True, text=True)
            calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            return result, calls

    def test_canonical_create_sends_exact_identity_and_workspace_and_retains_created_result(self):
        result, calls = self.run_example(
            f'''onboard_spotify_artist 'Artist "A"' '{self.spotify_id}' '{self.org_id}' ''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][-1], 'https://api.recoupable.dev/api/artists')
        self.assertEqual(calls[0][calls[0].index('-X') + 1], 'POST')
        body = json.loads(calls[0][calls[0].index('--data') + 1])
        self.assertEqual(body, {'name': 'Artist "A"', 'spotify_artist_id': self.spotify_id,
                                'organization_id': self.org_id})
        self.assertEqual(json.loads(result.stdout), {
            'spotify_artist_id': self.spotify_id, 'organization_id': self.org_id,
            'artist_account_id': self.artist_id, 'create_http_status': 201, 'outcome': 'created'})

    def test_existing_canonical_keeps_returned_id_and_reused_200_outcome(self):
        result, calls = self.run_example(
            f"onboard_spotify_artist Artist '{self.spotify_id}' '{self.org_id}'", status=200)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 1)
        receipt = json.loads(result.stdout)
        self.assertEqual((receipt['artist_account_id'], receipt['create_http_status'], receipt['outcome']),
                         (self.artist_id, 200, 'reused'))

    def test_http_errors_do_not_retry_or_fall_back_to_name_only(self):
        for status in [401, 403, 409, 402, 429, 503]:
            with self.subTest(status=status):
                result, calls = self.run_example(
                    f"onboard_spotify_artist Artist '{self.spotify_id}' '{self.org_id}'",
                    status=status, payload={'error': 'Stop', 'billingUrl': 'https://example.invalid/billing'})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(len(calls), 1)
                self.assertEqual(json.loads(calls[0][calls[0].index('--data') + 1])['spotify_artist_id'], self.spotify_id)
                self.assertEqual(result.stdout, '')

    def test_unresolved_identity_stops_before_any_mutation(self):
        result, calls = self.run_example(f"onboard_spotify_artist Artist unresolved '{self.org_id}'")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])

    def test_conflicting_returned_id_aliases_require_reconciliation(self):
        result, calls = self.run_example(
            f"onboard_spotify_artist Artist '{self.spotify_id}' '{self.org_id}'",
            payload={'artist': {'id': self.artist_id, 'account_id': 'different-artist'}})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.stdout, '')

    def test_manual_creation_is_an_explicit_separate_request(self):
        result, calls = self.run_example(f"onboard_manual_artist Artist '{self.org_id}' confirmed-manual")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 1)
        self.assertEqual(json.loads(calls[0][calls[0].index('--data') + 1]),
                         {'name': 'Artist', 'organization_id': self.org_id})
        self.assertEqual(json.loads(result.stdout)['spotify_artist_id'], None)

    def test_manual_creation_without_deliberate_confirmation_makes_no_request(self):
        result, calls = self.run_example(f"onboard_manual_artist Artist '{self.org_id}'")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])

    def test_lost_acknowledgment_then_new_session_reconciliation_is_read_only(self):
        command = f"onboard_spotify_artist Artist '{self.spotify_id}' '{self.org_id}'"
        failed, writes = self.run_example(command, transport_exit=7)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(len(writes), 1)
        self.assertEqual(failed.stdout, '')
        roster = {'artists': [{'id': self.artist_id, 'account_id': self.artist_id,
                              'name': 'Artist', 'account_socials': [
                                  {'profile_url': f'https://open.spotify.com/artist/{self.spotify_id}'}]}]}
        result, reads = self.run_example(
            f"reconcile_spotify_artist '{self.spotify_id}' '{self.org_id}'", status=200, payload=roster)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(reads), 1)
        self.assertEqual(reads[0][reads[0].index('-X') + 1], 'GET')
        self.assertEqual(reads[0][-1], f'https://api.recoupable.dev/api/artists?org_id={self.org_id}')
        self.assertEqual(json.loads(result.stdout), {
            'spotify_artist_id': self.spotify_id, 'organization_id': self.org_id,
            'artist_account_id': self.artist_id, 'roster_http_status': 200, 'reconciliation': 'matched'})

    def test_same_name_with_another_spotify_identity_is_not_a_reconciled_match(self):
        roster = {'artists': [{'id': self.artist_id, 'account_id': self.artist_id, 'name': 'Artist',
                              'account_socials': [{'link': 'https://open.spotify.com/artist/ZZZZZZZZZZZZZZZZZZZZZZ'}]}]}
        result, calls = self.run_example(
            f"reconcile_spotify_artist '{self.spotify_id}' '{self.org_id}'", status=200, payload=roster)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['reconciliation'], 'not_found')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][calls[0].index('-X') + 1], 'GET')

    def test_reconciliation_keeps_saved_id_and_does_not_replace_it_on_conflict(self):
        roster = {'artists': [{'id': self.artist_id, 'account_id': self.artist_id,
                              'account_socials': [{'link': f'https://open.spotify.com/artist/{self.spotify_id}'}]}]}
        result, calls = self.run_example(
            f"reconcile_spotify_artist '{self.spotify_id}' '{self.org_id}' saved-other-artist",
            status=200, payload=roster)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][calls[0].index('-X') + 1], 'GET')

    def test_reconciliation_denial_never_attempts_another_write(self):
        result, calls = self.run_example(
            f"reconcile_spotify_artist '{self.spotify_id}' '{self.org_id}'",
            status=403, payload={'error': 'Access denied'})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][calls[0].index('-X') + 1], 'GET')


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
