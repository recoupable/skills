---
name: recoup-content-connect-fans
description: Add Recoup's Spotify fan connection to an artist site using an existing eligible account, including site attribution, activation, the public connection button and retrieving connected fans. Use for "add login with Spotify", "connect fans to my Recoup account", or "collect Spotify fans on this release site". Works with externally built sites as well as Recoup Sites.
---

# Connect a site's fans to the artist

Use the customer's Recoup account to configure a hosted Spotify connection journey. The site contains a public link; the agent keeps the account credential private. Paths below are relative to this skill directory.

Read `references/api.md` for exact calls, responses and release dependencies. Check endpoint availability before promising this integration: this skill requires the corresponding fan-connection API, database migration, billing policy and Spotify callback to be deployed. A 404 or 503 is a setup problem, not a reason to invent an endpoint or simulate success.

## 1. Connect the customer

Prefer connected Recoup MCP tools when their actual schemas cover the operation. The host handles OAuth sign-in and secrets. For REST-only operations, reuse a credential already configured in the host's secure environment and verify it with `GET /api/accounts/id`. Never request or print credentials or put them into website code, URLs, generated screenshots or logs.

If access is missing, use the host's Recoup connection controls and retain this site task. If the required REST-only operation has no configured credential, explain the capability gap and stop that operation. Never collect emailed codes, passwords, API keys or OAuth tokens in conversation, or create a disposable identity. An empty roster can be a legitimate account.

## 2. Establish ownership and attribution

Resolve the intended artist from the authenticated roster. Use its Recoup artist account ID, not a Spotify ID or an artist row ID. If the artist does not exist, complete the platform's supported artist onboarding first. Resolve the customer workspace before creating a site; ask only if multiple choices remain ambiguous.

Reuse the existing Recoup site ID when provided. For an externally hosted site, register a Recoup site record with its artist and release URL. This record provides attribution without requiring Recoup to host or generate the website. Do not duplicate a site on every retry. Never accept an owner ID from public browser input.

## 3. Activate the existing entitlement

Read the site's current fan connection settings. Configure the final HTTPS return URL, the customer's clear marketing acceptance text, `enabled: true` and the current revision (0 when absent). Name the artist and the communication purpose in the text. The hosted journey presents it with one agreement button; Spotify presents its own permissions screen next. Do not add separate checkboxes to work around the configured journey.

If activation returns 402, explain that fan connection is unavailable with the site's current account entitlements and preserve the site and configuration. Do not display plan choices, offer an upgrade, surface payment links, create checkout sessions or buy credits. Customer consent does not turn this workflow into a purchase flow. Resume only after access is independently available and the customer asks to continue. A 503 is a service configuration issue; preserve the task and report the dependency.

## 4. Add the returned public link

Use the returned `connectUrl` as a normal anchor or full-page navigation with a clear label such as “Connect with Spotify”. Keep the visitor's existing progress so they can return to the experience. Place connection at a useful moment without making the entire experience incomprehensible behind login.

Do not expose the artist's API key, build a second Spotify client or ask the artist to supply a Spotify developer secret. Recoup owns the provider setup. The generated site needs only the public link.

The return query `recoup_spotify=connected|cancelled|failed` controls feedback only. It is not authentication, cannot identify a fan and must not authorize rewards or private content. On cancellation let the fan continue; on failure provide the same connection link for a fresh attempt. Do not automatically claim a fan has saved/followed a song, joined a mailing list delivery system or shared listening history.

## 5. Verify attribution and hand over

Have an authorized fan complete the real Spotify journey. Read the site's fans through the authenticated API and verify the new profile and separate connection, Spotify scope and marketing acceptance records. Never download the full fan list into a public repository or include personal details in deployment artifacts.

Report the site's owner, artist, configured return URL and activation state. Distinguish code implemented, paid activation enabled and live fan connection verified. If the deployment dependencies are missing, preserve the completed integration and report the exact remaining dependency.

This version captures Spotify identity and available email. It does not retain Spotify tokens, synchronize listening history, send marketing or create authenticated fan sessions. Playback is a separate capability.
