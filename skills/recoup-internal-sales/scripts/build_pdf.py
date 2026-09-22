#!/usr/bin/env python3
"""Render a house-style HTML page to PDF and check it before it goes to a customer.

Usage:
  python3 scripts/build_pdf.py page.html Out.pdf [--font GeistPixel-Square.ttf]
                               [--max-pages 1] [--preview preview.png]

- Fills __PIXEL_FONT__ (display font, base64) and __RECOUP_ICON__ (the icon shipped in
  templates/pdf-house-style/). Without --font the page falls back to Geist Mono.
- Inlines every <img src="embed:PATH_OR_URL"> as a base64 data URI, so the PDF survives
  being forwarded with no network access.
- Renders with Chrome headless (set CHROME=/path/to/chrome if it is not found).
- Fails (exit 1) on: more pages than --max-pages, any em/en dash in the text, or fewer
  PDF link annotations than <a href> tags in the page.
Scripts ship alongside the skill; run from the skill directory or pass absolute paths.
"""
import argparse, base64, mimetypes, os, re, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

try:
    import pypdf
except ImportError:
    sys.exit("needs pypdf: pip3 install pypdf")

SKILL = Path(__file__).resolve().parent.parent
ICON = SKILL / "templates" / "pdf-house-style" / "recoup-icon-black.png"
CHROMES = [os.environ.get("CHROME", ""),
           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def fetch(src: str, base: Path) -> tuple[bytes, str]:
    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read(), r.headers.get_content_type()
    p = Path(src) if Path(src).is_absolute() else base / src
    return p.read_bytes(), mimetypes.guess_type(p.name)[0] or "image/png"


def chrome() -> str:
    for c in CHROMES:
        if c and (Path(c).exists() or shutil.which(c)):
            return c
    sys.exit("Chrome not found: set CHROME=/path/to/chrome")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("pdf")
    ap.add_argument("--font", help="path to GeistPixel-Square.ttf (the display font)")
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--preview", help="also write a PNG screenshot of page 1")
    a = ap.parse_args()

    src = Path(a.html).resolve()
    html = re.sub(r"<!--.*?-->", "", src.read_text(), flags=re.S)  # guidance comments never ship
    font = ""
    if a.font:
        font = ('@font-face{font-family:"GeistPixel";src:url(data:font/ttf;base64,%s) format("truetype");}'
                % b64(Path(a.font).read_bytes()))
    html = html.replace("__PIXEL_FONT__", font).replace("__RECOUP_ICON__", b64(ICON.read_bytes()))

    def embed(m):
        data, mime = fetch(m.group(2), src.parent)
        return f'{m.group(1)}data:{mime};base64,{b64(data)}"'
    html = re.sub(r'(<img[^>]*?src=")embed:([^"]+)"', embed, html)

    if re.search("[—–]|&mdash;|&ndash;", re.sub(r"<!--.*?-->", "", html, flags=re.S)):
        print("FAIL: em/en dash in the page source")

    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=src.parent, delete=False) as t:
        t.write(html); built = Path(t.name)
    try:
        c = chrome()
        common = [c, "--headless", "--disable-gpu", "--virtual-time-budget=10000"]
        subprocess.run(common + ["--no-pdf-header-footer", f"--print-to-pdf={Path(a.pdf).resolve()}",
                                 built.as_uri()], check=True, capture_output=True)
        if a.preview:
            subprocess.run(common + ["--hide-scrollbars", "--window-size=816,1056",
                                     f"--screenshot={Path(a.preview).resolve()}", built.as_uri()],
                           check=True, capture_output=True)
    finally:
        built.unlink(missing_ok=True)

    r = pypdf.PdfReader(a.pdf)
    text = "".join(p.extract_text() for p in r.pages)
    links = sum(1 for p in r.pages for x in (p.get("/Annots") or [])
                if x.get_object().get("/Subtype") == "/Link")
    hrefs = len(re.findall(r"<a\s[^>]*href=", html))
    dashes = len(re.findall("[—–]", text))
    ok = len(r.pages) <= a.max_pages and dashes == 0 and links >= hrefs
    print(f"pages {len(r.pages)} (max {a.max_pages}) · dashes {dashes} · links {links}/{hrefs} · "
          + ("OK" if ok else "FAIL"))
    print("Now open the preview and look at it: the checks do not catch clipped labels or overlaps.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
