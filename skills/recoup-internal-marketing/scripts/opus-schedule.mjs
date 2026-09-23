// Schedules video/opus/teasers.manifest.json via the OpusClip CLI. Idempotent ledger. Usage: node schedule.mjs [--only yt] [--limit N]
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
const CLI = process.env.OPUSCLIP_CLI || `${process.env.HOME}/.agents/skills/opusclip/scripts/opusclip`;
const MANIFEST = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : "schedule.manifest.json";
const m = JSON.parse(readFileSync(MANIFEST, "utf8"));
const projects = JSON.parse(readFileSync("projects.json", "utf8"));
const args = process.argv.slice(2).filter(a => a !== MANIFEST);
const only = args.includes("--only") ? args[args.indexOf("--only") + 1] : null;
const limit = args.includes("--limit") ? +args[args.indexOf("--limit") + 1] : Infinity;
const ledgerPath = MANIFEST.replace(/\.json$/, ".ledger.jsonl");
const done = new Set(existsSync(ledgerPath) ? readFileSync(ledgerPath, "utf8").trim().split("\n").filter(Boolean).map(l => JSON.parse(l).key) : []);
const link = p => `${m.site}?utm_source=${p}&utm_medium=social&utm_campaign=${m.campaign}`;
const bodies = (c, p) => {
  const yt = { title: c.yt_title, description: `${c.caption}

${m.cta_yt} ${link("yt")}`, privacy: "public" };
  const tt = { title: `${c.caption} ${m.cta_bio} ${m.hashtags}` };
  const ig = { title: c.yt_title, description: `${c.caption}

${m.cta_bio}

${m.hashtags}` };
  const x = { title: c.x };                                            // no URL: Opus X rejects any URL in the text
  const li = { title: `${c.caption}

${m.cta_yt} ${link("li")}` };   // link in the body
  return { yt, tt, ig, x, li }[p];
};
let n = 0;
for (const c of m.items) {
  for (const p of Object.keys(m.accounts)) {
    if (only && p !== only) continue;
    const key = `${c.key}:${p}`; if (done.has(key)) continue; if (n >= limit) process.exit(0);
    const acct = m.accounts[p]; const b = bodies(c, p); const pr = projects[c.key];
    const argv = ["post", "schedule", "--project", pr.project_id, "--clip", pr.clip_id, "--account", acct.id, "--title", b.title, "--at", c.at];
    if (acct.sub) argv.push("--sub-account", acct.sub);
    if (b.description) argv.push("--description", b.description);
    if (b.privacy) argv.push("--privacy", b.privacy);
    let out, ok = true;
    try { out = execFileSync("node", [CLI, ...argv], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }); }
    catch (e) { ok = false; out = (e.stdout || "") + (e.stderr || ""); }
    const row = { key, item: c.key, platform: p, at: c.at, project: pr.project_id, clip: pr.clip_id, ok, result: out.trim().slice(0, 400) };
    console.log(JSON.stringify(row));
    if (ok) appendFileSync(ledgerPath, JSON.stringify(row) + "\n"); else process.exit(1);
    n++; await new Promise(r => setTimeout(r, 1200));
  }
}
