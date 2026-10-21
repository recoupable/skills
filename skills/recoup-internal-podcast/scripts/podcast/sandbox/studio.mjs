// Podcast post-production on Vercel Sandbox: raw media lives on a Drive, every re-cut, build and render runs in its
// own sandbox, and only text files and finished MP4s move between the laptop and Vercel. See references/podcast-sandbox.md.
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs setup                      base snapshot (ffmpeg, Chrome libs, zsh, HyperFrames)
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs media <project>            upload the raw media cut.py reads (skips files already there)
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs build <project> ch05 ...    re-cut + build only, pull the comp back for snapshots
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs run <project> ch05 s3 ...  re-cut + build + render each job in parallel
// <env> holds VERCEL_TOKEN, VERCEL_TEAM_ID and VERCEL_PROJECT_ID. Chapters land in <project>/exports/<ch>.mp4 (the previous file
// moves to exports/.prev/), shorts in exports/shorts/<slug>.mp4, and each built comp is pulled back into <project>/comp/.
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const SDK_DIR = process.env.RECOUP_SANDBOX_SDK || path.join(os.homedir(), ".cache/recoup/podcast-sandbox");
let Sandbox, Drive;
try {
  ({ Sandbox, Drive } = await import(pathToFileURL(createRequire(path.join(SDK_DIR, "package.json")).resolve("@vercel/sandbox"))));
} catch {
  console.error(`needs @vercel/sandbox: npm i --prefix ${SDK_DIR} @vercel/sandbox@3.8.0`);
  process.exit(1);
}

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const HF = "hyperframes@0.8.181";                    // same version as local renders, so frames match
const CFG = path.join(os.homedir(), ".config/recoup/podcast-sandbox.json");
const TMP = path.join(os.tmpdir(), "recoup-podcast-sandbox");
const DRIVE = "podcast-media";
const CHUNK = 48 * 1024 * 1024;                      // writeFiles takes a buffer; big files go up in pieces
const auth = { token: process.env.VERCEL_TOKEN, teamId: process.env.VERCEL_TEAM_ID, projectId: process.env.VERCEL_PROJECT_ID };
if (!auth.token || !auth.teamId || !auth.projectId) { console.error("set VERCEL_TOKEN, VERCEL_TEAM_ID, VERCEL_PROJECT_ID (--env-file)"); process.exit(1); }
const cfg = () => (fs.existsSync(CFG) ? JSON.parse(fs.readFileSync(CFG, "utf8")) : {});
const t0 = Date.now();
const log = (tag, m) => console.log(`[${((Date.now() - t0) / 1000).toFixed(0).padStart(4)}s ${tag}] ${m}`);
fs.mkdirSync(TMP, { recursive: true });

// Commands run in the image's home dir, not /vercel/sandbox: always use absolute paths.
async function sh(sbx, tag, script, { sudo = false, quiet = false } = {}) {
  const r = await sbx.runCommand({ cmd: "bash", args: ["-lc", script], sudo });
  const out = (await r.stdout()) + (await r.stderr());
  if (!quiet || r.exitCode !== 0) out.trim().split("\n").slice(-12).forEach((l) => log(tag, l));
  if (r.exitCode !== 0) throw new Error(`${tag}: exit ${r.exitCode}`);
  return out;
}

async function upload(sbx, local, remote) {
  const fd = fs.openSync(local, "r"), size = fs.statSync(local).size, parts = [];
  for (let off = 0, i = 0; off < size; off += CHUNK, i++) {
    const buf = Buffer.alloc(Math.min(CHUNK, size - off));
    fs.readSync(fd, buf, 0, buf.length, off);
    const p = `${remote}.part${String(i).padStart(4, "0")}`;
    await sbx.writeFiles([{ path: p, content: buf }]);
    parts.push(p);
  }
  fs.closeSync(fd);
  await sh(sbx, "upload", `cat ${parts.join(" ")} > '${remote}' && rm ${parts.join(" ")}`, { quiet: true });
}

// --no-xattrs: macOS provenance attributes make GNU tar print a warning per file.
const tarOf = (name, dir, items, excludes = []) => {
  const out = path.join(TMP, name);
  execFileSync("tar", ["--no-xattrs", "-czf", out, ...excludes.flatMap((e) => ["--exclude", e]), "-C", dir, ...items]);
  return out;
};

async function setup() {
  const sbx = await Sandbox.create({ ...auth, resources: { vcpus: 8 }, timeout: 30 * 60e3, persistent: false });
  log("setup", `sandbox ${sbx.name}`);
  await sh(sbx, "apt", "export DEBIAN_FRONTEND=noninteractive; apt-get update -qq && apt-get install -y -qq ffmpeg zsh " +
    "libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 " +
    "libgbm1 libpango-1.0-0 libcairo2 libasound2t64 libxfixes3 libdrm2 fonts-liberation >/dev/null && ffmpeg -version | head -1", { sudo: true });
  await sh(sbx, "hf", `npx --yes ${HF} browser ensure 2>&1 || npx --yes ${HF} browser install 2>&1; npx --yes ${HF} doctor 2>&1 | grep -E "Chrome|FFmpeg"`);
  const snap = await sbx.snapshot({ expiration: 0 });
  fs.mkdirSync(path.dirname(CFG), { recursive: true });
  fs.writeFileSync(CFG, JSON.stringify({ default: "sandbox", ...cfg(), snapshotId: snap.snapshotId, hyperframes: HF,
    created: new Date().toISOString() }, null, 2));
  log("setup", `base snapshot ${snap.snapshotId} saved to ${CFG}`);
}

// The files cut.py and build_hy.py read: the role names (symlinks or files), the fixed host video, the screen share,
// and any enhanced audio. Everything else in raw/ stays local.
function rawSet(proj) {
  const raw = path.join(proj, "raw"), files = new Set(), links = [];
  const add = (n) => {
    const p = path.join(raw, n);
    if (!fs.existsSync(p)) return;
    if (fs.lstatSync(p).isSymbolicLink()) { links.push([n, fs.readlinkSync(p)]); files.add(fs.readlinkSync(p)); } else files.add(n);
  };
  ["guest-video.mkv", "guest-audio.m4a", "host-audio.m4a", "host-video-fixed.mp4"].forEach(add);
  if (!fs.existsSync(path.join(raw, "host-video-fixed.mp4"))) add("host-video.mkv");
  const scr = JSON.parse(fs.readFileSync(path.join(proj, "edit/chapters.json"), "utf8")).screen;
  if (scr) add(path.relative(raw, path.join(proj, scr.src)));
  fs.readdirSync(raw).filter((f) => /-enhanced\.(wav|m4a)$/.test(f)).forEach(add);
  return { files, links };
}

async function media(proj) {
  const slug = path.basename(proj), raw = path.join(proj, "raw"), { files, links } = rawSet(proj);
  const drive = await Drive.getOrCreate({ ...auth, name: DRIVE });
  const sbx = await Sandbox.create({ ...auth, timeout: 2 * 60 * 60e3, persistent: false, mounts: { "/media": drive } });
  try {
    await sh(sbx, "media", `mkdir -p /media/${slug}/raw`, { quiet: true });
    const have = Object.fromEntries((await sh(sbx, "media", `cd /media/${slug}/raw && find . -maxdepth 1 -type f -printf '%f %s\\n'`, { quiet: true }))
      .trim().split("\n").filter(Boolean).map((l) => l.split(" ")).map(([f, s]) => [f, +s]));
    for (const f of files) {
      const size = fs.statSync(path.join(raw, f)).size;
      if (have[f] === size) { log("media", `${f} already on the drive`); continue; }
      const s = Date.now();
      await upload(sbx, path.join(raw, f), `/media/${slug}/raw/${f}`);
      log("media", `${f} ${(size / 1e6).toFixed(0)} MB in ${((Date.now() - s) / 1000).toFixed(0)}s`);
    }
    if (links.length) await sh(sbx, "media", `cd /media/${slug}/raw && ${links.map(([n, t]) => `ln -sfn '${t}' '${n}'`).join(" && ")}`, { quiet: true });
    await sh(sbx, "media", `ls -la /media/${slug}/raw`);
  } finally { await sbx.stop(); }
}

async function job(proj, id, snapshotId, drive, skillTar, projTar, render) {
  const slug = path.basename(proj), P = "/work/proj", S = "/work/skill", isShort = /^s\d+$/.test(id);
  // Read-only drive snapshot: only one sandbox can mount a drive read-write, and parallel jobs only read raw media.
  const sbx = await Sandbox.create({ ...auth, source: { type: "snapshot", snapshotId }, resources: { vcpus: 8 },
    timeout: 90 * 60e3, persistent: false, mounts: { "/media": drive.snapshot() } });
  log(id, `sandbox ${sbx.name}`);
  try {
    for (const [tar, dir] of [[skillTar, S], [projTar, P]]) {
      await sbx.writeFiles([{ path: `/work/${path.basename(tar)}`, content: fs.readFileSync(tar) }]);
      await sh(sbx, id, `mkdir -p ${dir} && tar -xzf /work/${path.basename(tar)} -C ${dir}`, { quiet: true });
    }
    await sh(sbx, id, `ln -sfn /media/${slug}/raw ${P}/raw && mkdir -p ${P}/exports/shorts`, { quiet: true });
    let outRel, compRel;
    if (isShort) {
      const sj = JSON.parse(fs.readFileSync(path.join(proj, "edit/shorts.json"), "utf8"));
      const s = (sj.shorts || sj).find((x) => x.id === id);
      outRel = `exports/shorts/${s.slug}.mp4`; compRel = `comp/shorts/${id}`;
      await sh(sbx, id, render ? `cd ${S} && RECUT=1 zsh scripts/podcast/shorts/render.sh ${P} ${id}:${s.slug}`
        : `cd ${S} && python3 scripts/podcast/shorts/build_hy.py ${P} ${id} --recut 2>&1 | tail -4`);
    } else {
      // Chapters build and render here rather than through render.sh, which rebuilds the comp and would drop an
      // episode-only overlay such as edit/screen_share.py.
      const cj = JSON.parse(fs.readFileSync(path.join(proj, "edit/chapters.json"), "utf8"));
      const ch = cj.chapters.find((c) => c.id === id), scr = cj.screen;
      const share = scr && fs.existsSync(path.join(proj, "edit/screen_share.py")) && ch.pieces.some((p) => p.out > scr.from && p.in < scr.to);
      outRel = `exports/${id}.mp4`; compRel = `comp/chapters/${id}`;
      await sh(sbx, id, `cd ${S} && python3 scripts/podcast/build.py ${P} ${id} --recut 2>&1 | tail -4` +
        (share ? ` && python3 ${P}/edit/screen_share.py ${P} ${id} 2>&1 | tail -3` : ""));
      if (render) await sh(sbx, id, `cd ${P}/${compRel} && npx --yes ${HF} render -o ${P}/${outRel} > ${P}/exports/render-${id}.log 2>&1; ` +
        `grep -q "Render complete" ${P}/exports/render-${id}.log && grep -E "MB ·" ${P}/exports/render-${id}.log | tr -s ' '`);
    }
    const local = path.join(proj, outRel);
    if (render && fs.existsSync(local)) {
      fs.mkdirSync(path.join(path.dirname(local), ".prev"), { recursive: true });
      fs.renameSync(local, path.join(path.dirname(local), ".prev", path.basename(local)));
    }
    if (render) await sbx.downloadFile({ path: `${P}/${outRel}` }, { path: local }, { mkdirRecursive: true });
    await sh(sbx, id, `tar -czf /work/comp.tgz --exclude .hyperframes -C ${P}/${compRel} .`, { quiet: true });
    const ct = path.join(TMP, `${id}-comp.tgz`);
    await sbx.downloadFile({ path: "/work/comp.tgz" }, { path: ct });
    fs.rmSync(path.join(proj, compRel, "assets"), { recursive: true, force: true });
    fs.mkdirSync(path.join(proj, compRel), { recursive: true });
    execFileSync("tar", ["-xzf", ct, "-C", path.join(proj, compRel)]);
    const done = render ? outRel : compRel;
    log(id, `done -> ${done}`);
    return { id, ok: true, out: done };
  } catch (e) {
    log(id, `FAILED: ${e.message}`);
    return { id, ok: false };
  } finally { await sbx.stop(); }
}

async function run(proj, ids, render) {
  const { snapshotId } = cfg();
  if (!snapshotId) throw new Error(`no base snapshot in ${CFG}; run setup first`);
  const drive = await Drive.get({ ...auth, name: DRIVE });
  const skillTar = tarOf("skill.tgz", SKILL, ["scripts", "templates", "brand"], ["__pycache__"]);
  const projTar = tarOf("proj.tgz", proj, ["episode.json", "edit"], ["fixseg", "intake", "sharecheck", "__pycache__"]);
  const res = await Promise.all(ids.map((id) => job(proj, id, snapshotId, drive, skillTar, projTar, render)));
  res.forEach((r) => log("summary", `${r.id} ${r.ok ? "ok " + r.out : "FAILED"}`));
  log("summary", `wall ${((Date.now() - t0) / 60e3).toFixed(1)} min`);
  if (res.some((r) => !r.ok)) process.exitCode = 1;
}

const [cmd, proj, ...ids] = process.argv.slice(2);
if (cmd === "setup") await setup();
else if (cmd === "media") await media(path.resolve(proj));
else if ((cmd === "run" || cmd === "build") && ids.length) await run(path.resolve(proj), ids, cmd === "run");
else console.log("usage: studio.mjs setup | media <project> | build|run <project> <chNN|sN> ...");
