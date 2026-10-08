---
name: recoup-platform-connect-account
description: Connect your real Recoup account through the host's MCP OAuth sign-in and verify artist access. Use for "set up Recoup", "connect my account", "connect Claude to Recoup", "I just joined", or "log in". Use separate API credentials only for REST-only capabilities or skills-only installations.
---

# Recoup — Connect Account

Connect through the host's Recoup MCP integration at
`https://api.recoupable.dev/mcp`. The host handles OAuth, callbacks, credential
storage and refresh. The plugin contains no account credentials.

## Procedure

1. Discover the available Recoup tools. Tool prefixes vary by host; match their
   names, descriptions and schemas rather than assuming a fixed prefix.
2. If `list_artists` is available, call it to verify access. A successful empty
   list is a valid connection, not proof of a bad account. Never invent a roster.
3. If authentication is required, direct the user to the host's Recoup connection
   controls. In Claude Code, open `/mcp` and authenticate the plugin's Recoup
   server. On other hosts, use their MCP/plugin connection UI. Let the user
   complete browser sign-in and consent; never ask them to paste an OAuth token.
4. For the full business catalog, approve `mcp:tools` in the consent flow. This
   covers accessible personal and organization workspaces and includes writes,
   deletion, messages, publication and paid generation. Existing limited grants
   do not expand silently: reconnect for broader consent and refresh tools.
5. Verify with `list_artists` again. Use the returned artist identifiers for the
   next task. If multiple workspaces could fit, clarify the intended workspace.
6. Report connection success only after the read succeeds. Continue the user's
   requested task without creating an extra account or asking for an API key.

## REST-only or skills-only fallback

`npx skills add` installs instructions; it does not provision a host MCP
connection. Configure the endpoint above in the host if MCP is supported.

Some REST operations and bundled scripts are not available through MCP. For
those, use an existing `RECOUP_API_KEY` or host-provided `RECOUP_ACCESS_TOKEN`.
Keep REST authentication separate from the MCP OAuth connection; never export
MCP credentials, substitute its access token into curl, or claim all REST
endpoints are covered by the MCP catalog.

If a REST credential is needed and the user authorizes email verification:

1. Confirm an email address the user controls; never generate a throwaway one.
2. `POST https://api.recoupable.dev/api/agents/signup` with `{email}` requests a PIN.
3. `POST https://api.recoupable.dev/api/agents/verify` with `{email, code}` returns
   `api_key`. Keep the result out of messages and logs.
4. Store it only through an available secret facility, or a user-approved local
   environment file with mode `600`. Do not edit shell startup files or global
   agent instructions as part of connection setup.
5. Verify with authenticated `GET /api/accounts/id`, then continue the requested
   REST operation. Report missing access without fabricating data.

## Boundaries

- Missing environment variables do not invalidate a working MCP connection.
- Credentials, PINs and tokens never belong in the plugin, source control, or output.
- Tool availability is not permission to send, publish, delete or spend without
  the user's applicable authorization. Follow the tool's disclosed constraints.
- Connections remain usable until disconnected or revoked, subject to successful
  host token refresh. If refresh fails, use the host's reconnect flow.
