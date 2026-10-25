// Phone-width page captures for short prints on Vercel Sandbox (the laptop runs no browser): a 460 css px viewport
// @2x wraps the paragraph inside ~920 px, so a crop never bleeds words off its edges (podcast-shorts.md section 3).
//   node --env-file=<env> scripts/podcast/sandbox/capture.mjs <out-dir> <jobs.json>
// jobs.json: [{"name", "url", "mark": "<exact phrase to highlight>", "maxH"?: css px}] -> <out>/<name>.png (the
// mark's paragraph, at most maxH tall, default 440), <name>.page.png (viewport) and <name>.json (mark box in % of the
// png, clip, paragraph text to verify). Crop whole lines afterwards and re-measure the mark.
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const SDK_DIR = process.env.RECOUP_SANDBOX_SDK || path.join(os.homedir(), ".cache/recoup/podcast-sandbox");
const { Sandbox } = await import(pathToFileURL(createRequire(path.join(SDK_DIR, "package.json")).resolve("@vercel/sandbox")));
const CFG = JSON.parse(fs.readFileSync(path.join(os.homedir(), ".config/recoup/podcast-sandbox.json"), "utf8"));
const auth = { token: process.env.VERCEL_TOKEN, teamId: process.env.VERCEL_TEAM_ID, projectId: process.env.VERCEL_PROJECT_ID };
if (!auth.token || !auth.teamId || !auth.projectId) { console.error("set VERCEL_TOKEN, VERCEL_TEAM_ID, VERCEL_PROJECT_ID (--env-file)"); process.exit(1); }
const [outDir, jobsFile] = process.argv.slice(2);
if (!outDir || !jobsFile) { console.error("usage: capture.mjs <out-dir> <jobs.json>"); process.exit(1); }
const jobs = JSON.parse(fs.readFileSync(jobsFile, "utf8"));
fs.mkdirSync(outDir, { recursive: true });

const inner = `
const puppeteer = require(process.env.PPT);
const jobs = ${JSON.stringify(jobs)};
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  for (const j of jobs) {
    const p = await b.newPage();
    await p.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1');
    await p.setViewport({ width: 460, height: 1000, deviceScaleFactor: 2, isMobile: true });
    try { await p.goto(j.url, { waitUntil: 'networkidle2', timeout: 60000 }); } catch (e) { console.log(j.name, 'goto', e.message); }
    await new Promise(r => setTimeout(r, 2000));
    const r = await p.evaluate((P, maxH) => {
      for (const el of document.querySelectorAll('*')) { const s = getComputedStyle(el); if (s.position === 'fixed' || s.position === 'sticky') el.style.setProperty('display', 'none', 'important'); }
      document.querySelectorAll('[id*=cookie],[class*=cookie],[class*=consent],[id*=consent]').forEach(e => e.remove());
      const norm = x => x.replace(/\\s+/g, ' ');
      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) { const i = norm(n.textContent).indexOf(P); if (i >= 0 && n.parentElement.offsetParent) break; }
      if (!n) return { err: 'phrase not found' };
      let st = n.textContent.indexOf(P); if (st < 0) st = norm(n.textContent).indexOf(P);
      const rg = document.createRange(); rg.setStart(n, st); rg.setEnd(n, Math.min(n.textContent.length, st + P.length));
      let blk = n.parentElement; while (blk.parentElement && getComputedStyle(blk).display === 'inline') blk = blk.parentElement;
      blk.scrollIntoView({ block: 'center', behavior: 'instant' });
      const m = rg.getBoundingClientRect(), k = blk.getBoundingClientRect();
      return { m: [m.left + scrollX, m.top + scrollY, m.width, m.height], k: [k.left + scrollX, k.top + scrollY, k.width, k.height], sy: scrollY, txt: norm(blk.textContent).slice(0, 600) };
    }, j.mark, j.maxH || 440);
    if (r.err) { console.log(j.name, r.err); continue; }
    const [kx, ky, kw, kh] = r.k, [mx, my, mw, mh] = r.m, maxH = j.maxH || 440;
    let y0 = ky - 14, h = kh + 28;
    if (h > maxH) { y0 = Math.max(ky - 14, Math.min(my + mh / 2 - maxH / 2, ky + kh + 14 - maxH)); h = maxH; }
    const x0 = Math.max(0, kx - 12), cw = Math.min(460 - x0, kw + 24);
    await p.screenshot({ path: '/work/out/' + j.name + '.png', clip: { x: x0, y: y0, width: cw, height: h }, captureBeyondViewport: true });
    await p.screenshot({ path: '/work/out/' + j.name + '.page.png' });
    const pad = 4;
    const mark = [(mx - x0 - pad) / cw * 100, (my - y0 - pad) / h * 100, (mw + 2 * pad) / cw * 100, (mh + 2 * pad) / h * 100].map(v => +v.toFixed(1));
    require('fs').writeFileSync('/work/out/' + j.name + '.json', JSON.stringify({ url: j.url, mark, clip: [x0, y0, cw, h], text: r.txt }, null, 1));
    console.log(j.name, 'ok', JSON.stringify(mark));
  }
  await b.close();
})();`;

const t0 = Date.now();
const sbx = await Sandbox.create({ ...auth, source: { type: "snapshot", snapshotId: CFG.snapshotId }, resources: { vcpus: 2 }, timeout: 15 * 60e3, persistent: false });
try {
  await sbx.writeFiles([{ path: "/work/cap.cjs", content: Buffer.from(inner) }]);
  const run = async (s) => { const r = await sbx.runCommand({ cmd: "bash", args: ["-lc", s] }); const o = (await r.stdout()) + (await r.stderr()); return [r.exitCode, o]; };
  // the snapshot carries puppeteer-core (npx cache) and Chrome headless shell (hyperframes); find both
  const [, probe] = await run(`PPT=$(find / -path '*node_modules/puppeteer-core/package.json' 2>/dev/null | head -1); CHROME=$(find / \\( -name chrome -o -name chrome-headless-shell \\) -type f -perm -u+x 2>/dev/null | head -1); echo "$PPT|$CHROME"`);
  const [ppt, chrome] = probe.trim().split("\n").pop().split("|");
  console.log("puppeteer", ppt, "chrome", chrome);
  const [code, out] = await run(`mkdir -p /work/out && cd /work && PPT=${path.dirname(ppt)} CHROME=${chrome} node cap.cjs 2>&1 | tail -20; tar -czf /work/out.tgz -C /work/out .`);
  console.log(out);
  const tgz = path.join(outDir, "out.tgz");
  await sbx.downloadFile({ path: "/work/out.tgz" }, { path: tgz });
  const { execFileSync } = await import("node:child_process");
  execFileSync("tar", ["-xzf", tgz, "-C", outDir]); fs.rmSync(tgz);
} finally { await sbx.stop().catch(() => {}); console.log(`wall ${((Date.now() - t0) / 1000).toFixed(0)} s`); }
