import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import x_auth as auth


class AuthTest(unittest.TestCase):
    def test_pkce_scopes_and_callback(self):
        query = parse_qs(urlsplit(auth.authorization('client','verifier','state')).query)
        self.assertEqual(query['code_challenge_method'],['S256'])
        self.assertEqual(query['redirect_uri'],[auth.CALLBACK])
        self.assertIn('bookmark.read',query['scope'][0])
        self.assertNotIn('bookmark.write',query['scope'][0])
        self.assertNotIn('verifier',query['code_challenge'][0])

    def test_state_validation(self):
        self.assertEqual(auth.callback_values('/callback?state=good&code=123','good'),'123')
        for path in ['/callback?state=bad&code=123','/wrong?state=good&code=123','/callback?state=good&error=denied']:
            with self.assertRaises(ValueError): auth.callback_values(path,'good')

    def test_private_atomic_storage_and_refresh_rotation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'token.json'
            auth.save(path,'client',{'access_token':'old','refresh_token':'refresh-old','expires_in':-1})
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            with patch.object(auth,'token_request',return_value={'access_token':'new','refresh_token':'refresh-new','expires_in':3600}) as request:
                self.assertEqual(auth.fresh_token(path),'new')
                self.assertEqual(request.call_args.args[0]['refresh_token'],'refresh-old')
                self.assertEqual(json.loads(path.read_text())['refresh_token'],'refresh-new')
                self.assertEqual(auth.fresh_token(path),'new')
                self.assertEqual(request.call_count,1)

    def test_failed_refresh_keeps_previous_token(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'token.json'
            auth.save(path,'client',{'access_token':'old','refresh_token':'refresh-old','expires_in':-1})
            before=path.read_bytes()
            with patch.object(auth,'token_request',side_effect=ValueError('failed')):
                with self.assertRaises(ValueError): auth.fresh_token(path)
            self.assertEqual(before,path.read_bytes())


if __name__ == '__main__': unittest.main()
