#!/usr/bin/env bash
# Source these one-request REST examples after reading the skill's identity checks.
# They use an already configured Recoup credential; sourcing makes no request.

roster_post_artist() {
  local body="$1" response status payload artist_id outcome
  local token="${RECOUP_API_KEY:-${RECOUP_ACCESS_TOKEN:-}}"
  [ -n "$token" ] || { echo 'Configure a Recoup credential first.' >&2; return 1; }
  response=$(curl -sS --max-time 90 -X POST \
    -H "Authorization: Bearer $token" -H 'Content-Type: application/json' \
    --data "$body" -w '\n%{http_code}' https://api.recoupable.dev/api/artists) || {
    echo 'Request outcome unknown. Keep the checkpoint and reconcile before another mutation.' >&2
    return 1
  }
  status="${response##*$'\n'}"; payload="${response%$'\n'*}"
  case "$status" in
    200) outcome=reused ;;
    201) outcome=created ;;
    *) printf 'HTTP %s; stop and preserve the checkpoint: %s\n' "$status" "$payload" >&2; return 1 ;;
  esac
  artist_id=$(printf '%s' "$payload" | jq -er '
    .artist | select(type == "object") |
    select(.id == null or .account_id == null or .id == .account_id) |
    (.account_id // .id) | select(type == "string" and length > 0)') || {
    echo 'Missing or conflicting returned artist ID. Reconcile; do not create another profile.' >&2
    return 1
  }
  jq -cn --argjson request "$body" --arg id "$artist_id" --argjson status "$status" --arg outcome "$outcome" \
    '{spotify_artist_id:($request.spotify_artist_id // null), organization_id:$request.organization_id,
      artist_account_id:$id, create_http_status:$status, outcome:$outcome}'
}

onboard_spotify_artist() {
  local body
  body=$(jq -cen --arg name "$1" --arg spotify "$2" --arg org "$3" '
    select(($name | length) > 0 and ($spotify | test("^[A-Za-z0-9]{22}$")) and
      ($org | test("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"))) |
    {name:$name, spotify_artist_id:$spotify, organization_id:$org}') || {
    echo 'Use a verified exact Spotify artist ID and the requested organization UUID.' >&2
    return 1
  }
  roster_post_artist "$body"
}

onboard_manual_artist() {
  local body
  [ "${3:-}" = confirmed-manual ] || {
    echo 'Manual creation requires an explicit choice, never a fallback after errors.' >&2
    return 1
  }
  body=$(jq -cen --arg name "$1" --arg org "$2" '
    select(($name | length) > 0 and
      ($org | test("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"))) |
    {name:$name, organization_id:$org}') || return 1
  roster_post_artist "$body"
}

reconcile_spotify_artist() {
  local spotify="$1" org="$2" saved_id="${3:-}" response status payload matches artist_id
  local token="${RECOUP_API_KEY:-${RECOUP_ACCESS_TOKEN:-}}"
  [ -n "$token" ] || return 1
  jq -en --arg spotify "$spotify" --arg org "$org" '
    ($spotify | test("^[A-Za-z0-9]{22}$")) and
    ($org | test("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"))' >/dev/null || return 1
  response=$(curl -sS --max-time 90 -X GET -H "Authorization: Bearer $token" \
    -w '\n%{http_code}' "https://api.recoupable.dev/api/artists?org_id=$org") || return 1
  status="${response##*$'\n'}"; payload="${response%$'\n'*}"
  [ "$status" = 200 ] || { printf 'Roster HTTP %s; stop.\n' "$status" >&2; return 1; }
  matches=$(printf '%s' "$payload" | jq -ec --arg spotify "$spotify" '
    .artists | arrays | map(select(any(.account_socials[]?;
      (.profile_url // .link // "") | test("^https://open\\.spotify\\.com/artist/" + $spotify + "([?].*)?$"))))') || return 1
  case "$(printf '%s' "$matches" | jq 'length')" in
    0)
      jq -cn --arg spotify "$spotify" --arg org "$org" \
        '{spotify_artist_id:$spotify, organization_id:$org, roster_http_status:200, reconciliation:"not_found"}'
      return 2 ;;
    1) ;;
    *) echo 'Multiple profiles have that identity. Resolve the conflict; do not merge or create.' >&2; return 1 ;;
  esac
  artist_id=$(printf '%s' "$matches" | jq -er '.[0] |
    select(.id == null or .account_id == null or .id == .account_id) |
    (.account_id // .id) | select(type == "string" and length > 0)') || return 1
  [ -z "$saved_id" ] || [ "$saved_id" = "$artist_id" ] || {
    echo 'The saved artist ID conflicts with the current roster. Stop for review.' >&2; return 1;
  }
  jq -cn --arg spotify "$spotify" --arg org "$org" --arg id "$artist_id" \
    '{spotify_artist_id:$spotify, organization_id:$org, artist_account_id:$id,
      roster_http_status:200, reconciliation:"matched"}'
}
