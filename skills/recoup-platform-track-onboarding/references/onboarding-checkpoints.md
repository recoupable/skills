# Recoup onboarding checkpoints

The activation funnel for a Recoup account, in order. Derived from how retained
accounts actually behave: every long-lived, revenue-relevant account converges
on claimed artists with connected socials running scheduled tasks; every ghost
account stalls before step 7.

**Activation bar: claim a catalog AND schedule a first recurring task within
week one.** Steps 1–6 are setup; step 7 is the habit loop that predicts
retention; step 8 is the outcome, not a step to push.

| # | Checkpoint | Owner-token API check | Internal check (staff) |
|---|---|---|---|
| 1 | Account created | `GET /api/accounts/id` succeeds | Privy user + `accounts` row |
| 2 | Artist added to roster | `GET /api/artists` non-empty | `account_artist_ids` rows |
| 3 | Socials connected | `GET /api/artists/{id}/socials` non-empty | `account_socials` rows for the artist accounts |
| 4 | First interactive chat | `GET /api/chats` has a chat not titled "Scheduled generation" | `chats` via `sessions`, same title filter |
| 5 | Valuation run | catalog endpoints show measured songs | `playcount_snapshots` rows |
| 6 | Catalog claimed | `GET /api/catalogs` (owned) non-empty | `account_catalogs` rows |
| 7 | Scheduled task enabled | `GET /api/tasks` has an enabled task | `scheduled_actions` where `enabled` |
| 8 | Paying | `GET /api/accounts/{id}/subscription` → `isPro` | Stripe (the DB `subscriptions` mirror can be empty — trust Stripe) |

Scoring: report the furthest **contiguous** step reached plus any skipped steps
(e.g. "chatted but never added an artist" is a routing failure worth flagging,
not credit for step 4). Also record credits used vs remaining and whether the
account returned on any day after signup — day-2 return is the earliest
retention signal.
