// Still frames of built HyperFrames comps on Vercel Sandbox: `hyperframes snapshot` is a full headless render, so it never
// runs on the laptop when ~/.config/recoup/podcast-sandbox.json says "default": "sandbox". Used to compare looks before a
// render (podcast-shorts.md, "A new look gets three directions first").
//   node --env-file=<env> scripts/podcast/sandbox/stills.mjs <out-dir> <comp-dir>@<t1,t2,...> [<comp-dir>@<times> ...]
// Each comp (already built, e.g. pulled back by `studio.mjs build`) gets its own sandbox; PNGs land in
// <out-dir>/<comp-name>/ as frame-NN-at-<t>s.png with the CLI's contact-sheet.jpg.
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SDK_DIR = process.env.RECOUP_SANDBOX_SDK || path.join(os.homedir(), ".cache/recoup/podcast-sandbox");
const { Sandbox } = await import(pathToFileURL(createRequire(path.join(SDK_DIR, "package.json")).resolve("@vercel/sandbox")));
const CFG = JSON.parse(fs.readFileSync(path.join(os.homedir(), ".config/recoup/podcast-sandbox.json"), "utf8"));
const HF = CFG.hyperframes || "hyperframes@0.8.181";
const auth = { token: process.env.VERCEL_TOKEN, teamId: process.env.VERCEL_TEAM_ID, projectId: process.env.VERCEL_PROJECT_ID };
if (!auth.token || !auth.teamId || !auth.projectId) { console.error("set VERCEL_TOKEN, VERCEL_TEAM_ID, VERCEL_PROJECT_ID (--env-file)"); process.exit(1); }
const [outDir, ...specs] = process.argv.slice(2);
if (!outDir || !specs.length) { console.error("usage: stills.mjs <out-dir> <comp-dir>@<t1,t2,...> ..."); process.exit(1); }
const JOBS = specs.map((spec) => {
  const at = spec.lastIndexOf("@"), dir = spec.slice(0, at), ts = spec.slice(at + 1).split(",").map(Number);
  if (at < 1 || !ts.length || ts.some((t) => !Number.isFinite(t) || t < 0)) { console.error(`bad spec ${spec}: want <comp-dir>@<t1,t2,...>`); process.exit(1); }
  return { dir, times: ts.join(","), name: path.basename(dir) };
});
const dup = JOBS.map((j) => j.name).find((n, i, a) => a.indexOf(n) !== i);
if (dup) { console.error(`two comps named ${dup}: their stills would overwrite each other`); process.exit(1); }
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "recoup-stills-"));
const t0 = Date.now(), log = (tag, m) => console.log(`[${((Date.now() - t0) / 1000).toFixed(0).padStart(4)}s ${tag}] ${m}`);

async function sh(sbx, tag, script) {
  const r = await sbx.runCommand({ cmd: "bash", args: ["-lc", script] });
  const out = (await r.stdout()) + (await r.stderr());
  if (r.exitCode !== 0) { out.trim().split("\n").slice(-12).forEach((l) => log(tag, l)); throw new Error(`${tag}: exit ${r.exitCode}`); }
  return out;
}

async function stills({ dir, times, name }) {
  const local = path.join(outDir, name);
  let sbx;
  try {
    sbx = await Sandbox.create({ ...auth, source: { type: "snapshot", snapshotId: CFG.snapshotId }, resources: { vcpus: 8 },
      timeout: 30 * 60e3, persistent: false });
    log(name, `sandbox ${sbx.name}`);
    const tar = path.join(TMP, `${name}.tgz`);
    execFileSync("tar", ["--no-xattrs", "-czf", tar, "--exclude", ".hyperframes", "--exclude", "snapshots", "-C", dir, "."]);
    await sbx.writeFiles([{ path: `/work/${name}.tgz`, content: fs.readFileSync(tar) }]);
    await sh(sbx, name, `mkdir -p /work/c && tar -xzf /work/${name}.tgz -C /work/c`);
    // snapshot writes frame-NN-at-<t>s.png + contact-sheet.jpg into .hyperframes/artifacts/snapshots/<run-id>/ (plus an end frame)
    await sh(sbx, name, `cd /work/c && npx --yes ${HF} snapshot --at ${times} . > /work/snap.log 2>&1; ` +
      `R=$(ls -d .hyperframes/artifacts/snapshots/*/ 2>/dev/null | head -1); test -n "$R" || { tail -15 /work/snap.log; exit 1; }; ` +
      `tar -czf /work/snaps.tgz -C "$R" .`);
    const st = path.join(TMP, `${name}-snaps.tgz`);
    await sbx.downloadFile({ path: "/work/snaps.tgz" }, { path: st });
    fs.mkdirSync(local, { recursive: true });
    execFileSync("tar", ["-xzf", st, "-C", local]);
    log(name, `done -> ${local} (${fs.readdirSync(local).filter((f) => f.endsWith(".png")).length} png)`);
    return true;
  } catch (e) { log(name, `FAILED: ${e.message}`); return false; } finally { if (sbx) await sbx.stop().catch(() => log(name, `stop ${sbx.name} in the dashboard`)); }
}

let ok;
try { ok = await Promise.all(JOBS.map(stills)); } finally { fs.rmSync(TMP, { recursive: true, force: true }); }
log("summary", `wall ${((Date.now() - t0) / 60e3).toFixed(1)} min`);
if (ok.some((r) => !r)) process.exitCode = 1;
