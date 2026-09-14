#!/usr/bin/env python3
"""Render filled proposal HTML to PDF; validate slots before starting a renderer."""
import argparse
import datetime
import os
from pathlib import Path
import re


def out_path(html, given=None):
    return str(given or Path(html).with_name(f"{Path(html).stem}-{datetime.date.today()}.pdf"))


def validate_html(html):
    path = Path(html).resolve(strict=True)
    slots = sorted(set(re.findall(r"\{\{[^{}]+\}\}", path.read_text())))
    if slots:
        raise ValueError("Unfilled proposal fields: " + ", ".join(slots))
    return path


def render_chromium(html, pdf):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        launch = {}
        if os.environ.get("CHROMIUM_PATH"):
            launch["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = p.chromium.launch(**launch)
        try:
            page = browser.new_page()
            page.goto(Path(html).resolve().as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(pdf), format="A4", print_background=True, prefer_css_page_size=True)
        finally:
            browser.close()


def render_weasyprint(html, pdf):
    from weasyprint import HTML
    HTML(filename=str(html)).write_pdf(str(pdf))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--engine", choices=["auto", "chromium", "weasyprint"], default="auto")
    parser.add_argument("--check", action="store_true", help="validate fields without rendering")
    args = parser.parse_args(argv)
    try:
        html = validate_html(args.html)
        if args.check:
            print("All proposal fields are resolved.")
            return 0
        pdf = Path(out_path(html, args.output)).resolve()
        if pdf == html:
            raise ValueError("Output must differ from the source HTML.")
        pdf.parent.mkdir(parents=True, exist_ok=True)
        engines = ["chromium", "weasyprint"] if args.engine == "auto" else [args.engine]
        failures = []
        for engine in engines:
            try:
                {"chromium": render_chromium, "weasyprint": render_weasyprint}[engine](html, pdf)
                print(f"[{engine}] wrote {pdf}; inspect page count and layout before delivery")
                return 0
            except Exception as exc:
                failures.append(f"{engine}: {type(exc).__name__}")
        raise RuntimeError("Renderers unavailable or failed (" + "; ".join(failures) + "). "
                           "Prepare Playwright + Chromium or WeasyPrint in a project Python environment.")
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
