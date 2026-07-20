# SQL pack — weekly usage review

All read-only, against the production Supabase project. Replace `:FROM` / `:TO`
with the window bounds (UTC, `TO` exclusive). Prior week = same queries shifted
back 7 days.

## Credits & activity

```sql
-- 1. Schema discovery (run first if tables have drifted)
SELECT table_name, column_name, data_type FROM information_schema.columns
WHERE table_schema='public' AND table_name IN
  ('usage_events','credits_usage','account_emails','accounts',
   'scheduled_actions','chats','sessions','email_send_log')
ORDER BY table_name, ordinal_position;

-- 2. Per-account consumption in window
SELECT ue.account_id, ae.email, a.name, COUNT(*) AS events,
  SUM(ue.credits_deducted_cents) AS cents_used,
  MIN(ue.created_at) AS first_event, MAX(ue.created_at) AS last_event
FROM usage_events ue
LEFT JOIN accounts a ON a.id = ue.account_id
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = ue.account_id LIMIT 1) ae ON true
WHERE ue.created_at >= :FROM AND ue.created_at < :TO
GROUP BY ue.account_id, ae.email, a.name ORDER BY cents_used DESC;

-- 3. Model / flat-fee split (for the gateway reconciliation)
SELECT model, COUNT(*), SUM(credits_deducted_cents) AS cents
FROM usage_events
WHERE created_at >= :FROM AND created_at < :TO
GROUP BY model ORDER BY cents DESC;   -- NULL model = flat-fee (research/scrape), not gateway-backed

-- 4. Balances for window-active accounts (negative = burning past zero)
SELECT cu.account_id, ae.email, cu.remaining_credits, cu.timestamp
FROM credits_usage cu
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = cu.account_id LIMIT 1) ae ON true
WHERE cu.account_id IN (SELECT DISTINCT account_id FROM usage_events
  WHERE created_at >= :FROM AND created_at < :TO)
ORDER BY cu.remaining_credits ASC;

-- 5a. Chats per account in window (scheduled + interactive)
SELECT s.account_id, ae.email, COUNT(DISTINCT c.id) AS chats_in_window,
  ARRAY_AGG(DISTINCT c.title) FILTER (WHERE c.title IS NOT NULL) AS titles
FROM chats c JOIN sessions s ON s.id = c.session_id
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = s.account_id LIMIT 1) ae ON true
WHERE c.updated_at >= :FROM AND c.updated_at < :TO
GROUP BY s.account_id, ae.email ORDER BY chats_in_window DESC;

-- 5b. Interactive-only accounts (cross-check for Privy session-riders)
SELECT s.account_id, ae.email,
  COUNT(*) FILTER (WHERE c.title IS DISTINCT FROM 'Scheduled generation')
    AS interactive_chats,
  MIN(c.updated_at) AS first_seen, MAX(c.updated_at) AS last_seen
FROM chats c JOIN sessions s ON s.id = c.session_id
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = s.account_id LIMIT 1) ae ON true
WHERE c.updated_at >= :FROM AND c.updated_at < :TO
GROUP BY s.account_id, ae.email
HAVING COUNT(*) FILTER (WHERE c.title IS DISTINCT FROM 'Scheduled generation') > 0
ORDER BY interactive_chats DESC;

-- 6. Enabled scheduled tasks for window-active accounts
--    (last_run is dead — do NOT filter on it; look for duplicate rows per account)
SELECT sa.account_id, ae.email, sa.title, sa.schedule, sa.enabled,
  a2.name AS artist_name
FROM scheduled_actions sa
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = sa.account_id LIMIT 1) ae ON true
LEFT JOIN accounts a2 ON a2.id = sa.artist_account_id
WHERE sa.enabled = true AND sa.account_id IN
  (SELECT DISTINCT account_id FROM usage_events
   WHERE created_at >= :FROM AND created_at < :TO)
ORDER BY ae.email NULLS LAST, sa.title;

-- 7. Emails sent per account in window
SELECT esl.account_id, ae.email, COUNT(*) AS emails,
  COUNT(*) FILTER (WHERE esl.status='sent') AS sent_ok
FROM email_send_log esl
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = esl.account_id LIMIT 1) ae ON true
WHERE esl.created_at >= :FROM AND esl.created_at < :TO
GROUP BY esl.account_id, ae.email ORDER BY emails DESC;

-- 8. Went silent (active prior week, zero this week — churn signal)
WITH prior AS (SELECT account_id, SUM(credits_deducted_cents) AS prior_cents,
    COUNT(*) AS prior_events
  FROM usage_events
  WHERE created_at >= :FROM - interval '7 days' AND created_at < :FROM
  GROUP BY account_id),
cur AS (SELECT DISTINCT account_id FROM usage_events
  WHERE created_at >= :FROM AND created_at < :TO)
SELECT p.account_id, ae.email, p.prior_cents, p.prior_events
FROM prior p LEFT JOIN cur c ON c.account_id = p.account_id
LEFT JOIN LATERAL (SELECT email FROM account_emails
  WHERE account_id = p.account_id LIMIT 1) ae ON true
WHERE c.account_id IS NULL ORDER BY p.prior_cents DESC;

-- 9. Daily totals (spike detection; expect a Monday cron pile-up)
SELECT date_trunc('day', created_at)::date AS day, COUNT(*) AS events,
  SUM(credits_deducted_cents) AS cents
FROM usage_events WHERE created_at >= :FROM AND created_at < :TO
GROUP BY 1 ORDER BY 1;

-- 10. Account-less email rejects (pipeline noise worth tracing if large)
SELECT status, COUNT(*) FROM email_send_log
WHERE created_at >= :FROM AND created_at < :TO AND account_id IS NULL
GROUP BY status;
```

## Catalogs

```sql
-- 11. Per-catalog lifetime streams (latest measurement per song)
WITH latest AS (
  SELECT DISTINCT ON (sm.song) sm.song, sm.value, sm.captured_at
  FROM song_measurements sm
  WHERE sm.platform='spotify' AND sm.metric='platform_displayed_play_count'
  ORDER BY sm.song, sm.captured_at DESC)
SELECT c.id, c.name, c.created_at::date, COUNT(DISTINCT cs.song) AS songs,
  COALESCE(SUM(l.value),0) AS total_streams, MAX(l.captured_at)::date AS measured
FROM catalogs c
LEFT JOIN catalog_songs cs ON cs.catalog = c.id
LEFT JOIN latest l ON l.song = cs.song
GROUP BY c.id, c.name, c.created_at ORDER BY total_streams DESC;

-- 12. Catalog owners
SELECT ac.catalog, c.name AS catalog_name, a.name AS owner, ae.email
FROM account_catalogs ac
JOIN catalogs c ON c.id = ac.catalog
LEFT JOIN accounts a ON a.id = ac.account
LEFT JOIN account_emails ae ON ae.account_id = ac.account;

-- 13. Valuation runs in window (schedule='once' = one-off customer valuations;
--     rows with a NULL catalog are measured-but-unclaimed → warm leads)
SELECT ps.created_at::date, ae.email, ps.album_count, ps.state, ps.catalog
FROM playcount_snapshots ps
LEFT JOIN account_emails ae ON ae.account_id = ps.account
WHERE ps.created_at >= :FROM AND ps.created_at < :TO
ORDER BY ps.created_at;

-- 14. Paying-status cross-check (mirror may be EMPTY — trust Stripe, not this)
SELECT count(*) FROM subscriptions;
```
