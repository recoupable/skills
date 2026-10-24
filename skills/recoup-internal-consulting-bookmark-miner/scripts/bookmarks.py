#!/usr/bin/env python3
"""Bounded X capture and editorial queue. Python standard library only."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,20}", value):
        raise ValueError("Expected a numeric X ID as a string")
    return value


def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    os.chmod(path, 0o600)
    db.row_factory = sqlite3.Row
    db.executescript('''
    CREATE TABLE IF NOT EXISTS bookmarks (
      account TEXT NOT NULL, id TEXT NOT NULL, payload TEXT NOT NULL,
      first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
      state TEXT NOT NULL DEFAULT 'pending', decision TEXT,
      PRIMARY KEY(account,id));
    CREATE TABLE IF NOT EXISTS runs (
      started TEXT NOT NULL, account TEXT NOT NULL, pages INTEGER NOT NULL,
      complete INTEGER NOT NULL, added INTEGER NOT NULL);
    ''')
    return db


def normalize(page):
    if not isinstance(page, dict):
        raise ValueError("Expected an X API response object")
    if page.get('errors'):
        raise ValueError("X returned partial errors; nothing from this page was saved")
    rows = page.get('data', [])
    if not isinstance(rows, list):
        raise ValueError("Response data must be a list")
    if 'data' not in page and page.get('meta', {}).get('result_count') != 0:
        raise ValueError("Response has neither data nor an explicit empty result")
    includes = page.get('includes', {})
    users = {u['id']: u for u in includes.get('users', [])}
    references = includes.get('tweets', includes.get('posts', []))
    records = []
    for row in rows:
        post_id = identifier(row.get('id'))
        text = row.get('note_tweet', row.get('note_post', {})).get('text') or row.get('text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Post is unavailable or missing text")
        referenced = row.get('referenced_tweets', row.get('referenced_posts', []))
        wanted = {r['id'] for r in referenced}
        records.append(dict(id=post_id, url=f'https://x.com/i/status/{post_id}', text=text,
                            author=users.get(row.get('author_id'), {'id': row.get('author_id')}),
                            published_at=row.get('created_at'), entities=row.get('entities', {}),
                            references=referenced,
                            context=[r for r in references if r.get('id') in wanted],
                            context_status='needs_review', evidence_status='unverified'))
    return records


def ingest(db, account, page):
    records = normalize(page)  # Validate the entire page before changing state.
    added = 0
    with db:
        for record in records:
            stamp = now()
            existing = db.execute('SELECT payload FROM bookmarks WHERE account=? AND id=?',
                                  (account, record['id'])).fetchone()
            # Keep the first snapshot and its editorial decision stable on repeated polls.
            if existing:
                db.execute('UPDATE bookmarks SET last_seen=? WHERE account=? AND id=?',
                           (stamp, account, record['id']))
            else:
                db.execute('INSERT INTO bookmarks(account,id,payload,first_seen,last_seen) VALUES(?,?,?,?,?)',
                           (account, record['id'], json.dumps(record), stamp, stamp))
                added += 1
    return added


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_page(url, token):
    request = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not emit provider response bodies, tokens or request headers.
        hints = {401: 'Reconnect X: user access token expired or invalid.',
                 403: 'Check account identity, bookmark.read scope and API entitlement.',
                 429: 'Rate limited; retry later. Saved pages remain intact.'}
        raise ValueError(hints.get(exc.code, f'X request failed (HTTP {exc.code}); retry later.')) from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError('X request failed; check connectivity and retry.') from None


def sync(db, account, token, max_pages=1, page_size=20, folder=None, fetch=request_page):
    if not 1 <= max_pages <= 100 or not 1 <= page_size <= 100:
        raise ValueError('Use 1–100 pages and 1–100 results per page')
    endpoint = f'https://api.x.com/2/users/{identifier(account)}/bookmarks'
    if folder:
        endpoint += f'/folders/{identifier(folder)}'
    cursor, seen, added, complete = None, set(), 0, False
    started = now()
    for page_number in range(max_pages):
        query = {'max_results': page_size, 'post.fields': 'created_at,entities,note_post',
                 'expansions': 'author_id,referenced_posts', 'user.fields': 'username,name'}
        if cursor:
            query['pagination_token'] = cursor
        page = fetch(endpoint + '?' + urllib.parse.urlencode(query), token)
        added += ingest(db, account, page)
        cursor = page.get('meta', {}).get('next_token')
        if not cursor:
            complete = True
            break
        if cursor in seen:
            raise ValueError('X repeated a pagination cursor; retry later')
        seen.add(cursor)
    with db:
        db.execute('INSERT INTO runs VALUES(?,?,?,?,?)',
                   (started, account, page_number + 1, int(complete), added))
    # Every poll starts at the newest page; old post publication dates are irrelevant.
    return {'added': added, 'pages': page_number + 1, 'complete': complete,
            'bounded': not complete, 'next_action': None if complete else 'Increase --max-pages to cover the remaining bookmarks'}


def queue(db, account, state='pending', limit=20):
    return [dict(json.loads(r['payload']), first_seen=r['first_seen'], state=r['state'],
                 decision=json.loads(r['decision']) if r['decision'] else None)
            for r in db.execute('SELECT * FROM bookmarks WHERE account=? AND state=? ORDER BY first_seen,id LIMIT ?',
                                (account, state, limit))]


def decide(db, account, post_id, decision, workspace):
    """Persist an agent's reviewed decision; facts and editorial merit are agent checks."""
    row = db.execute('SELECT * FROM bookmarks WHERE account=? AND id=?', (account, identifier(post_id))).fetchone()
    if not row:
        raise ValueError('Bookmark was not captured for this account')
    state = decision.get('state')
    if state not in ('skipped', 'needs-research', 'promoted', 'linked'):
        raise ValueError('Decision state must be skipped, needs-research, promoted or linked')
    if not isinstance(decision.get('reason'), str) or not decision['reason'].strip():
        raise ValueError('Every decision needs a reason')
    if row['state'] in ('promoted', 'linked'):
        if json.loads(row['decision']) == decision:
            return {'state': row['state'], 'repeated': True}
        raise ValueError('Already promoted/linked; preserve its lifecycle and review manually')
    root = Path(workspace).resolve()
    source = json.loads(row['payload'])
    target = None
    if state in ('promoted', 'linked'):
        signal_id = decision.get('signal_id', '')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*', signal_id):
            raise ValueError('signal_id must be YYYY-MM-DD-slug')
        dt.date.fromisoformat(signal_id[:10])
        target = root / 'signals' / (signal_id + '.md')
        if not target.resolve().is_relative_to(root) or target.is_symlink():
            raise ValueError('Signal destination escapes workspace')
        if state == 'linked':
            if not target.is_file() or source['url'] not in target.read_text():
                raise ValueError('Linked signal must exist and already cite this bookmark URL')
        else:
            for key in ('topic', 'hook', 'intent', 'body', 'evidence'):
                if not isinstance(decision.get(key), str) or not decision[key].strip():
                    raise ValueError(f'Missing {key}')
            if decision.get('verification') not in ('primary-source-checked', 'attributed-opinion'):
                raise ValueError('Verify primary evidence or label an attributed opinion before promotion')
            formats = decision.get('formats')
            if not isinstance(formats, list) or not formats or any(f not in ('linkedin', 'article', 'email', 'x', 'video') for f in formats):
                raise ValueError('Supply supported formats')
            kind = decision.get('type', 'content-idea')
            if kind not in ('content-idea', 'market-signal', 'insight'):
                raise ValueError('Unsupported signal type')
            meta = dict(id=signal_id, type=kind, topic=decision['topic'], hook=decision['hook'],
                        intent=decision['intent'], formats=formats,
                        source={'type': 'research', 'ref': source['url'], 'locator': f"X post {post_id}"},
                        related=[], status='evergreen' if kind == 'insight' else 'new',
                        used_by=None, used_date=None)
            # JSON scalars/objects are valid YAML; no YAML dependency or unsafe interpolation.
            front = '\n'.join(f'{key}: {json.dumps(value, ensure_ascii=False)}' for key, value in meta.items())
            text = f"---\n{front}\n---\n\n# {decision['hook']}\n\n{decision['body']}\n\n## Evidence\n\n{decision['evidence']}\n\nVerification: {decision['verification']}.\n"
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.read_text() != text:
                    raise ValueError('Signal already exists with different content; refusing overwrite')
            else:
                # Exclusive create plus SQLite serialization makes concurrent retries non-destructive.
                with target.open('x') as output:
                    output.write(text)
    with db:
        db.execute('UPDATE bookmarks SET state=?,decision=? WHERE account=? AND id=?',
                   (state, json.dumps(decision, sort_keys=True), account, post_id))
    return {'state': state, 'signal': str(target) if target else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-db', required=True, help='Private durable SQLite path; keep outside Git')
    parser.add_argument('--account', required=True, type=identifier)
    sub = parser.add_subparsers(dest='command', required=True)
    imp = sub.add_parser('import', help='Import an explicitly supplied X API JSON response, offline')
    imp.add_argument('--input', required=True)
    live = sub.add_parser('sync', help='Read X bookmarks using X_USER_ACCESS_TOKEN from the environment')
    live.add_argument('--max-pages', type=int, default=1)
    live.add_argument('--page-size', type=int, default=20)
    live.add_argument('--folder', type=identifier)
    pending = sub.add_parser('queue')
    pending.add_argument('--state', choices=['pending', 'needs-research', 'skipped', 'promoted', 'linked'], default='pending')
    pending.add_argument('--limit', type=int, default=20)
    resolution = sub.add_parser('decide')
    resolution.add_argument('--post-id', required=True, type=identifier)
    resolution.add_argument('--decision', required=True, help='Path to reviewed decision JSON')
    resolution.add_argument('--workspace', required=True)
    args = parser.parse_args()
    try:
        with connect(args.state_db) as db:
            if args.command == 'import':
                result = {'added': ingest(db, args.account, json.loads(Path(args.input).read_text()))}
            elif args.command == 'sync':
                token = os.environ.get('X_USER_ACCESS_TOKEN')
                if not token:
                    raise ValueError('Set X_USER_ACCESS_TOKEN securely; never pass it as a CLI argument')
                result = sync(db, args.account, token, args.max_pages, args.page_size, args.folder)
            elif args.command == 'queue':
                if not 1 <= args.limit <= 100:
                    raise ValueError('Queue limit must be 1–100')
                result = queue(db, args.account, args.state, args.limit)
            else:
                result = decide(db, args.account, args.post_id, json.loads(Path(args.decision).read_text()), args.workspace)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as exc:
        # JSON decoder and filesystem messages can contain user data; keep failures bounded.
        print(str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError)
              else 'Could not read/write local state or parse input; inspect the supplied paths.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
