# Attio "Valuation Leads" funnel — schema & API recipes

The funnel is an Attio **List** named **Valuation Leads** (`api_slug: valuation_leads`)
on the **people** object. Each inbound catalog valuation creates a person record (with the
lead data) and a list entry (the funnel position).

Auth: `Authorization: Bearer $ATTIO_API_KEY`. Base: `https://api.attio.com/v2`.
List/attribute/option IDs are **workspace-specific** — discover them at runtime, don't
hardcode.

## Stages (the `stage` status attribute)

```
New → Report Delivered → Qualified → Pro Offer Sent → Pro Active (Won) → Lost
```

- **New** — valuation ran (auto-entry). Exit within ~24h.
- **Report Delivered** — welcome email + valuation PDF sent.
- **Qualified** — replied / booked / confirmed they own-or-represent the catalog AND value ≥ threshold.
- **Pro Offer Sent** — Pro trial link or pilot terms sent.
- **Pro Active (Won)** — **Stripe Pro subscription active** (the only definition of Won).
- **Lost** — no-go; set a **Lost Reason**.

## Custom funnel fields (list-entry attributes)

| Slug | Type | Use |
| --- | --- | --- |
| `catalog_value` | currency (USD) | Point-in-time estimated value; lets the board sort by $. |
| `relationship` | select | `Owner/Operator` · `Label` · `Manager` · `Collaborator` · `Fan/Other` · `Unknown`. |
| `lost_reason` | select | `Price too high` · `Not the owner/rep` · `Didn't trust the number` · `No upside / already managed` · `No response` · `Other`. |
| `owner` | actor-reference | Recoup member accountable for the lead. |

Lead data (artist, value, streams, followers, Spotify URL) lives on the **person record**
under attributes like `looked_up_artist`, `est_catalog_value`, `lifetime_streams`,
`follower_count`, `spotify_artist_url`, `email_addresses`, `lead_source` (= "Catalog Valuation").

## Recipes

### Discover the list ID

```bash
curl -s -H "Authorization: Bearer $ATTIO_API_KEY" https://api.attio.com/v2/lists \
 | jq -r '.data[] | select(.api_slug=="valuation_leads") | .id.list_id'
```

### List all leads in the funnel (with stage)

```bash
curl -s -X POST -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
 -d '{"limit":100}' "https://api.attio.com/v2/lists/$LIST/entries/query"
```

Each entry has `parent_record_id` (the person) and `entry_values.stage`.

### Read the lead's person record

```bash
curl -s -H "Authorization: Bearer $ATTIO_API_KEY" \
 "https://api.attio.com/v2/objects/people/records/$RECORD_ID"
```

### Discover select-option IDs (e.g. relationship)

```bash
curl -s -H "Authorization: Bearer $ATTIO_API_KEY" \
 "https://api.attio.com/v2/lists/$LIST/attributes/relationship/options" \
 | jq -r '.data[] | "\(.title)=\(.id.option_id)"'
```

### Enrich a funnel entry (owner + value + relationship)

```bash
curl -s -X PATCH -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
 -d '{"data":{"entry_values":{
       "owner":[{"referenced_actor_type":"workspace-member","referenced_actor_id":"'$ME'"}],
       "catalog_value":[{"currency_value":312500}],
       "relationship":[{"option":"'$REL_OPTION_ID'"}]
     }}}' \
 "https://api.attio.com/v2/lists/$LIST/entries/$ENTRY_ID"
```

### Set the person's name / socials

```bash
curl -s -X PATCH -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
 -d '{"data":{"values":{"name":[{"first_name":"Alex","last_name":"Rivera","full_name":"Alex Rivera"}],
                        "instagram":"https://www.instagram.com/example"}}}' \
 "https://api.attio.com/v2/objects/people/records/$RECORD_ID"
```

> `avatar_url` is enrichment-only (`is_writable:false`) — it cannot be set via the API.
> Attio populates it from a resolvable identity (email/social). To capture an artist image,
> store the Spotify image URL on a writable custom field instead.

### Advance the stage (after the email is sent)

```bash
# resolve the status_id once
curl -s -H "Authorization: Bearer $ATTIO_API_KEY" \
 "https://api.attio.com/v2/lists/$LIST/attributes/stage/statuses" \
 | jq -r '.data[] | "\(.title)=\(.id.status_id)"'

curl -s -X PATCH -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
 -d '{"data":{"entry_values":{"stage":[{"status":"'$REPORT_DELIVERED_STATUS_ID'"}]}}}' \
 "https://api.attio.com/v2/lists/$LIST/entries/$ENTRY_ID"
```

### Get the artist image (no Recoup quota, no auth)

```bash
curl -s "https://open.spotify.com/oembed?url=$SPOTIFY_ARTIST_URL" | jq -r .thumbnail_url
```
