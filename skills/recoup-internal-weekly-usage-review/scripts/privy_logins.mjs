// Read-only: paginate Privy users, report logins in a UTC window.
// Usage: PRIVY_APP_ID=... PRIVY_PROJECT_SECRET=... \
//   node scripts/privy_logins.mjs --from 2026-07-13 --to 2026-07-20
const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 ? process.argv[i + 1] : fallback;
};
const appId = process.env.PRIVY_APP_ID;
const secret = process.env.PRIVY_PROJECT_SECRET;
if (!appId || !secret) {
  console.error("needs PRIVY_APP_ID and PRIVY_PROJECT_SECRET in the environment");
  process.exit(1);
}
const WINDOW_START = Date.parse(`${arg("from")}T00:00:00Z`);
const WINDOW_END = arg("to") ? Date.parse(`${arg("to")}T00:00:00Z`) : Date.now();
if (Number.isNaN(WINDOW_START) || Number.isNaN(WINDOW_END)) {
  console.error("usage: node scripts/privy_logins.mjs --from YYYY-MM-DD [--to YYYY-MM-DD]");
  process.exit(1);
}

const auth = "Basic " + Buffer.from(`${appId}:${secret}`).toString("base64");
const toMs = (t) => (t < 1e12 ? t * 1000 : t); // Privy mixes s / ms epochs

let cursor;
let total = 0;
const hits = [];
while (true) {
  const url = new URL("https://api.privy.io/v1/users");
  url.searchParams.set("limit", "100");
  if (cursor) url.searchParams.set("cursor", cursor);
  const res = await fetch(url, {
    headers: { "privy-app-id": appId, Authorization: auth },
  });
  if (!res.ok) throw new Error(`Privy API ${res.status}: ${await res.text()}`);
  const page = await res.json();
  if (!page.data?.length) break;
  total += page.data.length;

  for (const u of page.data) {
    let latest = null;
    const idents = [];
    for (const a of u.linked_accounts ?? []) {
      if (typeof a.latest_verified_at === "number") {
        const ms = toMs(a.latest_verified_at);
        if (latest === null || ms > latest) latest = ms;
      }
      if (a.type === "email") idents.push(a.address);
      else if (a.type === "google_oauth") idents.push(`google:${a.email}`);
      else if (a.type === "apple_oauth") idents.push(`apple:${a.email}`);
      else if (a.type === "wallet") idents.push(`wallet:${a.address}`);
      else if (a.type) idents.push(a.type);
    }
    const createdMs = typeof u.created_at === "number" ? toMs(u.created_at) : null;
    if (latest !== null && latest >= WINDOW_START && latest < WINDOW_END) {
      hits.push({
        id: u.id,
        idents: [...new Set(idents)],
        latestLogin: new Date(latest).toISOString(),
        created: createdMs ? new Date(createdMs).toISOString() : null,
        isNew: createdMs !== null && createdMs >= WINDOW_START,
      });
    }
  }
  if (!page.next_cursor) break;
  cursor = page.next_cursor;
}

hits.sort((a, b) => (a.latestLogin < b.latestLogin ? 1 : -1));
console.log(
  JSON.stringify(
    {
      window: { from: new Date(WINDOW_START).toISOString(), to: new Date(WINDOW_END).toISOString() },
      totalPrivyUsers: total,
      activeCount: hits.length,
      newSignups: hits.filter((h) => h.isNew).length,
      returning: hits.filter((h) => !h.isNew).length,
      users: hits,
    },
    null,
    2,
  ),
);
