// Podcast post-production on Vercel Sandbox: raw media lives on a Drive, every re-cut, build and render runs in its
// own sandbox, and only text files and finished MP4s move between the laptop and Vercel. See references/podcast-sandbox.md.
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs setup                      base snapshot (ffmpeg, Chrome libs, zsh, HyperFrames)
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs media <project>            upload the raw media cut.py reads (skips files already there)
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs build <project> ch05 ...    re-cut + build only, pull the comp back for snapshots
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs run <project> ch05 s3 ...  re-cut + build + render each job in parallel
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs enhanced <project> <host.wav> <guest.wav> [<guest-part2.wav>]
//        Adobe output -> enhance_pack.py unpack + gate_host_audio.py, results written to the drive (guest halves rejoined)
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs assemble <project>       opening join + assemble.py -> exports/final/
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs tracks <project>         episode's edit/enhance_assemble.py build (Adobe files in
//        raw/enhance/*-enhanced.wav + any *.map.json) + gate_host_audio.py per enhanced track, results written to the drive
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs comp <project> intro outro  render comp/<name> -> exports/<name>.mp4 (make_intro.py output)
//   node --env-file=<env> scripts/podcast/sandbox/studio.mjs cutout <photo.jpg> <cutout.png>   rembg (bria-rmbg) background removal
//        for the cover headshot, plus <cutout>-check.png (mask on flat lime) to look at before make_cover.py
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
// One temp dir per run: parallel runs for two episodes would otherwise overwrite each other's proj.tgz mid-upload.
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "recoup-podcast-sandbox-"));
const DRIVE = "podcast-media";
const CHUNK = 48 * 1024 * 1024;                      // writeFiles takes a buffer; big files go up in pieces
const auth = { token: process.env.VERCEL_TOKEN, teamId: process.env.VERCEL_TEAM_ID, projectId: process.env.VERCEL_PROJECT_ID };
if (!auth.token || !auth.teamId || !auth.projectId) { console.error("set VERCEL_TOKEN, VERCEL_TEAM_ID, VERCEL_PROJECT_ID (--env-file)"); process.exit(1); }
const cfg = () => (fs.existsSync(CFG) ? JSON.parse(fs.readFileSync(CFG, "utf8")) : {});
const t0 = Date.now();
const log = (tag, m) => console.log(`[${((Date.now() - t0) / 1000).toFixed(0).padStart(4)}s ${tag}] ${m}`);

// A home connection drops mid-upload ("fetch failed", connect timeouts): retry the API call, not the job.
async function retry(fn, tag = "net") {
  for (let i = 1; ; i++) {
    try { return await fn(); } catch (e) {
      const transient = /fetch failed|ECONNRESET|ETIMEDOUT|UND_ERR|socket hang up/i.test(`${e.message} ${e.cause?.code ?? ""}`);
      if (!transient || i === 5) throw e;
      log(tag, `connection dropped (${e.cause?.code ?? e.message}); retry ${i}/4`);
      await new Promise((r) => setTimeout(r, 5000 * i));
    }
  }
}
// Stopping must never throw: a failed stop would leave the sandbox billing until its timeout.
const stop = (sbx, tag) => retry(() => sbx.stop(), tag).catch((e) => log(tag, `could not stop ${sbx.name}: ${e.message}; stop it in the dashboard`));

// Commands run in the image's home dir, not /vercel/sandbox: always use absolute paths.
async function sh(sbx, tag, script, { sudo = false, quiet = false } = {}) {
  const r = await retry(() => sbx.runCommand({ cmd: "bash", args: ["-lc", script], sudo }), tag);
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
    await retry(() => sbx.writeFiles([{ path: p, content: buf }]), "upload");
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
  fs.readdirSync(raw).filter((f) => /-enhanced(-gated)?\.(wav|m4a)$/.test(f)).forEach(add);
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
  } finally { await stop(sbx, "media"); }
}

async function job(proj, id, snapshotId, drive, skillTar, projTar, render) {
  // a short is any id in edit/shorts.json (s1, t2, ...); everything else is a chapter
  const shortsFile = path.join(proj, "edit/shorts.json");
  const slug = path.basename(proj), P = "/work/proj", S = "/work/skill",
    isShort = fs.existsSync(shortsFile) && JSON.parse(fs.readFileSync(shortsFile, "utf8")).shorts.some((x) => x.id === id);
  // Read-only drive snapshot: only one sandbox can mount a drive read-write, and parallel jobs only read raw media.
  const sbx = await Sandbox.create({ ...auth, source: { type: "snapshot", snapshotId }, resources: { vcpus: 8 },
    timeout: 90 * 60e3, persistent: false, mounts: { "/media": drive.snapshot() } });
  log(id, `sandbox ${sbx.name}`);
  try {
    for (const [tar, dir] of [[skillTar, S], [projTar, P]]) {
      await retry(() => sbx.writeFiles([{ path: `/work/${path.basename(tar)}`, content: fs.readFileSync(tar) }]), id);
      await sh(sbx, id, `mkdir -p ${dir} && tar -xzf /work/${path.basename(tar)} -C ${dir}`, { quiet: true });
    }
    await sh(sbx, id, `ln -sfn /media/${slug}/raw ${P}/raw && mkdir -p ${P}/exports/shorts`, { quiet: true });
    let outRel, compRel;
    if (isShort) {
      const sj = JSON.parse(fs.readFileSync(path.join(proj, "edit/shorts.json"), "utf8"));
      const s = (sj.shorts || sj).find((x) => x.id === id);
      outRel = `exports/shorts/${s.slug}.mp4`; compRel = `comp/shorts/${id}`;
      // render.sh logs a failed build and still exits 0: the output file is the only proof the short rendered
      await sh(sbx, id, render ? `cd ${S} && RECUT=1 zsh scripts/podcast/shorts/render.sh ${P} ${id}:${s.slug}; ` +
        `test -s ${P}/${outRel} || { cat ${P}/exports/shorts/build-${id}.log 2>/dev/null | tail -5; exit 1; }`
        : `cd ${S} && python3 scripts/podcast/shorts/build_hy.py ${P} ${id} --recut > /work/build.log 2>&1; ` +
        // a pipe into tail hid build_hy's exit code: a rejected beat (e.g. a caption id) reported "ok" with no index.html
        `rc=$?; tail -4 /work/build.log; exit $rc`);
    } else {
      // Chapters build and render here rather than through render.sh, which rebuilds the comp and would drop an
      // episode-only overlay such as edit/screen_share.py.
      const cj = JSON.parse(fs.readFileSync(path.join(proj, "edit/chapters.json"), "utf8"));
      const ch = cj.chapters.find((c) => c.id === id), scr = cj.screen;
      const share = scr && fs.existsSync(path.join(proj, "edit/screen_share.py")) && ch.pieces.some((p) => p.out > scr.from && p.in < scr.to);
      outRel = `exports/${id}.mp4`; compRel = `comp/chapters/${id}`;
      await sh(sbx, id, `cd ${S} && python3 scripts/podcast/build.py ${P} ${id} --recut 2>&1 | tail -4` +
        (share ? ` && python3 ${P}/edit/screen_share.py ${P} ${id} 2>&1 | tail -3` : ""));
      // step 8 checks without a local browser: inspect + snapshot at every card midpoint, kept in the comp
      // (comp/<ch>/inspect.json, comp/<ch>/snapshots/). Overflow on the #ghost word or the ticker is by design.
      await sh(sbx, id, `cd ${P}/${compRel} && AT=$(python3 -c "import re;h=open('index.html').read();print(','.join('%.2f'%(float(s)+float(d)/2) for s,d in re.findall(r'class=\\"card [^\\"]*\\" data-start=\\"([\\d.]+)\\" data-duration=\\"([\\d.]+)\\"',h)))") && ` +
        `if [ -n "$AT" ]; then npx --yes ${HF} inspect --at "$AT" --json --max-issues 5000 > inspect.json 2>/dev/null; ` +
        `npx --yes ${HF} snapshot --at "$AT" --no-end -o snapshots > /dev/null 2>&1; ` +
        `python3 -c "import json;d=json.load(open('inspect.json'));i=[x for x in d.get('issues',[]) if x.get('severity')!='info' and not any(k in x.get('selector','')+x.get('containerSelector','') for k in ('#run','div.lab','#ghost'))];print('inspect: %d card issues' % len(i));[print(json.dumps(x)[:240]) for x in i[:6]]" || echo "inspect: unreadable"; fi`);
      if (render) await sh(sbx, id, `cd ${P}/${compRel} && npx --yes ${HF} render -o ${P}/${outRel} > ${P}/exports/render-${id}.log 2>&1; ` +
        `grep -q "Render complete" ${P}/exports/render-${id}.log && grep -E "MB ·" ${P}/exports/render-${id}.log | tr -s ' '`);
    }
    const local = path.join(proj, outRel);
    if (render && fs.existsSync(local)) {
      fs.mkdirSync(path.join(path.dirname(local), ".prev"), { recursive: true });
      fs.renameSync(local, path.join(path.dirname(local), ".prev", path.basename(local)));
    }
    if (render) await retry(() => sbx.downloadFile({ path: `${P}/${outRel}` }, { path: local }, { mkdirRecursive: true }), id);
    await sh(sbx, id, `tar -czf /work/comp.tgz --exclude .hyperframes -C ${P}/${compRel} .`, { quiet: true });
    const ct = path.join(TMP, `${id}-comp.tgz`);
    await retry(() => sbx.downloadFile({ path: "/work/comp.tgz" }, { path: ct }), id);
    fs.rmSync(path.join(proj, compRel, "assets"), { recursive: true, force: true });
    fs.mkdirSync(path.join(proj, compRel), { recursive: true });
    execFileSync("tar", ["-xzf", ct, "-C", path.join(proj, compRel)]);
    const done = render ? outRel : compRel;
    log(id, `done -> ${done}`);
    return { id, ok: true, out: done };
  } catch (e) {
    log(id, `FAILED: ${e.message}`);
    return { id, ok: false };
  } finally { await stop(sbx, id); }
}

// Opens a sandbox on the base snapshot with the skill and the project's text files unpacked, raw/ linked from the drive.
async function workspace(proj, tag, { vcpus = 8, writable = false } = {}) {
  const { snapshotId } = cfg();
  if (!snapshotId) throw new Error(`no base snapshot in ${CFG}; run setup first`);
  const slug = path.basename(proj), drive = await Drive.get({ ...auth, name: DRIVE });
  const sbx = await Sandbox.create({ ...auth, source: { type: "snapshot", snapshotId }, resources: { vcpus }, timeout: 3 * 60 * 60e3,
    persistent: false, mounts: { "/media": writable ? drive : drive.snapshot() } });
  log(tag, `sandbox ${sbx.name}`);
  // a failure while setting up must still stop the sandbox, or it bills until its 3 h timeout
  try {
  const skillTar = tarOf("skill.tgz", SKILL, ["scripts", "templates", "brand"], ["__pycache__"]);
  const extra = ["enhance/host-used-map.json", "enhance/guest-used-map.json", "enhance/guest-used-split.json"].filter((f) => fs.existsSync(path.join(proj, f)));
  const projTar = tarOf("proj.tgz", proj, ["episode.json", "edit", ...extra], ["fixseg", "intake", "sharecheck", "__pycache__"]);
  for (const [tar, dir] of [[skillTar, "/work/skill"], [projTar, "/work/proj"]]) {
    await retry(() => sbx.writeFiles([{ path: `/work/${path.basename(tar)}`, content: fs.readFileSync(tar) }]), tag);
    await sh(sbx, tag, `mkdir -p ${dir} && tar -xzf /work/${path.basename(tar)} -C ${dir}`, { quiet: true });
  }
  // a real raw/ dir of links, so scripts that write next to the raw media (unpack, gate) can
  await sh(sbx, tag, `mkdir -p /work/proj/raw /work/proj/exports && for f in /media/${slug}/raw/*; do ln -sfn "$(readlink -f "$f")" /work/proj/raw/$(basename "$f"); done`, { quiet: true });
  } catch (e) { await stop(sbx, tag); throw e; }
  return sbx;
}

async function enhanced(proj, hostWav, guestWavs) {
  const slug = path.basename(proj), sbx = await workspace(proj, "enhanced", { vcpus: 4, writable: true });
  try {
    // drop the links to last run's outputs so unpack and gate write new files, not through links into the drive
    await sh(sbx, "enhanced", "rm -f /work/proj/raw/*-audio-enhanced.wav /work/proj/raw/host-audio-enhanced-gated.wav", { quiet: true });
    await sh(sbx, "enhanced", "pip install -q numpy 2>&1 | tail -1", { quiet: true });
    await sh(sbx, "enhanced", "mkdir -p /work/in", { quiet: true });
    await upload(sbx, hostWav, "/work/in/host.wav");
    for (const [i, g] of guestWavs.entries()) await upload(sbx, g, `/work/in/guest${i}.wav`);
    // halves split by sample (enhance/guest-used-split.json) rejoin by stream copy, sample-exact
    await sh(sbx, "enhanced", `cd /work/in && ls guest*.wav | sed "s/.*/file '&'/" > l.txt && ffmpeg -v error -y -f concat -safe 0 -i l.txt -c copy guest.wav`, { quiet: true });
    const E = "python3 /work/skill/scripts/podcast/enhance_pack.py /work/proj";
    await sh(sbx, "enhanced", `${E} unpack host /work/in/host.wav 2>&1 | tail -1 && ${E} unpack guest /work/in/guest.wav 2>&1 | tail -1`);
    const gate = await sh(sbx, "enhanced", "cd /work/skill && python3 scripts/podcast/gate_host_audio.py /work/proj 2>&1");
    fs.mkdirSync(path.join(proj, "enhance"), { recursive: true });
    fs.writeFileSync(path.join(proj, "enhance/gate-report.txt"), gate + "\n");
    await sh(sbx, "enhanced", `cd /work/proj/raw && cp host-audio-enhanced.wav guest-audio-enhanced.wav host-audio-enhanced-gated.wav /media/${slug}/raw/ && ls -la /media/${slug}/raw | grep enhanced`);
    log("enhanced", "gate report -> enhance/gate-report.txt");
  } finally { await stop(sbx, "enhanced"); }
}

async function assemble(proj) {
  const sbx = await workspace(proj, "assemble");
  const ex = path.join(proj, "exports"), P = "/work/proj";
  try {
    const cj = JSON.parse(fs.readFileSync(path.join(proj, "edit/chapters.json"), "utf8"));
    const blocks = ["ch00.mp4", "intro.mp4", ...cj.chapters.filter((c) => c.id !== "ch00").map((c) => `${c.id}.mp4`), "outro.mp4"];
    for (const b of blocks) {
      if (!fs.existsSync(path.join(ex, b))) throw new Error(`missing exports/${b}`);
      const s = Date.now(); await upload(sbx, path.join(ex, b), `${P}/exports/${b}`);
      log("assemble", `${b} up in ${((Date.now() - s) / 1000).toFixed(0)}s`);
    }
    // cut.py --audio-only writes the re-cut mixes into each chapter's comp assets dir
    await sh(sbx, "assemble", `cd ${P} && for c in ${cj.chapters.map((c) => c.id).join(" ")}; do mkdir -p comp/chapters/$c/assets; done`, { quiet: true });
    // opening = cold open + intro, the join command from make_intro.py's docstring
    await sh(sbx, "assemble", `cd ${P} && ffmpeg -v error -y -i exports/ch00.mp4 -i exports/intro.mp4 -filter_complex ` +
      `"[0:v]fps=30,format=yuv420p,setsar=1[v0];[1:v]fps=30,format=yuv420p,setsar=1[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" ` +
      `-map "[v]" -map "[a]" -c:v libx264 -crf 18 -c:a aac -b:a 256k exports/opening.mp4 && echo opening joined`);
    const sw = await sh(sbx, "assemble", `cd ${P}/raw && a=""; [ -e host-audio-enhanced-gated.wav ] && a="--host-audio raw/host-audio-enhanced-gated.wav"; ` +
      `if [ -e guest-audio-enhanced-gated.wav ]; then a="$a --guest-audio raw/guest-audio-enhanced-gated.wav"; elif [ -e guest-audio-enhanced.wav ]; then a="$a --guest-audio raw/guest-audio-enhanced.wav"; fi; echo "$a"`, { quiet: true });
    log("assemble", `audio: ${sw.trim() || "original tracks"}`);
    await sh(sbx, "assemble", `cd /work/skill && python3 scripts/podcast/assemble.py ${P} ${sw.trim()} 2>&1 | tail -20`);
    for (const f of ["exports/opening.mp4", "exports/final/episode.mp4", "exports/final/episode-audio.m4a", "exports/final/youtube-chapters.txt"]) {
      const local = path.join(proj, f);
      if (fs.existsSync(local)) { fs.mkdirSync(path.join(path.dirname(local), ".prev"), { recursive: true }); fs.renameSync(local, path.join(path.dirname(local), ".prev", path.basename(local))); }
      await retry(() => sbx.downloadFile({ path: `${P}/${f}` }, { path: local }, { mkdirRecursive: true }), "assemble");
    }
    log("assemble", "done -> exports/final/episode.mp4");
  } finally { await stop(sbx, "assemble"); }
}

// Full-length enhanced tracks from per-episode Adobe files (raw/enhance/), via the episode's own edit/enhance_assemble.py,
// then the ghost gate on every enhanced track that exists. Writes to the drive, so never alongside media or enhanced.
async function tracks(proj) {
  const slug = path.basename(proj), sbx = await workspace(proj, "tracks", { vcpus: 4, writable: true });
  try {
    const E = path.join(proj, "raw/enhance");
    await sh(sbx, "tracks", "rm -f /work/proj/raw/*-audio-enhanced.wav /work/proj/raw/*-audio-enhanced-gated.wav && mkdir -p /work/proj/raw/enhance", { quiet: true });
    await sh(sbx, "tracks", "pip install -q numpy 2>&1 | tail -1", { quiet: true });
    const names = fs.readdirSync(E).filter((f) => f.endsWith(".wav") || f.endsWith(".json"));
    for (const f of names) {
      if (/-enhanced\.wav$/.test(f) || f.endsWith(".json")) { const s = Date.now(); await upload(sbx, path.join(E, f), `/work/proj/raw/enhance/${f}`); log("tracks", `${f} up in ${((Date.now() - s) / 1000).toFixed(0)}s`); }
      else await sh(sbx, "tracks", `cd /work/proj/raw/enhance && ffmpeg -v error -y -f lavfi -i anullsrc=r=48000:cl=mono -t ${execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path.join(E, f)]).toString().trim()} '${f}'`, { quiet: true });
    }
    await sh(sbx, "tracks", "cd /work/proj && python3 edit/enhance_assemble.py build 2>&1");
    let rep = "";
    for (const t of ["host", "guest"]) {
      const has = (await sh(sbx, "tracks", `test -e /work/proj/raw/${t}-audio-enhanced.wav && echo yes || echo no`, { quiet: true })).trim();
      // a track this build did not produce must not stay on the drive, or assemble would pick up the stale file
      if (has !== "yes") { await sh(sbx, "tracks", `rm -f /media/${slug}/raw/${t}-audio-enhanced.wav /media/${slug}/raw/${t}-audio-enhanced-gated.wav`, { quiet: true }); continue; }
      rep += `== ${t}\n` + await sh(sbx, "tracks", `cd /work/skill && python3 scripts/podcast/gate_host_audio.py /work/proj --track ${t} 2>&1`);
      await sh(sbx, "tracks", `cd /work/proj/raw && cp ${t}-audio-enhanced.wav ${t}-audio-enhanced-gated.wav /media/${slug}/raw/`, { quiet: true });
    }
    fs.writeFileSync(path.join(proj, "edit/gate-report.txt"), rep + "\n");
    await sh(sbx, "tracks", `ls -la /media/${slug}/raw | grep enhanced`);
    log("tracks", "gate report -> edit/gate-report.txt");
  } finally { await stop(sbx, "tracks"); }
}

// Render a standalone HyperFrames project (comp/intro, comp/outro from make_intro.py) in its own sandbox.
async function comps(proj, names) {
  const { snapshotId } = cfg();
  if (!snapshotId) throw new Error(`no base snapshot in ${CFG}; run setup first`);
  const res = await Promise.all(names.map(async (name) => {
    const sbx = await Sandbox.create({ ...auth, source: { type: "snapshot", snapshotId }, resources: { vcpus: 8 }, timeout: 30 * 60e3, persistent: false });
    log(name, `sandbox ${sbx.name}`);
    try {
      const tar = tarOf(`${name}.tgz`, path.join(proj, "comp", name), ["."], [".hyperframes", "snapshots"]);
      await retry(() => sbx.writeFiles([{ path: `/work/${name}.tgz`, content: fs.readFileSync(tar) }]), name);
      await sh(sbx, name, `mkdir -p /work/c && tar -xzf /work/${name}.tgz -C /work/c`, { quiet: true });
      await sh(sbx, name, `cd /work/c && npx --yes ${HF} render -o /work/${name}.mp4 > /work/render.log 2>&1; grep -q "Render complete" /work/render.log && grep -E "MB ·" /work/render.log | tr -s ' '`);
      const local = path.join(proj, "exports", `${name}.mp4`);
      if (fs.existsSync(local)) { fs.mkdirSync(path.join(proj, "exports/.prev"), { recursive: true }); fs.renameSync(local, path.join(proj, "exports/.prev", `${name}.mp4`)); }
      await retry(() => sbx.downloadFile({ path: `/work/${name}.mp4` }, { path: local }, { mkdirRecursive: true }), name);
      log(name, `done -> exports/${name}.mp4`);
      return true;
    } catch (e) { log(name, `FAILED: ${e.message}`); return false; } finally { await stop(sbx, name); }
  }));
  if (res.some((r) => !r)) process.exitCode = 1;
}

// Guest headshot cutout for the covers (podcast-packaging.md). rembg needs ~1 GB of model and onnxruntime: too heavy
// for the laptop, so it runs in a sandbox. Installed without deps (numba/llvmlite fail on new Pythons) and with
// pymatting stubbed, since only alpha matting uses it.
async function cutout(photo, out) {
  // 8 vCPUs for the 16 GB of memory: bria-rmbg is OOM-killed in the 8 GB of a 4-vCPU sandbox
  const sbx = await Sandbox.create({ ...auth, resources: { vcpus: 8 }, timeout: 30 * 60e3, persistent: false });
  log("cutout", `sandbox ${sbx.name}`);
  try {
    await sh(sbx, "cutout", "mkdir -p /work && python3 --version");
    await retry(() => sbx.writeFiles([{ path: "/work/in.img", content: fs.readFileSync(photo) }]), "cutout");
    await sh(sbx, "cutout", "python3 -m venv /work/v && /work/v/bin/pip install -q --no-deps rembg && /work/v/bin/pip install -q " +
      "onnxruntime numpy pillow opencv-python-headless scipy pooch jsonschema tqdm scikit-image 2>&1 | tail -2", { quiet: true });
    await sh(sbx, "cutout", `SP=$(/work/v/bin/python -c "import site;print(site.getsitepackages()[0])") && mkdir -p $SP/pymatting/alpha $SP/pymatting/foreground $SP/pymatting/util && ` +
      `touch $SP/pymatting/__init__.py $SP/pymatting/alpha/__init__.py $SP/pymatting/foreground/__init__.py $SP/pymatting/util/__init__.py && ` +
      `echo "def estimate_alpha_cf(*a, **k): raise NotImplementedError" > $SP/pymatting/alpha/estimate_alpha_cf.py && ` +
      `echo "def estimate_foreground_ml(*a, **k): raise NotImplementedError" > $SP/pymatting/foreground/estimate_foreground_ml.py && ` +
      `echo "def stack_images(*a, **k): raise NotImplementedError" > $SP/pymatting/util/util.py`, { quiet: true });
    await sh(sbx, "cutout", `cd /work && /work/v/bin/python -c "
from rembg import remove, new_session
from PIL import Image
im = remove(Image.open('in.img').convert('RGB'), session=new_session('bria-rmbg'))
im.save('cutout.png')
bg = Image.new('RGBA', im.size, (160, 255, 60, 255)); bg.alpha_composite(im); bg.convert('RGB').save('check.png')
print('cutout', im.size, im.getbbox())
" > /work/cutout.log 2>&1; test -s /work/cutout.png && grep "^cutout" /work/cutout.log || { grep -v "%|" /work/cutout.log | tail -12; exit 1; }`);
    // downloadFile returns null instead of throwing on a missing file: check the result
    if (!(await retry(() => sbx.downloadFile({ path: "/work/cutout.png" }, { path: out }, { mkdirRecursive: true }), "cutout"))) throw new Error("cutout: no cutout.png");
    const chk = out.replace(/\.png$/, "") + "-check.png";
    await retry(() => sbx.downloadFile({ path: "/work/check.png" }, { path: chk }, { mkdirRecursive: true }), "cutout");
    log("cutout", `done -> ${out} (check the mask: ${chk})`);
  } finally { await stop(sbx, "cutout"); }
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
else if (cmd === "enhanced" && ids.length >= 2) await enhanced(path.resolve(proj), ids[0], ids.slice(1));
else if (cmd === "assemble") await assemble(path.resolve(proj));
else if (cmd === "tracks") await tracks(path.resolve(proj));
else if (cmd === "comp" && ids.length) await comps(path.resolve(proj), ids);
else if (cmd === "cutout" && ids.length) await cutout(path.resolve(proj), path.resolve(ids[0]));
else console.log("usage: studio.mjs setup | media <project> | build|run <project> <chNN|short id> ... | enhanced <project> <host.wav> <guest.wav>... | assemble <project> | tracks <project> | comp <project> intro outro | cutout <photo> <cutout.png>");
