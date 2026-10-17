# Report credential and API errors

Users receive an actionable error when a key is missing or the API rejects a request.

## Sub-features

- Missing credentials fail before a request is sent.
- A status/message response prints the API message.
- A status/error response prints the API error.

## How to get to it (user POV)

Run `recoup whoami` without RECOUP_API_KEY. The same command can receive a rejected-key response. Run `recoup whoami --json` to check a forbidden response.

## Driving it with Node

Preconditions: the helper removes the key for one case and supplies synthetic HTTP 401 and 403 responses for the others.

- Missing key. Expect exit one, the RECOUP_API_KEY instruction on stderr, and zero HTTP requests.
- HTTP 401. Expect exit one and the fixture's message field on stderr.
- HTTP 403. Expect exit one and the fixture's error field on stderr, including with `--json`.

## Gotchas

The fixture intentionally covers two response-envelope shapes. It does not establish that either shape is the universal backend contract. Each network case must produce one observed request; an error printed without reaching the boundary is insufficient evidence.
