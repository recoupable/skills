# Connection and execution

Verified documentation routes (2026-10-23):
- https://docs.x.com/x-api/posts/bookmarks/introduction
- https://docs.x.com/x-api/users/get-bookmarks
- https://docs.x.com/fundamentals/authentication/oauth-2-0/authorization-code

Use the X developer app's OAuth 2.0 authorization-code flow with PKCE and user consent.
Request read scopes `tweet.read users.read bookmark.read`; a persistent runner also needs
`offline.access` and secure refresh-token rotation. An app-only bearer token cannot read a user's
private bookmarks. The user ID must belong to the authenticated user. Confirm API entitlement and
pricing in the owner's developer account before paid reads; this skill neither buys credits nor
provisions a developer app. Do not paste tokens into chat, flags, files in Git or logs.

The runner must inject a current `X_USER_ACCESS_TOKEN`. For a local public/native app, the bundled `scripts/x_auth.py` manages PKCE and atomic refresh-token
rotation in an explicitly selected private token file. A hosted runner can inject its own managed token.
An expired token fails with an actionable message. No automatic retries that could consume an
unbounded budget. The default batch is one API request for 20 posts. API responses and fixtures use
X API v2 objects; field naming may evolve, so a successful live pilot is required before scheduling.

The CLI requests the current documented `post.fields` and `referenced_posts` expansions, and
accepts both `note_tweet`/`note_post` and `includes.tweets`/`includes.posts` response names.
A successful live pilot is still required before scheduling. Do not silently retry paid requests
with guessed field combinations.

Commands below run from the installed skill directory; replace absolute example paths with the
selected private workspace and durable state location. Scripts are bundled beside the skill.

```sh
python3 scripts/bookmarks.py --state-db /private/runtime/x-bookmarks.sqlite --account 123456 sync --page-size 20 --max-pages 1
python3 scripts/bookmarks.py --state-db /private/runtime/x-bookmarks.sqlite --account 123456 import --input /private/work/bookmarks.json
python3 scripts/bookmarks.py --state-db /private/runtime/x-bookmarks.sqlite --account 123456 queue --limit 20
python3 scripts/bookmarks.py --state-db /private/runtime/x-bookmarks.sqlite --account 123456 decide --post-id 1001 --decision /private/work/decision.json --workspace /private/business
```

`sync --folder NUMERIC_FOLDER_ID` scopes capture to a selected folder. The token is supplied through
the environment by the connection manager. Keep the SQLite database on a local durable filesystem,
not an ephemeral runner or network-shared drive. Use one importer/decision writer at a time. Back it
up privately; deleting it loses capture and skip history. Existing signal files are still protected
against overwrites, but dedup by source/angle must be repeated after a restore.

`queue` prints source text intentionally for the reviewing agent. Treat its output as private.
The DB preserves the first capture; live edits/deletions are checked again at drafting time.
A valid empty response is `{"data": [], "meta": {"result_count": 0}}`. Partial API errors fail the page.
Thread completeness and linked-page research are agent work, not implied by returned API context.

## Local connection (public/native app)

In X's User authentication settings choose OAuth 2.0 Native App (public client), callback
`http://127.0.0.1:8765/callback`, and the workspace's public website URL. Save the OAuth 2.0 Client ID;
it is different from the consumer/API key. Do not use app-only bearer credentials.

```sh
python3 scripts/x_auth.py --token-file /private/runtime/x-token.json connect --client-id YOUR_OAUTH2_CLIENT_ID
python3 scripts/x_auth.py --token-file /private/runtime/x-token.json sync --account YOUR_NUMERIC_X_USER_ID --state-db /private/runtime/x-bookmarks.sqlite --max-pages 1 --page-size 20
```

The connection opens the system browser, listens on loopback for up to three minutes, validates
OAuth state, exchanges the code using S256 PKCE, and saves tokens with mode 0600. No token is printed.
The refresh-aware sync wrapper supplies the token to the importer through its child environment.
Run one wrapper at a time to avoid concurrent refresh-token rotation. Keep both token file and DB
outside Git and back them up securely. An app configured as a confidential web app requires a different
OAuth client configuration; this helper intentionally supports public/native clients only.
