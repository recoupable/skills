# Finding jobs: the scrape and the scoring

Upwork's own search cannot filter on the only number that matters, so pull a wide
result set and score it locally.

## The scraper

Apify actor `neatrat/upwork-job-scraper`. Needs an Apify API token; read it from
the environment rather than hardcoding it, and note that `.env` values are often
quoted, so strip quotes before use.

Fetch the current input schema before composing a run, since the field list
changes:

```bash
BUILD=$(curl -s -H "Authorization: Bearer $APIFY_TOKEN" \
  "https://api.apify.com/v2/acts/neatrat~upwork-job-scraper" \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['taggedBuilds']['latest']['buildId'])")
curl -s -H "Authorization: Bearer $APIFY_TOKEN" \
  "https://api.apify.com/v2/actor-builds/$BUILD" \
  | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['data']['inputSchema'],indent=2))"
```

Input fields as of 2026-08-12: `query`, `rawUrl`, `experienceLevel`
(`entry`/`intermediate`/`expert`), `jobType` (`fixed`/`hourly`), `paymentVerified`,
`fixedPriceRange`, `hourlyRateRange`, `clientHistory` (`noHires`/`1to9Hires`/
`10+Hires`), `location`, `cookies`, `customFilters`, `page`, `pagesToScrape`,
`perPage`, `sort` (`newest`/`relevance`), `maxJobAge` (`{value, unit}`).

## The input to use

```json
{
  "query": "<keywords>",
  "jobType": ["hourly"],
  "experienceLevel": ["intermediate", "expert"],
  "paymentVerified": true,
  "clientHistory": ["1to9Hires", "10+Hires"],
  "sort": "newest",
  "maxJobAge": { "value": 4, "unit": "days" },
  "perPage": 50,
  "pagesToScrape": 4
}
```

**Deliberately omitted: `hourlyRateRange`.** It matches the posted band, which the
client writes and nothing enforces. It fails in both directions, and both were
observed in a single afternoon:

- **A good band hiding a bad payer.** Seven AI-agent postings all advertised
  respectable bands; their clients paid $5.70 to $47.49 an hour. The filter
  excluded none of them.
- **A bad band hiding a good payer.** A client posting **$15-55** had paid an
  average of **$72.17** across **$195,772** of spend at a 5.0 rating, roughly 30%
  above their own advertised ceiling. A `[60, 250]` filter discards them silently.

The band is a wish; the average paid is behavior. Apply the rate test to
`clientAvgHourlyRate` after the results land, never in the query.

`paymentVerified: true` and the `clientHistory` exclusion of `noHires` are worth
keeping in the query, because both are facts about the client rather than claims
in the posting. Including `noHires` is defensible when connects are plentiful, since
a brand-new account is unknown risk rather than known-bad risk.

`sort: "newest"` matters more than it looks. Proposal counts climb fast; a posting
under an hour old had 20 to 50 proposals in one observed case.

## Running it

```bash
RUN=$(curl -s -X POST "https://api.apify.com/v2/acts/neatrat~upwork-job-scraper/runs" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d @input.json | python3 -c "import json,sys;d=json.load(sys.stdin)['data'];print(d['id'],d['defaultDatasetId'])")
```

Runs take roughly two to three minutes. Poll `actor-runs/<id>` for `status`, then
pull `datasets/<datasetId>/items?format=json&limit=1000`.

## Fields the dataset returns

The scoring inputs are all present per row: `clientAvgHourlyRate`,
`clientTotalSpent`, `clientHireRatePercent`, `clientRating`, `proposals`,
`budget`, `jobType`, `experienceLevel`, `relativeDate`, `clientLocation`,
`allowedApplicantCountries`, `tags`, `title`, `description`, `url`.

## Scoring

Save as `scripts/score_jobs.py` in the workspace, or inline it:

```python
import json, sys

TARGET_RATE = 60          # the floor you actually want to work at
MAX_PROPOSALS = 50        # above this the odds stop justifying connects

jobs = json.load(open(sys.argv[1]))
for j in jobs:
    band = (j.get("budget") or "").replace("$", "").split("-")
    try:
        hi = float(band[1].strip())
    except (IndexError, ValueError):
        hi = None
    avg = j.get("clientAvgHourlyRate") or 0
    gap = (hi / avg) if (hi and avg) else None

    reds = []
    if avg and avg < TARGET_RATE:
        reds.append(f"pays ${avg:.0f}/hr")
    if gap and gap > 3:
        reds.append(f"band/paid gap {gap:.1f}x")
    if (j.get("proposals") or 0) >= MAX_PROPOSALS:
        reds.append(f"{j['proposals']} proposals")

    j["_reds"] = reds

for j in sorted(jobs, key=lambda x: len(x["_reds"])):
    flag = "PASS" if not j["_reds"] else "; ".join(j["_reds"])
    print(f"{len(j['_reds'])}  {j.get('title','')[:60]:60}  {flag}")
```

Only rows with zero reds go to Step 0 for the manual gate. Zero passing rows is a
normal and useful outcome; record it and change the query.

## What scans have shown

- **AI-agent and LLM-build postings are saturated and underpaid.** One scan of
  seven returned proposal counts of 83, 115, 142, 219, 292 and 433 on postings one
  to two days old, with client averages paid from $5.70 to $47.49. Not one build
  job cleared the gate.
- **Big spenders are often the worst payers.** A client with $2.8M in total spend
  paid an average of $10.40/hr. Another with $98K paid $19.04.
- **Maintenance postings are cheap at the low end.** Of eight, four advertised
  ceilings at or under $35 and one posted $3-7. The category held the two largest
  verified spenders seen ($347,900 and $218,291), and both paid around $11 and $24
  an hour.
- **Fifteen postings across two scans produced zero clean passes.** Expect that.
  The gate is doing its job when it returns nothing, and a scan that surfaces
  nothing still costs a fraction of one wasted proposal.

**When a category keeps returning saturated, low-paying work, stop querying your
own stack.** Query the client's problem instead: "inherited codebase", "previous
developer left", "app is slow", "need to stabilize before launch". Those phrasings
attract fewer bidders and select for clients who already have a budget and a live
product. Also prefer an older posting with few proposals over a fresh one with
hundreds; four days old with 12 proposals beats an hour old with 300.
