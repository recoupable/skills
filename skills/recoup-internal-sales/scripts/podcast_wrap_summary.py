"""Podcast wrap-up one-sheet: an executive summary of the episode run, as a one-page Letter PDF.

The page is the episode recap (summary, takeaways, the guest's own lines) and how every clip did; the links
live in the CSV that goes out with it. Same look as the guest brief and the timeline PDF (Recoup Sky brand
kit: lockup, sky labels, meta strip, pale card, forest note, box-shadow rules).

  python3 podcast_wrap_summary.py posts.csv summary.json --brand <path>/recoup-sky --out recap.html --pdf recap.pdf

posts.csv  columns item,title,date,platform,account,url,views,metric,as_of
           item = "Full episode" or "Clip <n>"; date = YYYY-MM-DD; views blank where the platform has no count.
summary.json  guest, role, company, role_url, slug, campaign, label, length, summary, takeaways[], quotes[],
              as_of, sources (one line: when the numbers were pulled and what each platform's number means).
Checks (exit 1): one page, no em/en dashes in the text."""
import argparse, csv, datetime, html, json, os, re, subprocess, sys

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")  # headless Chrome or Chromium
EPISODE_ORDER = ["YouTube", "Spotify", "Apple Podcasts"]
CLIP_ORDER = ["YouTube", "LinkedIn", "Instagram", "X"]
e = html.escape

CSS = """
  @page { size: Letter; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: var(--recoup-white); }
  body { width: 8.5in; height: 11in; overflow: hidden; font-family: var(--brand-body-font), sans-serif;
         color: var(--recoup-ink); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  a { color: var(--recoup-link); text-decoration: underline; text-decoration-thickness: 1px;
      text-underline-offset: 2px; text-decoration-color: rgba(8,123,171,.4); }
  .page { padding: 0.5in 0.6in 0.45in; height: 100%; display: flex; flex-direction: column; }
  .page > * { flex-shrink: 0; }
  header { display: flex; justify-content: space-between; align-items: center; }
  header img { width: 118px; height: auto; display: block; }
  .kicker { font-size: 9.5px; color: var(--recoup-muted); }
  .hero { margin-top: 0.2in; }
  .hero .label, .sec { font-size: 9.5px; color: var(--recoup-sky); }
  h1 { font-family: var(--brand-display-font), sans-serif; font-weight: 500; font-size: 27px; line-height: 1.1;
       letter-spacing: -0.02em; margin-top: 7px; max-width: 6.6in; }
  .guest { font-size: 13px; color: var(--recoup-muted); margin-top: 8px; }
  .guest strong { color: var(--recoup-ink); font-weight: 500; }
  .meta { display: flex; margin-top: 0.17in; border-radius: 10px; box-shadow: 0 0 0 1px var(--recoup-border); overflow: hidden; }
  .meta div { flex: 1; padding: 8px 13px; }
  .meta div + div { box-shadow: -1px 0 0 var(--recoup-border); }
  .meta .recoup-label { font-size: 8.5px; color: var(--recoup-muted); display: block; }
  .meta b { font-weight: 500; font-size: 12.5px; display: block; margin-top: 3px; }
  .meta .hl { background: var(--recoup-pale); }
  .summary { font-size: 11.5px; line-height: 1.48; margin-top: 0.13in; }
  .listen { display: flex; gap: 7px; margin-top: 8px; align-items: center; font-size: 10px; color: var(--recoup-muted); }
  .chip { font-size: 10.5px; padding: 4px 10px; border-radius: 999px; box-shadow: 0 0 0 1px var(--recoup-border);
          text-decoration: none; color: var(--recoup-ink); }
  .cols { display: grid; grid-template-columns: 1.15fr 1fr; gap: 14px; margin-top: 0.13in; }
  .box { border-radius: 10px; box-shadow: 0 0 0 1px var(--recoup-border); padding: 11px 14px; }
  .box.pale { background: var(--recoup-pale); box-shadow: none; }
  ol.take { list-style: none; margin-top: 6px; counter-reset: t; }
  ol.take li { counter-increment: t; display: grid; grid-template-columns: 18px 1fr; font-size: 10.8px; line-height: 1.42;
               padding: 5px 0; box-shadow: 0 -1px 0 var(--recoup-border); }
  ol.take li:first-child { box-shadow: none; }
  ol.take li::before { content: counter(t); font-family: var(--brand-label-font, monospace); font-size: 9px; color: var(--recoup-sky); padding-top: 2px; }
  .q { font-size: 11.5px; line-height: 1.42; padding: 6px 0; box-shadow: 0 -1px 0 #DCE8EE; }
  .q:first-of-type { box-shadow: none; }
  .q::before { content: "\\201C"; color: var(--recoup-sky); margin-right: 1px; }
  .q::after { content: "\\201D"; color: var(--recoup-sky); }
  .perf { margin-top: 0.14in; }
  .perf-head { display: flex; justify-content: space-between; align-items: baseline; }
  .perf-head span:last-child { font-size: 9px; color: var(--recoup-muted); }
  table { width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 11px; }
  th { text-align: right; font-weight: 400; font-size: 8.5px; color: var(--recoup-muted); padding: 0 0 5px; }
  th.l { text-align: left; }
  td { padding: 6px 0; border-top: 1px solid var(--recoup-border); text-align: right; font-variant-numeric: tabular-nums; }
  td.n { width: 0.3in; text-align: left; font-size: 9px; color: var(--recoup-sky); }
  td.t { text-align: left; padding-right: 10px; }
  td.t span { color: var(--recoup-muted); font-size: 9.5px; margin-left: 6px; }
  td.v { width: 0.66in; color: var(--recoup-muted); }
  td.v.top { color: var(--recoup-ink); font-weight: 500; }
  td.tot { width: 0.7in; font-weight: 500; }
  tr.lead td.tot span { background: var(--recoup-lime); color: var(--recoup-forest); padding: 2px 7px; border-radius: 999px; }
  tr.sum td { font-weight: 500; border-top: 1px solid var(--recoup-ink); }
  .note { margin-top: auto; border-radius: 10px; background: var(--recoup-forest); color: #C9D6D2;
          padding: 11px 18px; font-size: 11.5px; line-height: 1.5; }
  .note b { color: var(--recoup-white); font-weight: 500; }
  footer { display: flex; justify-content: space-between; gap: 20px; margin-top: 0.13in; font-size: 8.5px; color: var(--recoup-muted); line-height: 1.4; }
  footer a { text-decoration: none; white-space: nowrap; }
"""


def n(v):
    return f"{v:,}"


def build(rows, s, brand_rel):
    eps = [r for r in rows if r["item"].lower().startswith("full episode")]
    clips = {}
    for r in rows:
        if r["item"].lower().startswith("clip"):
            clips.setdefault(r["item"], []).append(r)
    order = sorted(clips, key=lambda k: int(re.sub(r"\D", "", k) or 0))
    views = lambda r: int(r["views"]) if r.get("views", "").strip() else None
    total = sum(v for r in rows if (v := views(r)) is not None)
    ep_date = min(r["date"] for r in eps) if eps else min(r["date"] for r in rows)
    first_clip, last_clip = (min(r["date"] for c in clips.values() for r in c), max(r["date"] for c in clips.values() for r in c)) if clips else (ep_date, ep_date)
    fmt = lambda d, f: datetime.date.fromisoformat(d).strftime(f)

    # clip table: per-platform views, best platform per clip in ink, the top clip's total in a lime pill
    totals = {k: sum(views(r) or 0 for r in clips[k]) for k in order}
    lead = max(totals, key=totals.get) if totals else None
    col = {p: 0 for p in CLIP_ORDER}
    body = ""
    for k in order:
        cs = {r["platform"]: r for r in clips[k]}
        vals = {p: views(cs[p]) if p in cs else None for p in CLIP_ORDER}
        best = max((p for p in CLIP_ORDER if vals[p] is not None), key=lambda p: vals[p], default=None)
        for p in CLIP_ORDER: col[p] += vals[p] or 0
        cells = "".join(f'<td class="v{" top" if p == best else ""}">{n(vals[p]) if vals[p] is not None else ""}</td>' for p in CLIP_ORDER)
        first = clips[k][0]
        body += (f'<tr{" class=lead" if k == lead else ""}><td class="n recoup-label">{e(re.sub(r"(?i)clip ", "", k))}</td>'
                 f'<td class="t">{e(first["title"])}</td>{cells}'
                 f'<td class="tot"><span>{n(totals[k])}</span></td></tr>')
    body += ('<tr class="sum"><td></td><td class="t">All clips</td>' + "".join(f'<td class="v">{n(col[p])}</td>' for p in CLIP_ORDER)
             + f'<td class="tot">{n(sum(totals.values()))}</td></tr>')

    chips = "".join(f'<a class="chip" href="{e(r["url"])}">{e(r["platform"])}</a>'
                    for r in sorted(eps, key=lambda r: EPISODE_ORDER.index(r["platform"]) if r["platform"] in EPISODE_ORDER else 99))
    role = e(s["role"])
    if s.get("role_url") and s.get("company"):
        role = role.replace(e(s["company"]), f'<a href="{e(s["role_url"])}">{e(s["company"])}</a>')
    first_name = s["guest"].split()[0]
    utm = f"utm_source=pdf&amp;utm_medium=guest-wrap-up&amp;utm_campaign={e(s['campaign'])}&amp;utm_content={e(s['slug'])}"
    title = eps[0]["title"] if eps else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Recoup Podcast recap: {e(s['guest'])}</title>
<link rel="stylesheet" href="{e(brand_rel)}/brand.css">
<style>{CSS}</style></head>
<body><div class="page">
  <header><img src="{e(brand_rel)}/logos/lockup-ink.svg" alt="Recoup"><span class="kicker recoup-label">Recoup Podcast · Episode recap</span></header>
  <section class="hero"><span class="label recoup-label">{e(s.get('label', 'Episode recap'))}</span>
    <h1>{e(title)}</h1>
    <p class="guest">With <strong>{e(s['guest'])}</strong>, {role}</p></section>
  <div class="meta">
    <div><span class="recoup-label">Published</span><b>{fmt(ep_date, "%B %-d")}</b></div>
    <div><span class="recoup-label">Length</span><b>{e(s['length'])}</b></div>
    <div><span class="recoup-label">Clips</span><b>{len(clips)}, {fmt(first_clip, "%b %-d")} to {fmt(last_clip, "%-d")}</b></div>
    <div class="hl"><span class="recoup-label">Views so far</span><b>{n(total)}</b></div>
  </div>
  <p class="summary">{e(s['summary'])}</p>
  <div class="listen">Full episode: {chips}</div>
  <div class="cols">
    <div class="box"><span class="sec recoup-label">Key takeaways</span><ol class="take">{"".join(f"<li>{e(t)}</li>" for t in s['takeaways'])}</ol></div>
    <div class="box pale"><span class="sec recoup-label">In {e(first_name)}'s words</span>{"".join(f'<p class="q">{e(q)}</p>' for q in s['quotes'])}</div>
  </div>
  <div class="perf"><div class="perf-head"><span class="sec recoup-label">How the clips did</span><span>Views as of {e(s['as_of'])}</span></div>
    <table><tr><th></th><th class="l">Clip</th>{"".join(f"<th>{e(p)}</th>" for p in CLIP_ORDER)}<th>Total</th></tr>{body}</table></div>
  <div class="note"><b>Every link is in the attached spreadsheet,</b> one row per post, to reshare whichever channels suit you.</div>
  <footer><span>{e(s['sources'])}</span>
    <a href="https://recoupable.dev/podcast?{utm}">recoupable.dev/podcast</a></footer>
</div></body></html>
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv"); p.add_argument("summary")
    p.add_argument("--brand", required=True, help="path to the recoup-sky brand kit folder")
    p.add_argument("--out", required=True); p.add_argument("--pdf", required=True)
    a = p.parse_args()
    rows = list(csv.DictReader(open(a.csv, newline="")))
    s = json.load(open(a.summary))
    brand_rel = os.path.relpath(os.path.abspath(a.brand), os.path.dirname(os.path.abspath(a.out)))
    open(a.out, "w").write(build(rows, s, brand_rel))
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={os.path.abspath(a.pdf)}", "file://" + os.path.abspath(a.out)],
                   check=True, capture_output=True)
    fails = []
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", a.pdf], capture_output=True, text=True).stdout).group(1))
    if pages != 1: fails.append(f"{pages} pages")
    text = subprocess.run(["pdftotext", a.pdf, "-"], capture_output=True, text=True).stdout
    if re.search("[–—]", text): fails.append("em/en dash in text")
    print(f"{a.pdf}: {pages} page, {len(rows)} posts" + ("" if not fails else "\nFAIL: " + "; ".join(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
