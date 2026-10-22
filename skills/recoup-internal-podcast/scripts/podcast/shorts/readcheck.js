async () => {
  // Reading-time check: every text outside the captions must stay fully on screen for letters / 15 + 1.5 s.
  await new Promise(r => setTimeout(r, 1500));
  const tl = window.__timelines && window.__timelines.main; if (!tl) return 'no timeline';
  tl.pause();
  const D = tl.duration();
  const els = [...document.querySelectorAll('body *')].filter(e => !e.closest('#caps') && e.children.length === 0 && e.textContent.trim().length > 1 && !['SCRIPT', 'STYLE'].includes(e.tagName));
  const vis = e => { let n = e; while (n && n !== document.body) { const s = getComputedStyle(n); if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) < 0.6) return false; n = n.parentElement; } const r = e.getBoundingClientRect(); return r.width > 0 && r.left >= -2 && r.top >= -2 && r.right <= 1082 && r.bottom <= 1922; };
  const runs = new Map(), open = new Map();
  for (let t = 0; t <= D + 1e-6; t += 0.04) {
    tl.seek(t, false);
    for (const e of els) { const v = vis(e);
      if (v && !open.has(e)) open.set(e, t);
      if (!v && open.has(e)) { (runs.get(e) || runs.set(e, []).get(e)).push([open.get(e), t]); open.delete(e); } }
  }
  for (const [e, a] of open) (runs.get(e) || runs.set(e, []).get(e)).push([a, D]);
  const fails = [];
  for (const [e, rs] of runs) { const txt = e.textContent.trim().replace(/\s+/g, ' '), need = txt.length / 15 + 1.5;
    for (const [a, b] of rs) if (b - a + 0.05 < need && b < D - 0.05) fails.push({ txt: txt.slice(0, 60), at: +a.toFixed(2), held: +(b - a).toFixed(2), need: +need.toFixed(2) }); }
  return { D: +D.toFixed(2), fails, shown: [...runs].map(([e, rs]) => e.textContent.trim().slice(0, 40) + ' ' + rs.map(([a, b]) => a.toFixed(1) + '-' + b.toFixed(1)).join(',')) };
}
