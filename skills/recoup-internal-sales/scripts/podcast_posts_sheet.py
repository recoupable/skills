"""Podcast wrap-up one-sheet: every post of an episode run, on every platform, as a one-page Letter PDF.

Same look as the guest brief and the timeline PDF (Recoup Sky brand kit: lockup, sky labels, forest note,
border-as-box-shadow tables). Input is the CSV that goes out with it, so the PDF and the CSV never disagree.

  python3 podcast_posts_sheet.py posts.csv --brand <path>/recoup-sky --guest "Name" --role "Title, Company" \
      --role-url https://company.example --slug guest-slug --campaign 2026-10 --out sheet.html --pdf sheet.pdf

CSV columns: item,title,date,platform,account,url  (item = "Full episode" or "Clip <n>"; date = YYYY-MM-DD).
The HTML is written next to the PDF and links the brand kit by relative path, like the other guest PDFs.
Checks (exit 1): one page, no em/en dashes, every URL in the CSV is a link in the PDF."""
import argparse, csv, datetime, html, os, re, subprocess, sys

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")  # headless Chrome or Chromium
EPISODE_ORDER = ["YouTube", "Spotify", "Apple Podcasts", "LinkedIn"]
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
  .page { padding: 0.55in 0.6in 0.5in; height: 100%; display: flex; flex-direction: column; }
  .page > * { flex-shrink: 0; }
  header { display: flex; justify-content: space-between; align-items: center; }
  header img { width: 118px; height: auto; display: block; }
  .kicker { font-size: 9.5px; color: var(--recoup-muted); }
  .hero { margin-top: 0.3in; }
  .hero .label { font-size: 10px; color: var(--recoup-sky); }
  h1 { font-family: var(--brand-display-font), sans-serif; font-weight: 500; font-size: 34px; line-height: 1.08;
       letter-spacing: -0.02em; margin-top: 8px; }
  .guest { font-size: 14px; color: var(--recoup-muted); margin-top: 9px; }
  .guest strong { color: var(--recoup-ink); font-weight: 500; }
  .meta { display: flex; margin-top: 0.22in; border-radius: 10px; box-shadow: 0 0 0 1px var(--recoup-border); overflow: hidden; }
  .meta div { flex: 1; padding: 9px 13px; }
  .meta div + div { box-shadow: -1px 0 0 var(--recoup-border); }
  .meta .recoup-label { font-size: 8.5px; color: var(--recoup-muted); display: block; }
  .meta b { font-weight: 500; font-size: 12.5px; display: block; margin-top: 3px; }
  .ep { margin-top: 0.22in; border-radius: 10px; background: var(--recoup-pale); padding: 13px 16px; }
  .sec { font-size: 9px; color: var(--recoup-sky); }
  .ep h2 { font-weight: 500; font-size: 16px; letter-spacing: -0.01em; margin-top: 4px; }
  .links { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 9px; }
  .chip { font-size: 11.5px; padding: 5px 11px; border-radius: 999px; background: var(--recoup-white);
          box-shadow: 0 0 0 1px var(--recoup-border); text-decoration: none; color: var(--recoup-ink); }
  .chip span { color: var(--recoup-muted); }
  .clips { margin-top: 0.2in; }
  table { width: 100%; border-collapse: collapse; margin-top: 7px; font-size: 11.5px; }
  th { text-align: left; font-weight: 400; font-size: 8.5px; color: var(--recoup-muted); padding: 0 0 6px; }
  td { padding: 11px 0; vertical-align: top; border-top: 1px solid var(--recoup-border); }
  td.n { width: 0.42in; font-size: 9.5px; color: var(--recoup-sky); padding-top: 13px; }
  td.t { padding-right: 12px; }
  td.t b { font-weight: 500; display: block; line-height: 1.3; font-size: 12.5px; }
  td.t span { font-size: 9.5px; color: var(--recoup-muted); }
  td.l { width: 0.8in; padding-top: 12px; }
  .note { margin-top: auto; border-radius: 10px; background: var(--recoup-forest); color: #C9D6D2;
          padding: 14px 18px; font-size: 12.5px; line-height: 1.5; }
  .note b { color: var(--recoup-white); font-weight: 500; }
  footer { display: flex; justify-content: space-between; margin-top: 0.16in; font-size: 9px; color: var(--recoup-muted); }
  footer a { text-decoration: none; }
"""


def day(d):
    return datetime.date.fromisoformat(d).strftime("%a, %b %-d")


def build(rows, a, brand_rel):
    eps = [r for r in rows if r["item"].lower().startswith("full episode")]
    clips = {}
    for r in rows:
        if r["item"].lower().startswith("clip"):
            clips.setdefault(r["item"], []).append(r)
    ep_title = eps[0]["title"] if eps else ""
    ep_date = min(r["date"] for r in eps) if eps else min(r["date"] for r in rows)
    last = max(r["date"] for r in rows)
    platforms = sorted({r["platform"] for r in rows})
    chips = "".join(
        f'<a class="chip" href="{e(r["url"])}">{e(r["platform"])} <span>· {e(r["account"])}</span></a>'
        for r in sorted(eps, key=lambda r: EPISODE_ORDER.index(r["platform"]) if r["platform"] in EPISODE_ORDER else 99))
    body_rows = ""
    for item in sorted(clips, key=lambda k: int(re.sub(r"\D", "", k) or 0)):
        cs = {r["platform"]: r for r in clips[item]}
        first = clips[item][0]
        cells = "".join(f'<td class="l">{"<a href=" + chr(34) + e(cs[p]["url"]) + chr(34) + ">" + e(p) + "</a>" if p in cs else ""}</td>'
                        for p in CLIP_ORDER)
        body_rows += (f'<tr><td class="n recoup-label">{e(re.sub(r"(?i)clip ", "", item))}</td>'
                      f'<td class="t"><b>{e(first["title"])}</b><span>{day(first["date"])}</span></td>{cells}</tr>')
    role = e(a.role)
    if a.role_url and a.company:
        role = role.replace(e(a.company), f'<a href="{e(a.role_url)}">{e(a.company)}</a>')
    utm = f"utm_source=pdf&amp;utm_medium=guest-wrap-up&amp;utm_campaign={e(a.campaign)}&amp;utm_content={e(a.slug)}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Recoup Podcast posts: {e(a.guest)}</title>
<link rel="stylesheet" href="{e(brand_rel)}/brand.css">
<style>{CSS}</style></head>
<body><div class="page">
  <header><img src="{e(brand_rel)}/logos/lockup-ink.svg" alt="Recoup"><span class="kicker recoup-label">Recoup Podcast · Every post</span></header>
  <section class="hero"><span class="label recoup-label">Your episode, everywhere it went</span>
    <h1>Every post, on every platform</h1>
    <p class="guest">With <strong>{e(a.guest)}</strong>, {role}</p></section>
  <div class="meta">
    <div><span class="recoup-label">Episode live</span><b>{datetime.date.fromisoformat(ep_date).strftime("%B %-d")}</b></div>
    <div><span class="recoup-label">Clips</span><b>{len(clips)}, one a day</b></div>
    <div><span class="recoup-label">Platforms</span><b>{len(platforms)}</b></div>
    <div><span class="recoup-label">Posts</span><b>{len(rows)}, through {datetime.date.fromisoformat(last).strftime("%b %-d")}</b></div>
  </div>
  <div class="ep"><span class="sec recoup-label">The full episode</span><h2>{e(ep_title)}</h2><div class="links">{chips}</div></div>
  <div class="clips"><span class="sec recoup-label">The clips</span>
    <table><tr><th></th><th>Clip</th>{"".join(f"<th>{e(p)}</th>" for p in CLIP_ORDER)}</tr>{body_rows}</table></div>
  <div class="note"><b>Share any of them.</b> {e(a.note)}</div>
  <footer><span>Questions: reply to Patrick Sweetman, Cofounder, Recoup</span>
    <a href="https://recoupable.dev/podcast?{utm}">recoupable.dev/podcast</a></footer>
</div></body></html>
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv"); p.add_argument("--brand", required=True, help="path to the recoup-sky brand kit folder")
    p.add_argument("--guest", required=True); p.add_argument("--role", required=True)
    p.add_argument("--company", default=""); p.add_argument("--role-url", default="")
    p.add_argument("--slug", required=True); p.add_argument("--campaign", required=True)
    p.add_argument("--note", default="Repost, quote or reshare whichever channels suit you. "
                   "The spreadsheet attached to the email has every link, ready to paste.")
    p.add_argument("--out", required=True); p.add_argument("--pdf", required=True)
    a = p.parse_args()
    rows = list(csv.DictReader(open(a.csv, newline="")))
    out_dir = os.path.dirname(os.path.abspath(a.out))
    brand_rel = os.path.relpath(os.path.abspath(a.brand), out_dir)
    page = build(rows, a, brand_rel)
    open(a.out, "w").write(page)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={os.path.abspath(a.pdf)}", "file://" + os.path.abspath(a.out)],
                   check=True, capture_output=True)
    fails = []
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", a.pdf], capture_output=True, text=True).stdout).group(1))
    if pages != 1: fails.append(f"{pages} pages")
    text = subprocess.run(["pdftotext", a.pdf, "-"], capture_output=True, text=True).stdout
    if re.search("[–—]", text): fails.append("em/en dash in text")
    raw = open(a.pdf, "rb").read().decode("latin-1")
    missing = [r["url"] for r in rows if r["url"].replace("&", "&") not in raw]
    if missing: fails.append(f"{len(missing)} URLs not linked: {missing[:3]}")
    print(f"{a.pdf}: {pages} page, {len(rows)} posts" + ("" if not fails else "\nFAIL: " + "; ".join(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
