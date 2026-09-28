// Import finished clips into OpusClip as full-length projects with captions/emojis OFF (the bundled CLI cannot send those flags).
// Run from <project>/opus/: node opus-import.mjs   Reads ./import.json {"title": "...", "items": [{"key": "A", "file": "../teasers/out/a.mp4"}]}
// Needs OPUSCLIP_API_KEY in the environment and FAL_ENV pointing at a file with FAL_KEY=... (clips are hosted on fal storage). Ledger: ./projects.json
import { fal } from "/Users/voicefirstai/Projects/RECOUP/mono/api/node_modules/@fal-ai/client/src/index.js";
import fs from "node:fs"; import path from "node:path"; import { execFileSync } from "node:child_process";
const PROJ = process.cwd();
const CLI = process.env.OPUSCLIP_CLI || `${process.env.HOME}/.agents/skills/opusclip/scripts/opusclip`;
const env = fs.readFileSync(process.env.FAL_ENV, "utf8");
fal.config({ credentials: env.match(/^FAL_KEY=(.*)$/m)[1].trim().replace(/^["']|["']$/g, "") });
const KEY = process.env.OPUSCLIP_API_KEY; if (!KEY) throw new Error("OPUSCLIP_API_KEY not set");
const ledger = path.join(PROJ, "projects.json"); const led = fs.existsSync(ledger) ? JSON.parse(fs.readFileSync(ledger, "utf8")) : {};
const MAN = JSON.parse(fs.readFileSync(path.join(PROJ, "import.json"), "utf8"));
const ITEMS = Object.fromEntries(MAN.items.map(i => [i.key, i.file]));
for (const [k, f] of Object.entries(ITEMS)) {
  if (led[k]?.project_id) { console.log(`   ${k} already ${led[k].project_id}`); continue; }
  const url = await fal.storage.upload(new File([fs.readFileSync(path.join(PROJ, f))], `${k}.mp4`, { type: "video/mp4" }));
  const body = { videoUrl: url, uploadedVideoAttr: { title: `${MAN.title} ${k}` }, curationPref: { skipCurate: true },
    renderPref: { layoutAspectRatio: "portrait", enableCaption: false, enableEmoji: false, enableAutoEmoji: false, enableBRoll: false, enableKeywordHighlight: false } };
  const r = await fetch("https://api.opus.pro/api/clip-projects", { method: "POST", headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json(); if (!r.ok) { console.log(`   ${k} FAILED ${r.status}`, JSON.stringify(j).slice(0, 300)); continue; }
  led[k] = { project_id: j.projectId || j.data?.projectId || j.project_id, src: f, fal_url: url, created: new Date().toISOString() };
  fs.writeFileSync(ledger, JSON.stringify(led, null, 1)); console.log(`   ${k} -> ${led[k].project_id}`); await new Promise(r => setTimeout(r, 1200));
}
for (let i = 0; i < 40; i++) {
  let pending = 0;
  for (const k of Object.keys(ITEMS)) {
    if (led[k].clip_id) continue; pending++;
    let out = ""; try { out = execFileSync("node", [CLI, "clip", "list", "--project", led[k].project_id], { encoding: "utf8" }); } catch (e) { out = (e.stdout || "") + (e.stderr || ""); }
    let clips = []; try { const j = JSON.parse(out); clips = Array.isArray(j) ? j : (j.clips || j.data || []); } catch {}
    if (clips.length) { const c = clips[0]; led[k].clip_id = c.clip_id || c.clipId || c.id; led[k].duration_sec = c.duration_sec || c.duration || null; fs.writeFileSync(ledger, JSON.stringify(led, null, 1)); console.log(`   ${k} clip ${led[k].clip_id} ${led[k].duration_sec}s`); pending--; }
  }
  if (!pending) break; console.log(`   waiting (${i + 1}), ${pending} pending`); await new Promise(r => setTimeout(r, 15000));
}
