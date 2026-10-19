"""Podcast clips sheet: the one-page Letter PDF attached to the release-day live-links email.

A card per clip (cover still, day, hook, a "Watch clip" link to its file in the Drive folder), a full-episode card
(YouTube, Spotify, the folder, the tag line) and a "Share any of them" note. Same look as the guest brief, the
timeline PDF and the wrap-up recap (Recoup Sky brand kit).

  python3 podcast_clips_sheet.py clips.json --brand <path>/recoup-sky --out clips.html --pdf recoup-podcast-clips-<slug>.pdf

clips.json  guest, role, company, role_url, slug, campaign, episode_title, youtube, spotify, folder, tags,
            clips[] of {date (YYYY-MM-DD), hook, url, still (path relative to clips.json)},
            badge (optional {clip: <1-based index>, text: "Live today" or "Your pick: ..."}).
            Example: templates/podcast-clips-sheet/clips.example.json
Checks (exit 1): one page, no em/en dashes in the text, every clip has a link and an existing still."""
import argparse, datetime, html, json, os, re, subprocess, sys

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")  # headless Chrome or Chromium
e = html.escape

CSS = """
  @page { size: Letter; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: var(--recoup-white); }
  body { width: 8.5in; height: 11in; overflow: hidden; font-family: var(--brand-body-font), sans-serif;
         color: var(--recoup-ink); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  a { color: var(--recoup-link); text-decoration: none; }
  .page { padding: 0.5in 0.55in 0.42in; height: 100%; display: flex; flex-direction: column; }
  .page > * { flex-shrink: 0; }
  header { display: flex; justify-content: space-between; align-items: center; }
  header img { width: 118px; height: auto; display: block; }
  .kicker { font-size: 9.5px; color: var(--recoup-muted); }
  .hero { margin-top: 0.22in; }
  .hero .label { font-size: 10px; color: var(--recoup-sky); }
  h1 { font-family: var(--brand-display-font), sans-serif; font-weight: 500; font-size: 30px; line-height: 1.08;
       letter-spacing: -0.02em; margin-top: 7px; }
  .guest { font-size: 13px; color: var(--recoup-muted); margin-top: 7px; }
  .guest strong { color: var(--recoup-ink); font-weight: 500; }
  .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 0.2in; }
  .clip { display: flex; flex-direction: column; border-radius: 10px; box-shadow: 0 0 0 1px var(--recoup-border);
          overflow: hidden; color: var(--recoup-ink); background: var(--recoup-white); }
  .clip img { width: 100%; aspect-ratio: 9 / 13; object-fit: cover; object-position: top; display: block; }
  .clip .meta { padding: 8px 10px 9px; display: flex; flex-direction: column; gap: 3px; flex: 1; }
  .day { font-size: 8.5px; color: var(--recoup-sky); }
  .clip b { font-weight: 500; font-size: 10.5px; line-height: 1.3; flex: 1; }
  .go { font-size: 9.5px; color: var(--recoup-link); margin-top: 2px; }
  .badge { align-self: flex-start; font-size: 8px; background: var(--recoup-lime); color: var(--recoup-forest);
           padding: 2px 6px; border-radius: 999px; }
  .ep { border-radius: 10px; background: var(--recoup-pale); padding: 12px; display: flex; flex-direction: column; gap: 6px; }
  .ep .recoup-label { font-size: 8.5px; color: var(--recoup-sky); }
  .ep b { font-weight: 500; font-size: 12px; line-height: 1.3; }
  .ep a { font-size: 10.5px; padding: 6px 10px; border-radius: 999px; background: var(--recoup-white);
          box-shadow: 0 0 0 1px var(--recoup-border); color: var(--recoup-ink); }
  .ep a.all { background: var(--recoup-forest); color: var(--recoup-lime); box-shadow: none; }
  .ep p { font-size: 9.5px; line-height: 1.45; color: var(--recoup-muted); margin-top: auto; }
  .note { margin-top: auto; border-radius: 10px; background: var(--recoup-forest); color: #C9D6D2; padding: 12px 16px;
          font-size: 11.5px; line-height: 1.5; }
  .note b { color: var(--recoup-white); font-weight: 500; }
  footer { display: flex; justify-content: space-between; margin-top: 0.12in; font-size: 9px; color: var(--recoup-muted); }
"""

WORDS = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]


def build(s, brand_rel, still_rel):
    day = lambda d: datetime.date.fromisoformat(d)
    clips, badge = s["clips"], s.get("badge") or {}
    first, last = day(clips[0]["date"]), day(clips[-1]["date"])
    span = (f"{first:%b %-d} to {last:%-d}" if first.month == last.month else f"{first:%b %-d} to {last:%b %-d}")
    cards = ""
    for i, c in enumerate(clips, 1):
        b = f'<span class="badge">{e(badge["text"])}</span>' if badge.get("clip") == i else ""
        cards += (f'<a class="clip" href="{e(c["url"])}"><img src="{e(still_rel(c["still"]))}" alt="">'
                  f'<div class="meta"><span class="day recoup-label">{day(c["date"]):%a · %b %-d}</span>{b}'
                  f'<b>{e(c["hook"])}</b><span class="go">Watch clip ↗</span></div></a>')
    role = e(s["role"])
    if s.get("role_url") and s.get("company"):
        role = role.replace(e(s["company"]), f'<a href="{e(s["role_url"])}">{e(s["company"])}</a>')
    n = len(clips)
    utm = f"utm_source=pdf&amp;utm_medium=guest-clips&amp;utm_campaign={e(s['campaign'])}&amp;utm_content={e(s['slug'])}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Recoup Podcast clips: {e(s['guest'])}</title>
<link rel="stylesheet" href="{e(brand_rel)}/brand.css">
<style>{CSS}</style></head><body><div class="page">
  <header><img src="{e(brand_rel)}/logos/lockup-ink.svg" alt="Recoup"><span class="kicker recoup-label">Recoup Podcast · Your clips this week</span></header>
  <section class="hero"><span class="label recoup-label">One clip a day, {span}</span>
    <h1>{WORDS[n] if n < len(WORDS) else n} clips from your episode</h1>
    <p class="guest">With <strong>{e(s['guest'])}</strong>, {role}</p></section>
  <div class="grid">{cards}
    <div class="ep"><span class="recoup-label">The full episode</span><b>{e(s['episode_title'])}</b>
      <a href="{e(s['youtube'])}">YouTube ↗</a><a href="{e(s['spotify'])}">Spotify ↗</a>
      <a class="all" href="{e(s['folder'])}">All {n} clips (Drive) ↗</a>
      <p>Each clip posts on its day, {e(s['tags'])}.</p></div>
  </div>
  <div class="note"><b>Share any of them.</b> Reshare our posts or post the files from your own accounts. Every clip is in the Drive folder, vertical and captioned.</div>
  <footer><span>Questions: reply to Patrick Sweetman, Cofounder, Recoup</span><a href="https://recoupable.dev/podcast/{e(s['slug'])}?{utm}">recoupable.dev/podcast</a></footer>
</div></body></html>
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("clips")
    p.add_argument("--brand", required=True, help="path to the recoup-sky brand kit folder")
    p.add_argument("--out", required=True); p.add_argument("--pdf", required=True)
    a = p.parse_args()
    s = json.load(open(a.clips))
    out_dir, src_dir = os.path.dirname(os.path.abspath(a.out)), os.path.dirname(os.path.abspath(a.clips))
    fails = [f"clip {i}: missing still {c.get('still')}" for i, c in enumerate(s["clips"], 1)
             if not os.path.isfile(os.path.join(src_dir, c.get("still", "")))]
    fails += [f"clip {i}: no link" for i, c in enumerate(s["clips"], 1) if not c.get("url", "").startswith("http")]
    if fails: sys.exit("FAIL: " + "; ".join(fails))
    brand_rel = os.path.relpath(os.path.abspath(a.brand), out_dir)
    still_rel = lambda f: os.path.relpath(os.path.join(src_dir, f), out_dir)
    open(a.out, "w").write(build(s, brand_rel, still_rel))
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={os.path.abspath(a.pdf)}", "file://" + os.path.abspath(a.out)],
                   check=True, capture_output=True)
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", a.pdf], capture_output=True, text=True).stdout).group(1))
    if pages != 1: fails.append(f"{pages} pages")
    text = subprocess.run(["pdftotext", a.pdf, "-"], capture_output=True, text=True).stdout
    if re.search("[–—]", text): fails.append("em/en dash in text")
    print(f"{a.pdf}: {pages} page, {len(s['clips'])} clips" + ("" if not fails else "\nFAIL: " + "; ".join(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
