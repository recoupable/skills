#!/usr/bin/env python3
"""Local PKCE connection for an X OAuth 2.0 public/native app. Never prints tokens."""
import argparse
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from bookmarks import NoRedirect

CALLBACK = 'http://127.0.0.1:8765/callback'
SCOPES = 'tweet.read users.read bookmark.read offline.access'


def token_request(values):
    request = urllib.request.Request('https://api.x.com/2/oauth2/token',
        data=urllib.parse.urlencode(values).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            result = json.load(response)
    except (urllib.error.URLError, TimeoutError):
        raise ValueError('X token request failed. Check the app type, client ID and callback; reconnect if necessary.') from None
    if not isinstance(result.get('access_token'), str) or not result['access_token']:
        raise ValueError('X did not return an access token')
    return result


def save(path, client_id, tokens):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dict(tokens, client_id=client_id, expires_at=time.time() + int(tokens.get('expires_in', 7200)))
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.x-oauth-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def authorization(client_id, verifier, state):
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    return 'https://x.com/i/oauth2/authorize?' + urllib.parse.urlencode(dict(
        response_type='code', client_id=client_id, redirect_uri=CALLBACK, scope=SCOPES,
        state=state, code_challenge=challenge, code_challenge_method='S256'))


def callback_values(path, expected_state):
    url = urllib.parse.urlsplit(path)
    values = urllib.parse.parse_qs(url.query)
    if url.path != '/callback' or not secrets.compare_digest(values.get('state', [''])[0], expected_state):
        raise ValueError('Invalid OAuth callback state')
    if 'error' in values or not values.get('code'):
        raise ValueError('X authorization was declined or returned no code')
    return values['code'][0]


def login(client_id, path):
    verifier, state = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
    outcome = {}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                code = callback_values(self.path, state)
            except ValueError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid or declined authorization. Return to your terminal.')
                return
            outcome['code'] = code
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Authorization received. Return to the terminal to confirm connection.')
        def log_message(self, *args): pass  # OAuth code must never enter access logs.
    with HTTPServer(('127.0.0.1', 8765), Handler) as server:
        server.timeout = 1
        url = authorization(client_id, verifier, state)
        print('Open this URL on this computer and authorize read-only bookmark access:\n' + url, flush=True)
        webbrowser.open(url)
        deadline = time.time() + 180
        while 'code' not in outcome and time.time() < deadline:
            server.handle_request()
    if 'code' not in outcome:
        raise ValueError('Authorization timed out; rerun connect when ready')
    tokens = token_request(dict(grant_type='authorization_code', code=outcome['code'],
                                redirect_uri=CALLBACK, client_id=client_id, code_verifier=verifier))
    save(path, client_id, tokens)
    print('Connected. Tokens saved privately with owner-only permissions; no bookmarks fetched yet.')


def fresh_token(path):
    record = json.loads(Path(path).read_text())
    if record['expires_at'] > time.time() + 60:
        return record['access_token']
    if not record.get('refresh_token'):
        raise ValueError('No refresh token; reconnect with offline.access')
    tokens = token_request(dict(grant_type='refresh_token', refresh_token=record['refresh_token'],
                                client_id=record['client_id']))
    if not tokens.get('refresh_token'):
        tokens['refresh_token'] = record['refresh_token']
    save(path, record['client_id'], tokens)
    return tokens['access_token']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token-file', required=True, help='Private gitignored token JSON; never commit')
    sub = parser.add_subparsers(dest='command', required=True)
    start = sub.add_parser('connect')
    start.add_argument('--client-id', required=True, help='OAuth 2.0 Client ID, not consumer/API key')
    run = sub.add_parser('sync')
    run.add_argument('--account', required=True)
    run.add_argument('--state-db', required=True)
    run.add_argument('--max-pages', type=int, default=1)
    run.add_argument('--page-size', type=int, default=20)
    run.add_argument('--folder')
    args = parser.parse_args()
    try:
        if args.command == 'connect':
            login(args.client_id, args.token_file)
            return 0
        token = fresh_token(args.token_file)
        command = [sys.executable, str(Path(__file__).with_name('bookmarks.py')),
                   '--state-db', args.state_db, '--account', args.account, 'sync',
                   '--max-pages', str(args.max_pages), '--page-size', str(args.page_size)]
        if args.folder: command += ['--folder', args.folder]
        return subprocess.run(command, env=dict(os.environ, X_USER_ACCESS_TOKEN=token), check=False).returncode
    except (ValueError, KeyError, OSError):
        print('X connection failed. Check local configuration and reconnect if needed. Credentials were not printed.', file=sys.stderr)
        return 1


if __name__ == '__main__': sys.exit(main())
