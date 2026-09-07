# Recoup music generation contract

Reviewed 2026-09-07 against Recoup's API implementation and OpenAPI contract.
Check the current contract before generation if fields, pricing, or behavior have changed.

- [Generate](https://docs.recoupable.dev/api-reference/music/generate)
- [Read one generation](https://docs.recoupable.dev/api-reference/music/get)
- [List generations](https://docs.recoupable.dev/api-reference/music/list)
- [OpenAPI](https://docs.recoupable.dev/api-reference/openapi/content.json)
- [Request validator](https://github.com/recoupable/api/blob/main/lib/music/validateCreateMusicBody.ts)
- [Recoup music pricing](https://github.com/recoupable/api/blob/main/lib/music/creditCostForDuration.ts)
- [Completed-generation billing](https://github.com/recoupable/api/blob/071ff9b6dd02fa338128b193713604dd989f5dc1/lib/music/creditsForCompletedGeneration.ts)

## Authenticate and resolve ownership before the call gate

Base: `https://api.recoupable.dev/api`. Use
`Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}` from the authenticated environment.
Never print the credential or put it in a request artifact. If neither variable is available,
use the environment's established Recoup authentication flow or ask the user to connect.
Do not fall back to a provider key.

Read `GET /api/accounts/id` to verify the current identity. Confirm the intended account or
organization in the request preview. Omit `account_id` only when the authenticated account is
indeed the intended owner. Otherwise pass its verified UUID; do not invent one or silently
use a test account. Organizations use `account_id`, not `organization_id`.

## Prepare the approved JSON body

| Field | Contract |
|---|---|
| `prompt` | Required nonempty string: exact approved structured caption |
| `lyrics` | Required nonempty string: exact approved tagged lyrics; for instrumental music use section tags without sung words |
| `duration` | Seconds, 10–300 inclusive; API default 60. **Skill default: explicitly send 300**, the supported maximum, unless the user requests a shorter API limit. Output duration may differ. |
| `account_id` | Optional UUID ownership override, authorized by the API |
| `seed` | Optional integer; include only when part of the reviewed request |
| `num_inference_steps` | Optional integer, 1–100, default 30; normally omit |
| `guidance_scale` | Optional number, 0–20, default 1.7; normally omit |

The request schema is strict: extra fields fail. There is no `model`, `title`, `instructions`,
`input`, or `organization_id` request field. MiniMax Music 3 is selected by Recoup internally.
Store the body as JSON through a serializer; preserve actual newlines in prompt/lyrics.
Never interpolate those strings into shell source.

Treat the maximum request as headroom for the full song, not its intended musical length.
Do not substitute a runtime estimate for `duration`, omit the field, or pad the composition
to fill the maximum. Verify the supported maximum before generation.

Historical pricing snapshot: Recoup source on 2026-09-07 set music to $0.002 per output second,
with pass-through pricing and credit conversion. Verify the current rate and credit unit before
showing an estimate. Requested duration governs the credit precheck and maximum quote.
Successful billing uses the provider-reported actual output duration, capped at that quote.
If the reported duration is missing, non-finite, or non-positive, the API instead charges the
requested-duration quote. At this snapshot's rate, a 300-second request requires a $0.60
credit precheck; a valid 150-second output costs $0.30, while missing duration falls back to
$0.60. This is why the skill requests maximum headroom by default without promising an
unconditional actual-only charge. Do not report an estimate as an observed deduction. Failed generations
are documented as uncharged; plan/subscription fees are not part of this generation estimate.

## Submit only after gate 4

The `request.json` below must contain the exact payload the user approved. The skill does not
execute this command while drafting or preparing the request.

```bash
curl --silent --show-error --fail-with-body \
  -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  -H 'Content-Type: application/json' \
  --data-binary @request.json \
  https://api.recoupable.dev/api/music
```

Expect HTTP **202**, `{ "status": "success", "generation": { "id": "...", "status": "pending", ... } }`.
Top-level `status: success` means accepted, not ready to play. Save `generation.id` immediately.
Read `GET /api/music/{generationId}` with the same auth and any documented account scope.
Inspect `generation.status`: `pending` and `processing` are nonterminal; `completed` and `failed`
are terminal. A completed generation supplies `generation.audio_url`; read it from the response,
never construct a provider URL. GET responses are not song generations.

Poll about every 10 seconds, giving progress updates. After ten minutes of nonterminal results,
report the pending ID and resume polling later rather than submitting another take.
On `failed`, preserve the ID and report `error_message`; ask before any re-roll.

If POST times out after it may have been accepted, don't assume it failed. Reconcile with
`GET /api/music` using the intended account, recent creation time and approved inputs. If still
ambiguous, report that ambiguity and request direction before risking a duplicate paid generation.
There is no documented idempotency-key request field.

Handle 400 by reviewing validation errors, 401/403 by resolving authentication/access, and 402
by reporting insufficient credits. Do not change an approved creative payload or charged account
as an automatic error workaround. No automatic purchases, account switching, or provider fallback.
