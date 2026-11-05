#!/usr/bin/env python3
"""Checks for render.py output and theme files.

usage: check_render.py [--theme NAME|PATH ...] [page.html ...]

- every page: balanced tags, the JSON data block parses, the inline script passes `node --check`
  (needs node on PATH; without it that one check is skipped);
- every theme: defines each var(--x) the shared CSS uses, and small-text colour pairs reach 4.5:1
  on the surfaces they sit on (light and dark token sets);
- render.py itself: no theme names from themes/*.json, so the layout stays theme-neutral.
Exits 1 on any failure.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
BRAND_WORDS = ["recoup"]  # plus every theme name found in themes/

# (text token, surface, what uses it). Surfaces are composed in surfaces().
PAIRS = [
    ("--text", "page", "body text"), ("--muted", "page", "subheads, labels"), ("--faint", "page", "fact labels, axes, captions"),
    ("--muted", "item", "labels in cards"), ("--faint", "item", "cut and use labels in cards"),
    ("--faint", "panel", "chart axes and captions"), ("--muted", "panel", "chart labels"),
    ("--link", "page", "links"), ("--chip-text", "chip", "play pills"), ("--muted", "chip", "cut label in pills"),
    ("--ok", "ok-pill", "Clear / In pills"), ("--risk", "risk-pill", "Out pills"), ("--warn", "warn-pill", "Heavy pills"),
    ("--neutral", "neutral-pill", "Light pills"), ("--risk", "page", "No / risk text"), ("--ok", "page", "Yes text"),
    ("--warn", "panel", "breakdown label"), ("--sc-muted", "score", "score labels"), ("--sc-text", "score", "score text"),
    ("--hi-ink", "hi", "best-moment badge"), ("--accent-text", "page", "accent text"),
    ("--muted", "player", "player time"), ("--accent-ink", "accent", "play button icon"),
    ("--risk", "player", "player error message"),
]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.scripts, self.cur = [], [], [], None

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        self.stack.append((tag, self.getpos()))
        if tag == "script":
            self.cur = (dict(attrs).get("type"), [])

    def handle_data(self, data):
        if self.cur is not None:
            self.cur[1].append(data)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append(f"</{tag}> at {self.getpos()} closes {self.stack[-1] if self.stack else 'nothing'}")
            return
        self.stack.pop()
        if tag == "script":
            self.scripts.append((self.cur[0], "".join(self.cur[1])))
            self.cur = None


def check_page(path):
    fails = []
    p = Tags()
    with open(path, encoding="utf-8") as f:
        p.feed(f.read())
    p.close()
    fails += p.errors + [f"unclosed <{t}> from {pos}" for t, pos in p.stack]
    for typ, code in p.scripts:
        if typ == "application/json":
            try:
                json.loads(code)
            except ValueError as err:
                fails.append(f"data block: {err}")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tmp:
            tmp.write(code)
        try:
            res = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
        except FileNotFoundError:
            os.unlink(tmp.name)
            continue
        os.unlink(tmp.name)
        if res.returncode:
            fails.append("node --check: " + res.stderr.strip()[:400])
    return fails


# ---- colour maths -----------------------------------------------------------

def parse_color(v):
    v = v.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", v)
    if m:
        h = m.group(1)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    m = re.fullmatch(r"rgba?\(([^)]+)\)", v)
    if m:
        parts = [x.strip() for x in m.group(1).split(",")]
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return (float(parts[0]), float(parts[1]), float(parts[2]), a)
    return None


def resolve(tokens, name, depth=0):
    v = tokens.get(name)
    if v is None or depth > 8:
        return None
    m = re.fullmatch(r"var\((--[\w-]+)\)", v.strip())
    return resolve(tokens, m.group(1), depth + 1) if m else v


def first_color(v):
    """A plain colour, or the first stop of a gradient."""
    c = parse_color(v)
    if c:
        return c
    m = re.search(r"(#[0-9a-fA-F]{6}|rgba?\([^)]+\))", v or "")
    return parse_color(m.group(1)) if m else None


def over(top, base):
    a = top[3]
    return tuple(top[i] * a + base[i] * (1 - a) for i in range(3)) + (1.0,)


def lum(c):
    def ch(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def surfaces(tok, card_token):
    col = lambda n: first_color(resolve(tok, n) or "")  # noqa: E731
    page = col("--bg")
    card = over(col(card_token), page) if card_token and col(card_token) else page
    item = over(col("--item"), card)
    s = {"page": card, "panel": over(col("--panel"), card), "item": item, "chip": over(col("--chip-bg"), item),
         "score": over(col("--sc-bg"), page), "hi": col("--hi"), "accent": col("--accent-text"),
         "player": over(col("--player-bg"), page)}
    for k in ("ok", "risk", "warn", "neutral"):
        s[f"{k}-pill"] = over(col(f"--{k}-soft"), item)
    return s


def check_theme(value, css_vars):
    fails, notes = [], []
    theme = render.load_theme(value)
    sets = [("light" if theme.get("dark_tokens") else "default", theme["tokens"], theme["accents"])]
    if theme.get("dark_tokens"):
        dark = dict(theme["tokens"], **theme["dark_tokens"])
        sets.append(("dark", dark, theme.get("dark_accents") or theme["accents"]))
    defined = set(theme["tokens"]) | {"--sa", "--sa-soft", "--cols", "--fc"}
    missing = sorted(v for v in css_vars if v not in defined and not v.startswith("--acc-"))
    if missing:
        fails.append(f"{theme['name']}: tokens used by the shared CSS but not defined: {', '.join(missing)}")
    card_token = "--card-grad" if "--card-grad" in theme["tokens"] and ".sec" in (theme.get("css") or "") else None
    worst = 99
    for label, tok, accents in sets:
        s = surfaces(tok, card_token)
        rows = [(n, surf, why) for n, surf, why in PAIRS]
        for i, a in enumerate(accents, 1):
            tok = dict(tok, **{f"--acc-{i}": a["color"]})
            rows += [(f"--acc-{i}", "page", f"section accent {a.get('name', i)}"), (f"--acc-{i}", "item", f"accent {a.get('name', i)} in cards")]
        for n, surf, why in rows:
            fg, bg = first_color(resolve(tok, n) or ""), s.get(surf)
            if not fg or not bg:
                fails.append(f"{theme['name']} {label}: cannot resolve {n} on {surf}")
                continue
            r = ratio(over(fg, bg), bg)
            worst = min(worst, r)
            if r < 4.5:
                fails.append(f"{theme['name']} {label}: {n} on {surf} is {r:.2f}:1 ({why})")
    notes.append(f"{theme['name']}: {len(sets)} token set(s), lowest small-text contrast {worst:.2f}:1")
    return fails, notes


def check_renderer():
    with open(os.path.join(HERE, "render.py"), encoding="utf-8") as f:
        src = f.read().lower()
    words = BRAND_WORDS + [n.lower() for n in render.available_themes()]
    return [f"render.py mentions '{w}'" for w in words if w in src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--theme", action="append", default=[])
    a = ap.parse_args()
    css_vars = set(re.findall(r"var\((--[\w-]+)", render.BASE_CSS))
    fails = check_renderer()
    for t in a.theme or render.available_themes():
        f, notes = check_theme(t, css_vars)
        fails += f
        for n in notes:
            print(n)
    for p in a.pages:
        f = check_page(p)
        print(f"{os.path.basename(p)}: {'ok' if not f else str(len(f)) + ' problem(s)'}")
        fails += [f"{os.path.basename(p)}: {x}" for x in f]
    for x in fails:
        print("FAIL", x)
    print("all checks passed" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
