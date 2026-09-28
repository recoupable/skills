# Fan connection API contract

Release dependency: these routes require the site fan connection API release and its database migration. The skill alone does not enable them. Base URL: `https://api.recoupable.dev`.

Private calls use `x-api-key: $RECOUP_API_KEY` (or the platform's existing bearer authentication). Customer credentials stay with the agent/server. Public connection entry and callback use browser-bound OAuth state, not the customer API key.

## Customer and site

- `GET /api/accounts/id`: verify the current credential.
- `POST /api/agents/signup` with `{ "email": "customer@example.com" }`: request email verification.
- `POST /api/agents/verify` with `{ "email": "customer@example.com", "code": "123456" }`: receive `api_key`; never echo it.
- `GET /api/artists`: inspect the caller's roster and choose the artist's account ID.
- `GET /api/sites`: inspect existing site records.
- `POST /api/sites` with `{ "name": "Release experience", "artistId": "ARTIST_ACCOUNT_UUID", "releaseUrl": "https://open.spotify.com/track/TRACK_ID" }`: register a site. Add `organizationId` only for a selected authorized workspace. Read the returned `site.id`. Omit owner/account ID fields; ownership comes from authentication.

## Configure

`GET /api/sites/{siteId}/fan-connection` returns:

```json
{
  "siteId": "SITE_UUID",
  "ownerId": "WORKSPACE_ACCOUNT_UUID",
  "artistId": "ARTIST_ACCOUNT_UUID",
  "config": null,
  "connectUrl": null
}
```

Existing `config` contains `site_id`, `return_url`, `marketing_text`, `enabled` and `revision`. Update with `PUT /api/sites/{siteId}/fan-connection`:

```json
{
  "returnUrl": "https://artist.example/release",
  "marketingText": "I agree to receive release announcements and offers by email from Example Artist.",
  "enabled": true,
  "revision": 0
}
```

Use the real artist's approved text, not the example unchanged. Return URL must be HTTPS, at most 2048 characters, without credentials or fragments. Text length is 20–1000 characters. Pass the last read revision, or 0 for initial configuration. The response has the same envelope with persisted config and the public `connectUrl`; always use that returned URL.

- 400: invalid input or missing artist attribution.
- 401/403: reconnect the customer or select an authorized workspace.
- 402: no eligible paid subscription for the site's owning account.
- 404: missing site or API not deployed; inspect the actual response.
- 409: another configuration update won; reload and reconcile before retry.
- 503: provider, billing or storage unavailable; surface the dependency.

Spotify fan connection is included in an active paid Recoup subscription owned by the site's workspace. No separate add-on is required. Existing `POST /api/subscriptions/sessions` accepts `{plan: "starter" | "pro", successUrl, cancelUrl?}` and returns the customer checkout URL. Let the customer complete payment; then retry activation. Fans do not buy this feature.

## Public fan journey

`GET /api/sites/public/{siteId}/spotify` displays the site's agreement. Its own form POST binds acceptance to that browser and configuration revision, then redirects to Spotify PKCE authorization. Do not handcraft this POST or bypass the page. Spotify returns to Recoup's `/api/sites/spotify/callback`; Recoup then returns to the configured site URL with `recoup_spotify=connected`, `cancelled` or `failed`.

Only a successful provider exchange with `user-read-email` and `user-read-private` creates records. Actual granted scopes and the exact accepted marketing text are retained separately from the successful connection. Email may be absent. No tokens or profile details are passed to the public site.

## Read fans

`GET /api/sites/{siteId}/fans?offset=0&limit=50` (private):

```json
{
  "fans": [],
  "total": 0,
  "offset": 0,
  "limit": 50
}
```

Each fan has `id`, `site_id`, `spotify_id`, `display_name`, `email`, first/last connection timestamps and nested `site_fan_connections` with `site_fan_permissions` and `site_fan_marketing_consents`. Paginate up to 100 fans per page. Records are private to authorized workspace members. Read access remains available after paid eligibility expires. Repeated connection updates the existing fan for that site and adds a connection history entry. The site's owner and artist supply attribution. These records are separate from email-only signups and other artist audience data.

## Recoup operator setup

Operators must apply `20260928010000_site_fan_connections.sql`, configure `SITES_SPOTIFY_CLIENT_ID`, register an HTTPS callback ending `/api/sites/spotify/callback`, set `SITES_FAN_SPOTIFY_REDIRECT_URI`. This is Recoup service configuration, not work to impose on each artist. The existing browser playback callback remains separate.

## Activity reporting

`GET /api/sites/{siteId}/activity` returns 30-day counts for visits, starts, completions, replays and shares to authorized workspace members. `POST /api/sites/public/{siteId}/activity` accepts `{id: EVENT_UUID, visitId: VISIT_UUID, event: "visit" | "start" | "complete" | "replay" | "share"}`. Reuse the event UUID when retrying. Use a site-scoped visit ID. Never send emails, profile data or arbitrary page contents to this endpoint. These are browser-reported interactions, not verified Spotify listening or a named fan activity history.

Recoup-hosted generated sites use the trusted host bridge: `window.recoup.track(event)` reports approved events; `window.recoup.join()` reveals the trusted signup controls. External sites should implement the equivalent fixed-event transport and keep account credentials on the server.
