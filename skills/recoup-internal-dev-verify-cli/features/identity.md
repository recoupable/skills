# Read account identity

Users can read their account ID as plain text or get the response as JSON.

## Sub-features

- Plain text prints the accountId field.
- JSON preserves the account response.

## How to get to it (user POV)

Run `recoup whoami` or `recoup whoami --json`.

## Driving it with Node

Preconditions: the helper provides a synthetic success response containing accountId and sets a dummy key.

- Drive `whoami --json`. Expect valid JSON matching the fixture and exit zero.
- Drive `whoami`. Expect the fixture account ID on stdout and exit zero.
- Observe `GET /api/accounts/id` and the dummy `x-api-key` header at the fixture boundary.

## Gotchas

This proves CLI request construction and output handling. It does not verify a real identity provider, API-key ownership, or organization permissions.
