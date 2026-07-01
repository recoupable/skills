#!/usr/bin/env node
// recoup-internal-task-email-audit — enumerate customer-prompt-task runs from Trigger.dev.
//
// Needs a PROD Trigger key: `process.env.TRIGGER_SECRET_KEY` must be `tr_prod_*`
// (a `tr_dev_*` key returns 0 prod runs — the #1 gotcha). Pull it WITHOUT
// clobbering your local .env, from the recoupable/api repo (linked to recoup/api):
//   vercel env pull /tmp/prod.env --environment=production --yes
//   export TRIGGER_SECRET_KEY=$(grep '^TRIGGER_SECRET_KEY=' /tmp/prod.env | cut -d= -f2-)
//   rm /tmp/prod.env          # scrub the secrets when done
//
// Usage:
//   node fetch_task_runs.mjs [--hours 24] [--account <uuid>]
//
// Writes to stdout: JSON array of { run_id, account, status, createdAt, finishedAt }.
// Writes to stderr: a summary + a ready-to-paste Postgres `array[...]::uuid[]` of the
// run accounts for the correlation SQL in SKILL.md. So:
//   node fetch_task_runs.mjs --hours 24 > runs.json     # runs.json = clean JSON; array printed to terminal

const args = process.argv.slice(2);
const arg = (name, def) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : def;
};
const hours = Number(arg("hours", "24"));
const account = arg("account", null);

const key = process.env.TRIGGER_SECRET_KEY;
if (!key) {
  console.error("Missing TRIGGER_SECRET_KEY — pull the PROD key (see header).");
  process.exit(2);
}
if (!key.startsWith("tr_prod_")) {
  console.error(`WARN: key looks non-prod (${key.slice(0, 8)}…) — a tr_dev_* key returns 0 prod runs.`);
}

const cutoff = Date.now() - hours * 3600 * 1000;

async function page(after) {
  const u = new URL("https://api.trigger.dev/api/v1/runs");
  u.searchParams.set("page[size]", "100");
  if (account) u.searchParams.set("filter[tag]", `account:${account}`);
  if (after) u.searchParams.set("page[after]", after);
  const r = await fetch(u, { headers: { Authorization: `Bearer ${key}` } });
  if (!r.ok) {
    console.error(`Trigger.dev API ${r.status}: ${(await r.text()).slice(0, 300)}`);
    process.exit(1);
  }
  return r.json();
}

const out = [];
let after = null;
let pages = 0;
while (pages++ < 30) {
  const d = await page(after);
  const data = d.data || [];
  if (!data.length) break;
  for (const run of data) {
    if (run.taskIdentifier !== "customer-prompt-task") continue;
    if (new Date(run.createdAt).getTime() < cutoff) continue;
    const tag = (run.tags || []).map(String).find(t => t.startsWith("account:"));
    out.push({
      run_id: run.id,
      account: tag ? tag.slice("account:".length) : null,
      status: run.status,
      createdAt: run.createdAt,
      finishedAt: run.finishedAt,
    });
  }
  const oldest = data.map(r => new Date(r.createdAt).getTime()).sort((a, b) => a - b)[0];
  after = d.pagination && d.pagination.next;
  if (!after || oldest < cutoff) break;
}

const accts = [...new Set(out.map(r => r.account).filter(Boolean))];
console.error(`# ${out.length} customer-prompt-task runs in the last ${hours}h across ${accts.length} tagged accounts`);
console.error(`# paste this into the correlation SQL (§ 2):`);
console.error(`array[${accts.map(a => `'${a}'`).join(",")}]::uuid[]`);
console.log(JSON.stringify(out, null, 2));
