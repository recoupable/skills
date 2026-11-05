#!/usr/bin/env python3
"""Render one song analyst report to a single self-contained HTML page.

usage: render.py <report.json> <measurement.json> <out.html> --theme NAME|PATH
                 [--extra extra.json] [--audio URL] [--date YYYY-MM-DD]

report.json follows the skill's references/schema.json; measurement.json is the measure step's output.
Stdlib only. CSS and JS are inline; the only external requests are the theme's font stylesheets.
Charts are inline SVG drawn by the inline script from the measurement embedded as JSON.

--theme: a bare NAME loads themes/NAME.json beside this script; a value ending in .json or
containing a path separator is read as a path. The theme carries every colour token, the font
links, radii, the per-section accent rotation and any decoration; this file is layout and charts.

--extra: a JSON array of {"title", "nav"?, "html"} inserted after Growth and before Notes. "nav" is
the section's one name (nav, index, eyebrow, prev/next); without it the first two words of the
title are used. The HTML is kept as written, except that m:ss in its text become play pills (one
per sentence, none in headings), straight quotes become typographic, and a <code> ID is kept only
when it is labelled (text ending in "ID" before it, or a data-label/title attribute).

--audio: embeds <audio data-report-player> in a sticky mini player that every play pill and chart
marker seeks. Pills also dispatch a bubbling `report:seek` CustomEvent ({detail: {t}}) and post
{type: "report:seek", t} to a parent frame, so a host page can drive its own player.
"""

import argparse
import datetime as dt
import html
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUBSCORES = [
    ("hook", "Hook", 20),
    ("production", "Production", 20),
    ("songwriting", "Songwriting", 15),
    ("structure", "Structure", 10),
    ("vocal", "Vocal", 10),
    ("sync_utility", "Sync utility", 15),
    ("market", "Market", 10),
]

BAND_ORDER = ["sub", "low", "low_mid", "mid", "high_mid", "high", "air"]

# (id, label). The label is the section's one name: nav, index, section eyebrow and prev/next.
# Ids match verdict.review[].deep_dive.
CORE = [
    ("verdict", "Verdict"),
    ("first-listen", "First Listen"),
    ("sonic-identity", "Sonic Identity"),
    ("production", "Production"),
    ("songwriting", "Songwriting"),
    ("structure", "Structure"),
    ("market", "Market"),
    ("comparables", "Comparables"),
    ("sync", "Sync"),
    ("growth", "Growth"),
]

# (report.dimensions key, card title, section id)
DIMENSIONS = [
    ("sonic_identity", "Sonic Identity", "sonic-identity"),
    ("production_craft", "Production Craft", "production"),
    ("songwriting", "Songwriting", "songwriting"),
    ("structure_dynamics", "Structure & Dynamics", "structure"),
    ("creative_dna", "Creative DNA", "structure"),
    ("market_position", "Market Position", "market"),
    ("comparables", "Comparables", "comparables"),
    ("sync_placement", "Sync Placement", "sync"),
    ("growth", "Growth", "growth"),
]

FINGERPRINT = [
    ("organic_electronic", "Organic", "Electronic"),
    ("sparse_dense", "Sparse", "Dense"),
    ("dark_bright", "Dark", "Bright"),
    ("intimate_anthemic", "Intimate", "Anthemic"),
    ("smooth_textured", "Smooth", "Textured"),
    ("slow_fast", "Slow", "Fast"),
]

HUMAN_KEYS = {k: f"{lo.lower()}\u2013{hi.lower()}" for k, lo, hi in FINGERPRINT}
HUMAN_KEYS.update({"low_mid": "low-mid", "high_mid": "high-mid"})
HUMAN_RE = re.compile(r"\b(" + "|".join(HUMAN_KEYS) + r")\b")

BULLET = {
    "strength": ("\u2713", "b-ok", "Strength"),
    "neutral": ("\u2014", "b-neu", "Neutral"),
    "risk": ("\u26a0\ufe0e", "b-risk", "Risk"),
}

REQUIRED = ["identity", "verdict", "first_impression", "dimensions", "sonic_identity",
            "production_craft", "songwriting", "structure", "market", "sync", "growth",
            "score", "technical"]

# A time or a range, with an optional cut label before it (":15 0:44-0:59") and any
# bracket or punctuation that must stay on the same line as the pill.
PILL_RE = re.compile(
    r"(?P<pre>[(\[\u201c\u2018]?)"
    r"(?:(?P<cut>:(?:06|15|30|60))\s+)?"
    r"(?<![\d:.])(?P<m>\d{1,2}):(?P<s>[0-5]\d)(?!\d)(?!:\d)"
    r"(?:\s*[\u2013\u2014-]\s*(?P<m2>\d{1,2}):(?P<s2>[0-5]\d)(?!\d)(?!:\d))?"
    r"(?P<post>[)\]\u201d\u2019.,;:!?]*)"
)
TS_RE = re.compile(r"(?<![\d:])(\d{1,2}):([0-5]\d)(?!\d)(?!:\d)")
TAG_RE = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)
SKIP_TAGS = {"script", "style", "code", "pre", "button", "a", "textarea", "svg", "title"}

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def esc(v):
    return html.escape("" if v is None else str(v), quote=True)


def smart(s):
    """Straight quotes to typographic quotes."""
    s = re.sub(r'(^|[\s(\[{\u2014\u2013/-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(^|[\s(\[{\u2014\u2013/-])'", "\\1\u2018", s)
    return s.replace("'", "\u2019")


def humanize(s):
    return HUMAN_RE.sub(lambda mo: HUMAN_KEYS[mo.group(1)], s)


def pill(m, s, m2=None, s2=None, cut=None):
    t = m * 60 + s
    rng = f"{m}:{s:02d}" if m2 is None else f"{m}:{s:02d}\u2013{m2}:{s2:02d}"
    label = f"Play from {m}:{s:02d}" if m2 is None else f"Play {m}:{s:02d} to {m2}:{s2:02d}"
    if cut:
        label = f"{cut} cut, " + label[0].lower() + label[1:]
    k = f'<span class="t-k">{cut}</span>' if cut else ""
    return (f'<button type="button" class="t" data-t="{t}" aria-label="{label}">'
            f'<span class="t-g" aria-hidden="true">\u25b7\ufe0e</span>{k}{rng}</button>')


def plain_time(m, s, m2=None, s2=None, cut=None):
    """A time set in mono with no play control."""
    rng = f"{m}:{s:02d}" if m2 is None else f"{m}:{s:02d}–{m2}:{s2:02d}"
    return f'<span class="tm">{cut + " " if cut else ""}{rng}</span>'


SENT_END = re.compile(r"[.!?][”’)\]]*(?:\s|$)")
SENT_SPLIT = re.compile(r"[.!?][”’)\]]*\s+(?=[A-Z“‘(])")


def pillify(text, escape=True, pills=True):
    """m:ss (or an m:ss-m:ss range) becomes a play pill: only the first time in each sentence.
    Later times in the same sentence, and every time when pills=False, are plain mono text."""
    e = esc if escape else (lambda x: x)
    out, pos, used = [], 0, False
    for mo in PILL_RE.finditer(text):
        g = mo.group
        if SENT_END.search(text[pos:mo.start()]):
            used = False
        args = (int(g("m")), int(g("s")), int(g("m2")) if g("m2") else None,
                int(g("s2")) if g("s2") else None, g("cut"))
        if pills and not used:
            p, used = pill(*args), True
        else:
            p = plain_time(*args)
        out.append(e(text[pos:mo.start()]))
        if g("pre") or g("post"):
            p = f'<span class="nw">{e(g("pre"))}{p}{e(g("post"))}</span>'
        out.append(p)
        if re.search(r"[.!?]", g("post") or ""):
            used = False
        pos = mo.end()
    out.append(e(text[pos:]))
    return "".join(out)


def rich(v, pills=True):
    """Inline prose: escape, typographic quotes, readable keys, play pills (one per sentence)."""
    if v is None:
        return ""
    return pillify(humanize(smart(re.sub(r"\s*\n\s*", " ", str(v)).strip())), pills=pills)


def split_long(p, limit=120):
    """A paragraph over `limit` words splits at the sentence end nearest its middle."""
    words = p.split()
    if len(words) <= limit:
        return [p]
    ends = [mo.end() for mo in SENT_SPLIT.finditer(p)]
    if not ends:
        return [p]
    half = len(words) / 2
    cut = min(ends, key=lambda i: abs(len(p[:i].split()) - half))
    a, b = p[:cut].strip(), p[cut:].strip()
    if not a or not b:
        return [p]
    return split_long(a, limit) + split_long(b, limit)


def paras(v, cls=None, pills=True):
    """Block prose: a string (blank lines split paragraphs; over 120 words splits at a sentence
    end) or a list of strings."""
    if not v:
        return ""
    items = v if isinstance(v, list) else [v]
    parts = []
    for it in items:
        for p in re.split(r"\n\s*\n", str(it)):
            if p.strip():
                parts += split_long(re.sub(r"\s*\n\s*", " ", p.strip()))
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{rich(p, pills)}</p>" for p in parts)


SPEC_HEAD = re.compile(r"^([A-Z][A-Za-z&/+\- ]{0,22}?):\s+(\S.*)$", re.S)


def spec_or_paras(v):
    """'Kick: ... Bass: ... Snare: ...' run-ons become a two-column list; anything else is prose."""
    if not isinstance(v, str) or "\n\n" in v:
        return paras(v)
    sentences = re.split(r"(?<=[.!?])\s+", v.strip())
    intro, items = [], []
    for sentence in sentences:
        mo = SPEC_HEAD.match(sentence)
        if mo:
            items.append([mo.group(1), [mo.group(2)]])
        elif items:
            items[-1][1].append(sentence)
        else:
            intro.append(sentence)
    if len(items) < 3:
        return paras(v)
    outro = items[-1][1][1:]
    items[-1][1] = items[-1][1][:1]
    rows = "".join(f'<div><dt>{esc(k)}</dt><dd>{rich(" ".join(t))}</dd></div>' for k, t in items)
    return (paras(" ".join(intro)) + f'<dl class="spec">{rows}</dl>'
            + (f'<p class="spec-out">{rich(" ".join(outro))}</p>' if outro else ""))


CODE_RE = re.compile(r"(\s*)<code\b([^>]*)>(.*?)</code>", re.S | re.I)


def labelled_codes(h):
    """Keep a <code> ID only when it carries a label: a data-label/title/aria-label attribute, or
    text ending in 'ID' right before it (e.g. 'Track ID <code>123</code>'). Unlabelled IDs go."""
    def fix(mo):
        before = re.sub(r"<[^>]+>", " ", h[max(0, mo.start() - 60):mo.start()])
        if re.search(r"\b(data-label|title|aria-label)\s*=", mo.group(2), re.I) or re.search(r"\bID\s*:?\s*$", before):
            return mo.group(0)
        return ""
    return CODE_RE.sub(fix, h or "")


def enrich_html(h):
    """Pills and typographic quotes in the text of trusted extra-section HTML; tags untouched.
    Headings inside it get plain times, not pills."""
    out, skip, heading = [], [], 0
    for part in TAG_RE.split(labelled_codes(h)):
        if not part:
            continue
        if part.startswith("<"):
            mo = re.match(r"<\s*(/)?\s*([A-Za-z][A-Za-z0-9-]*)", part)
            name = mo.group(2).lower() if mo else ""
            if name in SKIP_TAGS:
                if mo.group(1):
                    if skip and skip[-1] == name:
                        skip.pop()
                elif not part.rstrip().endswith("/>"):
                    skip.append(name)
            elif name in ("h1", "h2", "h3"):
                heading = max(0, heading + (-1 if mo.group(1) else 1))
            out.append(part)
        elif skip:
            out.append(part)
        else:
            t = part.replace("&quot;", '"').replace("&#39;", "'").replace("&#x27;", "'")
            out.append(pillify(humanize(smart(t)), escape=False, pills=heading == 0))
    return "".join(out)


def num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def to_seconds(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    mo = TS_RE.search(str(v))
    return float(int(mo.group(1)) * 60 + int(mo.group(2))) if mo else None


def mmss(sec):
    sec = max(0, int(math.floor((sec or 0) + 1e-6)))
    return f"{sec // 60}:{sec % 60:02d}"


def fmt_num(v):
    f = num(v)
    if f is None:
        return ""
    return str(int(round(f))) if abs(f - round(f)) < 0.05 else f"{f:.1f}"


def signed(v, plus=False):
    f = num(v)
    if f is None:
        return "\u2014"
    s = f"{abs(f):.1f}"
    if f < 0 and s != "0.0":
        return "\u2212" + s
    return ("+" + s) if plus and f > 0 else s


def unit(v):
    """Normalise a valence/arousal reading to 0..1 (accepts 0..1, -1..1 or 0..100)."""
    f = num(v)
    if f is None:
        return None
    if f < 0:
        f = (f + 1) / 2
    elif f > 1:
        f = f / 100
    return max(0.0, min(1.0, f))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "section"


def safe_url(u):
    u = str(u or "").strip()
    return u if re.match(r"^https?://", u, re.I) else None


def media_url(u):
    u = str(u or "").strip()
    if not u or re.match(r"^\s*(javascript|data|vbscript):", u, re.I):
        return None
    return u


def json_for_script(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026") \
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def grid_cols(n):
    return n if n <= 4 else 3 if n in (5, 6, 9) else 4


# ---------------------------------------------------------------------------
# Small components
# ---------------------------------------------------------------------------


def bullets(items, cls="bul"):
    out = []
    for b in items or []:
        icon, kcls, label = BULLET.get(str(b.get("kind", "neutral")), BULLET["neutral"])
        out.append(f'<li class="{kcls}"><span class="b-i" aria-hidden="true">{icon}</span>'
                   f'<span><span class="sr">{label}: </span>{rich(b.get("text"))}</span></li>')
    return f'<ul class="{cls}">{"".join(out)}</ul>' if out else ""


def block(kicker, inner, cls=""):
    if not inner:
        return ""
    c = f"blk {cls}".strip()
    return f'<div class="{c}"><h3 class="mk">{esc(kicker)}</h3>{inner}</div>'


def facts(items, cls="facts"):
    cells = []
    for label, value, vcls in items:
        if value in (None, ""):
            continue
        c = f' class="{vcls}"' if vcls else ""
        cells.append(f'<div class="fact"><dt>{esc(label)}</dt><dd{c}>{esc(value)}</dd></div>')
    if not cells:
        return ""
    cols = len(cells) if len(cells) <= 6 else math.ceil(len(cells) / 2)
    return f'<dl class="{cls}" style="--fc:{cols}">{"".join(cells)}</dl>'


def issues(items, kicker="Issues"):
    cards = []
    for it in items or []:
        t = rich(it.get("time")) if it.get("time") else ""
        cards.append(
            f'<article class="item issue"><div class="issue-h"><h4 class="h4">{rich(it.get("title"))}</h4>{t}</div>'
            f'{paras(it.get("problem"))}'
            f'<div class="fix"><span class="fix-k">Fix</span>{paras(it.get("fix"))}</div></article>')
    return block(kicker, f'<div class="gc" style="--cols:{min(3, grid_cols(len(cards)))}">{"".join(cards)}</div>') if cards else ""


def ticks(items):
    lis = "".join(f"<li>{rich(x)}</li>" for x in items or [] if x)
    return f'<ul class="ticks">{lis}</ul>' if lis else ""


def chips(items):
    lis = "".join(f"<li>{esc(smart(str(x)))}</li>" for x in items or [] if x)
    return f'<ul class="chips">{lis}</ul>' if lis else ""


def headed(items):
    out = []
    for it in items or []:
        out.append(f'<div class="hb"><h4 class="h4">{rich(it.get("heading"))}</h4>'
                   f'<div class="prose">{paras(it.get("paragraphs"))}</div></div>')
    return f'<div class="hbs">{"".join(out)}</div>' if out else ""


def disclosure(summary, inner, count=None, cls="", open_label=None, index_label=None):
    """A closed-by-default toggle. open_label replaces the summary text while it is open."""
    if not inner:
        return ""
    c = f'<span class="count">{count}</span>' if count is not None else ""
    klass = f"disc {cls}".strip()
    swap = (f' data-closed="{esc(summary)}" data-open="{esc(open_label)}"' if open_label else "")
    return (f'<details class="{klass}" data-index="{esc(index_label or summary)}"><summary><span class="disc-l"{swap}>{esc(summary)}</span>{c}</summary>'
            f'<div class="disc-body">{inner}</div></details>')


def cuts_row(cuts, cut15=None):
    """The :06 / :15 / :30 windows as range pills; tolerates the older single cut_15 string."""
    found = []
    if isinstance(cuts, dict):
        for k in ("6", "15", "30"):
            if cuts.get(k):
                found.append((f":{int(k):02d}", cuts[k]))
    elif cut15:
        found.append((":15", cut15))
    pills = []
    for label, rng in found:
        mo = PILL_RE.search(str(rng))
        if mo:
            g = mo.group
            pills.append(pill(int(g("m")), int(g("s")), int(g("m2")) if g("m2") else None,
                              int(g("s2")) if g("s2") else None, label))
        else:
            pills.append(f'<span class="tag">{esc(label)} {esc(rng)}</span>')
    return f'<div class="cuts"><span class="cuts-k">Cuts</span>{"".join(pills)}</div>' if pills else ""


def ext_link(label_html, url):
    u = safe_url(url)
    if not u:
        return label_html
    return (f'<a class="ext" href="{esc(u)}" target="_blank" rel="noopener noreferrer">{label_html}'
            f'<span class="ext-i" aria-hidden="true">\u2197</span></a>')


# ---------------------------------------------------------------------------
# Hero, nav, index, frame
# ---------------------------------------------------------------------------


def core_facts(r, m):
    idn = r.get("identity") or {}
    key = idn.get("key")
    if not key and isinstance(m.get("key"), dict):
        key = f'{m["key"].get("tonic", "")} {m["key"].get("mode", "")}'.strip()
    tempo = idn.get("tempo_bpm", m.get("tempo_bpm"))
    return [
        ("Key", key, None),
        ("Tempo", f"{fmt_num(tempo)} BPM" if num(tempo) is not None else "", None),
        ("Time sig.", idn.get("time_signature") or m.get("time_signature"), None),
        ("Genre", idn.get("genre"), None),
        ("Subgenre", idn.get("subgenre"), None),
        ("Mood", idn.get("primary_mood"), None),
    ]


def loudness(m):
    lufs = m.get("lufs") if num(m.get("lufs")) is not None else m.get("loudness_lufs")
    return num(lufs), num(m.get("true_peak_dbtp")), m.get("broadcast_ready")


def score_card(sc):
    total = int(round(num(sc.get("total")) or 0))
    frac = max(0.0, min(1.0, total / 100))
    circ = 2 * math.pi * 54
    ring = (f'<svg class="ring" viewBox="0 0 128 128" width="128" height="128" role="img" aria-label="Score {total} out of 100">'
            f'<circle class="ring-track" cx="64" cy="64" r="54"/>'
            f'<circle class="ring-val" cx="64" cy="64" r="54" stroke-dasharray="{circ * frac:.1f} {circ:.1f}" '
            f'transform="rotate(-90 64 64)"/>'
            f'<text class="ring-n" x="64" y="64" text-anchor="middle" dominant-baseline="middle">{total}</text>'
            f'<text class="ring-d" x="64" y="94" text-anchor="middle">/ 100</text></svg>')
    subs = sc.get("subscores") or {}
    rows = []
    for key, label, weight in SUBSCORES:
        v = num(subs.get(key))
        if v is None:
            continue
        pct = max(0.0, min(100.0, v * 10))
        rows.append(f'<li><span class="ss-l">{label}<span class="ss-w">{weight}%</span></span>'
                    f'<span class="ss-bar"><i style="width:{pct:.0f}%"></i></span>'
                    f'<span class="ss-v">{fmt_num(v)}</span></li>')
    lst = f'<ul class="ss" aria-label="Subscores out of 10, with rubric weights">{"".join(rows)}</ul>' if rows else ""
    return (f'<aside class="score" aria-label="Score"><p class="k">Score</p>'
            f'<div class="score-top">{ring}<p class="score-line">{rich(sc.get("one_line"))}</p></div>{lst}</aside>')


def hero(r, m, date_label):
    idn = r.get("identity") or {}
    v = r.get("verdict") or {}
    who = []
    if idn.get("artists"):
        who.append(f'<span class="who-a">{esc(idn["artists"])}</span>')
    if idn.get("writers"):
        who.append(f'<span><span class="who-k">Written by</span> {esc(idn["writers"])}</span>')
    if idn.get("producers"):
        who.append(f'<span><span class="who-k">Produced by</span> {esc(idn["producers"])}</span>')
    if idn.get("year"):
        who.append(f'<span>{esc(idn["year"])}</span>')
    if idn.get("explicit") is True:
        who.append('<span class="tag">Explicit</span>')
    lufs, tp, ready = loudness(m)
    dur = idn.get("duration_mmss") or (mmss(num(m.get("duration_seconds"))) if m.get("duration_seconds") else "")
    items = [("Duration", dur, None)] + core_facts(r, m) + [
        ("Loudness", f"{signed(lufs)} LUFS" if lufs is not None else "", None),
        ("True peak", f"{signed(tp, plus=True)} dBTP" if tp is not None else "", None),
        ("Broadcast-ready", ("Yes" if ready else "No") if isinstance(ready, bool) else "",
         ("yes" if ready else "no") if isinstance(ready, bool) else None),
    ]
    who_html = f'<p class="who">{"".join(who)}</p>' if who else ""
    sub = f'<p class="subhead">{rich(v.get("subhead"))}</p>' if v.get("subhead") else ""
    return (f'<header class="wrap hero">'
            f'<p class="eyebrow">Song analyst report \u00b7 {esc(date_label)}</p>'
            f'<h1 class="title">{esc(smart(str(idn.get("title") or "Untitled")))}</h1>{who_html}'
            f'<div class="hero-grid"><div class="hero-main">'
            f'<p class="headline">{rich(v.get("headline"), pills=False)}</p>{sub}{bullets(v.get("bullets"))}</div>'
            f'{score_card(r.get("score") or {})}</div>{facts(items)}</header>')


def nav(secs):
    links = "".join(f'<a href="#{s["id"]}" style="{s["acc"]}"><i class="dot" aria-hidden="true"></i>{esc(s["nav"])}</a>'
                    for s in secs)
    return (f'<nav class="nav" aria-label="Report sections"><div class="wrap"><div class="nav-row">'
            f'<div class="nav-in">{links}</div>'
            f'<button type="button" class="nav-more" tabindex="-1" aria-label="Scroll section links">\u203a</button>'
            f'</div></div></nav>')


def toc(secs):
    """The right-hand index: the section in view and the subsections inside it."""
    lis = []
    for i, s in enumerate(secs):
        subs = "".join(f'<li><a href="#{aid}">{esc(text)}</a></li>' for aid, text in s.get("subs") or [])
        lis.append(f'<li class="toc-sec{" cur" if i == 0 else ""}" data-sec="{s["id"]}" style="{s["acc"]}">'
                   f'<a class="toc-s" href="#{s["id"]}"><i class="dot" aria-hidden="true"></i>{esc(s["nav"])}</a>'
                   + (f'<ol class="toc-sub">{subs}</ol>' if subs else "") + "</li>")
    return f'<aside class="toc" aria-label="On this page"><p class="toc-k">On this page</p><ol>{"".join(lis)}</ol></aside>'


def prevnext(prev, nxt):
    def link(s, cls, word):
        return (f'<a class="pn-a {cls}" href="#{s["id"]}" style="{s["acc"]}"><span class="pn-k">{word}</span>'
                f'<span class="pn-t">{esc(s["nav"])}</span></a>')
    a = link(prev, "pn-p", "\u2190 Previous") if prev else "<span></span>"
    b = link(nxt, "pn-n", "Next \u2192") if nxt else "<span></span>"
    return f'<nav class="pn" aria-label="Previous and next section">{a}{b}</nav>'


MK_RE = re.compile(r'<h3 class="mk">(.*?)</h3>')
DISC_RE = re.compile(r'<details class="(disc[^"]*)" data-index="([^"]*)">')


def anchor_subsections(s, used):
    """Give each block heading and toggle in a section an id, and list them for the index."""
    subs = []

    def new_id(text):
        aid = f'{s["id"]}--{slug(text)}'
        while aid in used:
            aid += "-2"
        used.add(aid)
        subs.append((aid, text))
        return aid

    def mk(mo):
        return f'<h3 class="mk" id="{new_id(html.unescape(re.sub(r"<[^>]+>", "", mo.group(1))))}">{mo.group(1)}</h3>'

    def disc(mo):
        return f'<details class="{mo.group(1)}" id="{new_id(html.unescape(mo.group(2)))}">'

    s["body"] = DISC_RE.sub(disc, MK_RE.sub(mk, s["body"]))
    s["subs"] = subs


def wrap_section(s, prev, nxt):
    h = f'<h2 class="h2">{rich(s["headline"], pills=False)}</h2>' if s.get("headline") else ""
    sub = f'<p class="sub">{rich(s["sub"])}</p>' if s.get("sub") else ""
    return (f'<section class="sec" id="{s["id"]}" aria-labelledby="{s["id"]}-k" style="{s["acc"]}">'
            f'<header class="sec-h"><p class="kicker" id="{s["id"]}-k"><span class="num">{s["n"]:02d}</span>'
            f'<span>{esc(s["nav"])}</span></p>{h}{sub}</header>{s["body"]}{prevnext(prev, nxt)}</section>')


def player(audio_url, title, artists, dur):
    return (f'<div class="player" id="player" role="region" aria-label="Audio player"><div class="wrap pl-in">'
            f'<button type="button" class="pl-btn" aria-label="Play"><svg class="pl-ic" viewBox="0 0 24 24" aria-hidden="true">'
            f'<path class="pl-play" d="M8 5.5v13l11-6.5z"/><path class="pl-pause" d="M6.5 5h4v14h-4zM13.5 5h4v14h-4z"/></svg></button>'
            f'<div class="pl-meta"><span class="pl-title">{esc(smart(str(title)))}</span>'
            f'<span class="pl-sub">{esc(artists)}</span></div>'
            f'<div class="pl-wave" id="pl-wave" role="slider" tabindex="0" aria-label="Seek" aria-valuemin="0" '
            f'aria-valuemax="{int(dur or 0)}" aria-valuenow="0" aria-valuetext="0:00"></div>'
            f'<span class="pl-time"><span id="pl-cur">0:00</span><span class="pl-sep"> / </span>'
            f'<span id="pl-dur">{mmss(dur)}</span></span><span class="pl-msg" role="status">Audio unavailable</span>'
            f'<audio data-report-player preload="none" src="{esc(audio_url)}"></audio></div></div>')


FEEDBACK = ('<section class="fb" aria-label="Feedback"><p class="fb-q">Was this useful?</p>'
            '<div class="fb-b"><button type="button" data-fb="yes" aria-pressed="false">Yes</button>'
            '<button type="button" data-fb="no" aria-pressed="false">No</button></div>'
            '<p class="fb-thanks" hidden>Thanks for the feedback.</p></section>')

# ---------------------------------------------------------------------------
# Section bodies: each returns {headline, sub, body}
# ---------------------------------------------------------------------------


def verdict_body(r, emo, by_id):
    v = r.get("verdict") or {}
    src = "the report" if emo.get("from_report") else "the measurement"
    if emo.get("v") is not None:
        reading = (f'<div class="emo-read"><p class="emo-label">{esc(smart(emo.get("label") or ""))}</p>'
                   f'<dl class="mini"><div><dt>Valence</dt><dd>{emo["v"]:.2f}</dd></div>'
                   f'<div><dt>Arousal</dt><dd>{emo["a"]:.2f}</dd></div></dl>'
                   f'<p class="small muted">Valence runs from negative to positive feeling, arousal from calm '
                   f'to energetic; both on a 0\u20131 scale, taken from {src}.</p></div>')
    else:
        reading = '<div class="emo-read"><p class="small muted">No valence or arousal reading.</p></div>'
    emo_html = f'<div class="emo"><div class="panel"><div class="chart" id="ch-emotion"></div></div>{reading}</div>'
    rv, dives = [], []
    for it in v.get("review") or []:
        dd = ""
        target = by_id.get(str(it.get("deep_dive") or ""))
        if target:
            dd = (f'<a class="dd" href="#{target["id"]}" style="{target["acc"]}">Deep dive '
                  f'<span aria-hidden="true">\u2192</span> {esc(target["nav"])}</a>')
            if target not in dives:
                dives.append(target)
        rv.append(f'<article class="rv"><h3 class="h3">{rich(it.get("heading"), pills=False)}</h3>'
                  f'<div class="prose">{paras(it.get("paragraphs"))}</div>{dd}</article>')
    body = block("Emotional position", emo_html)
    body += block("The review", f'<div class="review">{"".join(rv)}</div>' if rv else "")
    if dives:
        lis = "".join(f'<li><a href="#{d["id"]}" style="{d["acc"]}"><i class="dot" aria-hidden="true"></i>'
                      f'{esc(d["nav"])}<span aria-hidden="true">\u2192</span></a></li>' for d in dives)
        body += block("Deep dives", f'<ul class="dds">{lis}</ul>')
    return {"body": body}


def best_moment_index(moments, m):
    times = [to_seconds(x.get("time")) for x in moments]
    for kind in ("vocal_hook", "climax"):
        for mo in m.get("moments") or []:
            if mo.get("type") != kind or num(mo.get("start")) is None:
                continue
            best, gap = None, 3.01
            for i, t in enumerate(times):
                if t is not None and abs(t - mo["start"]) < gap:
                    best, gap = i, abs(t - mo["start"])
            if best is not None:
                return best
    return 0 if moments else None


def first_listen_body(r, m):
    fi = r.get("first_impression") or {}
    moments = fi.get("standout_moments") or []
    best = best_moment_index(moments, m)
    cards = []
    for i, mo in enumerate(moments):
        is_best = i == best
        badge = '<span class="badge">Best moment</span>' if is_best else ""
        lyric = f'<blockquote class="lyric">\u201c{esc(smart(str(mo.get("lyric"))))}\u201d</blockquote>' if mo.get("lyric") else ""
        use = f'<p class="use"><span class="use-k">Use</span><span>{rich(mo["use"])}</span></p>' if mo.get("use") else ""
        foot = use + cuts_row(mo.get("cuts"), mo.get("cut_15"))
        cards.append(f'<article class="item moment{" best" if is_best else ""}">'
                     f'<div class="mo-top">{rich(mo.get("time"))}{badge}</div>{lyric}'
                     f'<h4 class="h4">{rich(mo.get("what"))}</h4>{paras(mo.get("why"))}'
                     f'{"<div class=" + chr(34) + "card-foot" + chr(34) + ">" + foot + "</div>" if foot else ""}</article>')
    body = block("Opening read", paras(fi.get("opening_read"), "lead"))
    body += ('<div class="cols">' + block("Sonic landscape", f'<div class="prose">{spec_or_paras(fi.get("sonic_landscape"))}</div>')
             + block("Production quality", f'<div class="prose">{paras(fi.get("production_quality"))}</div>') + "</div>")
    body += block("Standout moments", f'<div class="gc" style="--cols:{grid_cols(len(cards))}">{"".join(cards)}</div>' if cards else "")
    body += ('<div class="cols">' + block("Emotional texture", f'<div class="prose">{paras(fi.get("emotional_texture"))}</div>')
             + block("Weaknesses", f'<div class="prose">{paras(fi.get("weaknesses"))}</div>') + "</div>")
    body += ('<div class="cols">' + block("Lyrics & narrative", f'<div class="prose">{paras(fi.get("lyrics_and_narrative"))}</div>')
             + (block("Artist context", f'<div class="prose">{paras(fi.get("artist_context"))}</div>') if fi.get("artist_context") else "")
             + "</div>")
    if fi.get("quality_calibration"):
        body += block("Quality calibration", f'<div class="callout">{paras(fi.get("quality_calibration"))}</div>')
    return {"body": body}


def dimensions_strip(r, by_id):
    dims = r.get("dimensions") or {}
    cards = []
    for key, title, sid in DIMENSIONS:
        d = dims.get(key)
        if not d:
            continue
        acc = (by_id.get(sid) or {}).get("acc", "")
        cards.append(f'<article class="item dim" style="{acc}"><a class="dim-t" href="#{sid}">{esc(title)}</a>'
                     f'<p class="dim-s">{rich(d.get("summary"))}</p>{bullets(d.get("bullets"))}</article>')
    if not cards:
        return ""
    return (f'<section class="dims" id="dimensions" aria-labelledby="dimensions-k">'
            f'<p class="kicker" id="dimensions-k"><span>At a glance \u00b7 nine dimensions</span></p>'
            f'<div class="grid g3">{"".join(cards)}</div></section>')


def sonic_body(r, m):
    si = r.get("sonic_identity") or {}
    moods = si.get("moods") or []
    bars = "".join(
        f'<li><span class="mb-l">{esc(x.get("tag"))}</span><span class="mb-track"><span class="mb-fill" '
        f'style="width:{max(0, min(100, num(x.get("pct")) or 0)):.0f}%"></span></span>'
        f'<span class="mb-v">{fmt_num(x.get("pct"))}%</span></li>' for x in moods)
    mood_panel = (f'<div class="panel"><h3 class="mk">Mood profile</h3><div class="chart radar radar-alt" id="ch-mood"></div>'
                  f'<ul class="mbars">{bars}</ul><p class="cap">Mood weights from the report, 0\u2013100% each; '
                  f'they are independent, so they do not add up to 100.</p></div>')
    fp = m.get("fingerprint") or {}
    sl = []
    for key, lo, hi in FINGERPRINT:
        v = num(fp.get(key))
        if v is None:
            continue
        v = max(0.0, min(1.0, v))
        sl.append(f'<li><div class="sl-row"><span>{lo}</span><span class="sl-v">{v:.2f}</span><span>{hi}</span></div>'
                  f'<div class="sl-track" role="img" aria-label="{lo} to {hi}: {v:.2f}">'
                  f'<span class="sl-dot" style="left:{v * 100:.1f}%"></span></div></li>')
    note = f'<p class="note">{rich(si.get("fingerprint_note"))}</p>' if si.get("fingerprint_note") else ""
    fp_panel = (f'<div class="panel"><h3 class="mk">Sonic fingerprint</h3><div class="chart radar" id="ch-fp"></div>'
                f'<ul class="sliders">{"".join(sl)}</ul>{note}<p class="cap">Measured from the audio: each axis runs '
                f'0\u20131 between its two poles, 0.5 is the middle.</p></div>')
    body = f'<div class="grid g2 top blk">{mood_panel}{fp_panel}</div>'
    body += block("Technical details", facts(core_facts(r, m), "facts facts-tight"))
    body += issues(si.get("issues"))
    return {"headline": si.get("headline"), "sub": si.get("subhead"), "body": body}


def production_body(r, m):
    pc = r.get("production_craft") or {}
    ann = {b.get("band"): b for b in pc.get("bands") or []}
    prof = {b.get("band"): b for b in m.get("band_profile") or []}
    order = [b for b in BAND_ORDER if b in prof] + [b for b in prof if b not in BAND_ORDER]
    notes = []
    for b in order:
        st = str(prof[b].get("status") or "clear").lower()
        tag = f'<span class="pill p-{esc(slug(st))}">{esc(st.capitalize())}</span>' if st != "clear" else ""
        notes.append(f'<li>{tag}<span>{rich((ann.get(b) or {}).get("note"))}</span></li>')
    band_html = ""
    if order:
        band_html = (f'<div class="panel"><div class="scroll"><div class="minw-bands">'
                     f'<div class="chart wide" id="ch-bands"></div>'
                     f'<ol class="band-notes" style="grid-template-columns:repeat({len(order)},minmax(0,1fr))">'
                     f'{"".join(notes)}</ol></div></div>'
                     f'<p class="cap">Bar height is the band\u2019s measured level (0\u2013100); the percentage under each '
                     f'band is its share of the total energy. Bands are clear unless marked heavy or light.</p></div>')
    lufs, tp, ready = loudness(m)
    stats = []
    if lufs is not None:
        stats.append(("Integrated loudness", signed(lufs), "LUFS", "Measured across the whole file.", ""))
    if tp is not None:
        stats.append(("True peak", signed(tp, plus=True), "dBTP", "Broadcast delivery ceiling is \u22121.0 dBTP.", ""))
    if isinstance(ready, bool):
        why = "Passes the peak and loudness checks." if ready else (
            "Fails: true peak is above \u22121.0 dBTP." if tp is not None and tp > -1 else "Fails the loudness check.")
        stats.append(("Broadcast ready", "Yes" if ready else "No", "", why, "yes" if ready else "no"))
    stat_html = "".join(
        f'<div class="panel stat"><p class="k2">{k}</p><p class="v {c}">{esc(v)}'
        f'{"<span class=" + chr(34) + "u" + chr(34) + ">" + u + "</span>" if u else ""}</p><p class="c">{cap}</p></div>'
        for k, v, u, cap, c in stats)
    body = block("Frequency balance", band_html)
    body += block("Loudness", f'<div class="stats">{stat_html}</div>' if stats else "")
    body += block("Approach", f'<div class="prose">{paras(pc.get("approach"))}</div>' if pc.get("approach") else "")
    body += block("Mix", headed(pc.get("mix")))
    body += block("Techniques", ticks(pc.get("techniques")))
    body += issues(pc.get("issues"), "Areas to address")
    return {"headline": pc.get("headline"), "sub": pc.get("subhead"), "body": body}


def songwriting_body(r):
    sw = r.get("songwriting") or {}
    lines = "".join(
        f'<li><span class="ln-t">{rich(k.get("time"))}</span><div><p class="ln-q">\u201c{esc(smart(str(k.get("line"))))}\u201d</p>'
        f'<p class="ln-w">{rich(k.get("why"))}</p></div></li>' for k in sw.get("key_lines") or [])
    body = ('<div class="cols">' + block("Craft", f'<div class="prose">{paras(sw.get("craft"))}</div>')
            + block("Narrative arc", f'<div class="prose">{paras(sw.get("narrative_arc"))}</div>')
            + block("Theme", f'<div class="prose">{paras(sw.get("theme"))}</div>') + "</div>")
    body += block("Key lines", f'<ol class="lines">{lines}</ol>' if lines else "")
    return {"headline": sw.get("headline"), "body": body}


def form_list(m):
    """The measured sections as rows: name, a play pill for the span, the section's energy."""
    dur = num(m.get("duration_seconds")) or 0
    rows = []
    for sec in m.get("sections") or []:
        start = num(sec.get("start"))
        if start is None:
            continue
        end = num(sec.get("end")) or dur or start
        a, b = int(start), int(end)
        energy = num(sec.get("energy"))
        bar = (f'<span class="fl-bar" aria-hidden="true"><i style="width:{max(0, min(100, energy)):.0f}%"></i></span>'
               f'<span class="fl-v">{fmt_num(energy)}</span>') if energy is not None else "<span></span><span></span>"
        label = str(sec.get("label") or "").replace("_", " ").strip().capitalize() or "Section"
        rows.append(f'<li><span class="fl-l">{esc(label)}</span>{pill(a // 60, a % 60, b // 60, b % 60)}{bar}</li>')
    if not rows:
        return ""
    return (f'<ol class="form-list">{"".join(rows)}</ol>'
            f'<p class="cap">Measured sections; the bar is each section\u2019s energy, 0\u2013100.</p>')


def structure_body(r, m):
    st = r.get("structure") or {}
    drops = {d.get("type") for d in m.get("mute_drops") or []}
    legend = ('<ul class="legend"><li><i class="lg lg-curve"></i>Energy, 5-second average (0\u2013100)</li>'
              '<li><i class="lg lg-raw"></i>Per second</li>'
              + ('<li><i class="lg lg-mo"></i>Moment</li>' if m.get("moments") else "")
              + ('<li><i class="lg lg-mute"></i>Mute drop</li>' if drops - {"breakdown"} else "")
              + ('<li><i class="lg lg-bd"></i>Breakdown</li>' if "breakdown" in drops else "")
              + '<li><i class="lg lg-band"></i>Section</li></ul>')
    songmap = f'<div class="panel"><div class="chart wide" id="ch-songmap"></div>{legend}</div>'
    body = block("Song map", songmap)
    body += ('<div class="cols">' + block("Form", form_list(m) + f'<div class="prose">{paras(st.get("form"))}</div>')
             + block("Dynamics", f'<div class="prose">{paras(st.get("dynamics"))}</div>')
             + block("Creative DNA", f'<div class="prose">{paras(st.get("creative_dna"))}</div>') + "</div>")
    return {"headline": st.get("headline"), "body": body}


def market_body(r):
    mk = r.get("market") or {}
    aud = mk.get("audience") or {}
    kv = []
    if aud.get("age_range"):
        kv.append(f'<div><dt>Age</dt><dd>{esc(aud["age_range"])}</dd></div>')
    if aud.get("gender_skew"):
        kv.append(f'<div><dt>Skew</dt><dd>{esc(aud["gender_skew"])}</dd></div>')
    aud_html = ""
    if kv or aud.get("lifestyle_tags"):
        aud_html = (f'<div class="panel"><h3 class="mk">Audience</h3>'
                    f'{"<dl class=" + chr(34) + "kv" + chr(34) + ">" + "".join(kv) + "</dl>" if kv else ""}'
                    f'{chips(aud.get("lifestyle_tags"))}</div>')
    pl_html = f'<div class="panel"><h3 class="mk">Playlist fits</h3>{chips(mk.get("playlist_fits"))}</div>' if mk.get("playlist_fits") else ""
    body = block("Positioning", f'<div class="prose">{paras(mk.get("positioning"))}</div>' if mk.get("positioning") else "")
    if aud_html or pl_html:
        body += f'<div class="grid g2 blk">{aud_html}{pl_html}</div>'
    body += block("Influence map", ticks(mk.get("influence_map")))
    rows = "".join(f'<tr><td>{rich(b.get("category"))}</td><td>{rich(b.get("angle"))}</td><td class="td-cut">{rich(b.get("cut"))}</td></tr>'
                   for b in mk.get("brand_categories") or [])
    if rows:
        body += block("Brand categories", f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Category</th>'
                                          f'<th>Angle</th><th>Cut</th></tr></thead><tbody>{rows}</tbody></table></div>')
    return {"headline": ((r.get("dimensions") or {}).get("market_position") or {}).get("summary"), "body": body}


def comparables_body(r):
    mk = r.get("market") or {}
    arts = []
    for a in mk.get("comparable_artists") or []:
        era = f'<span class="tag">{esc(a["era"])}</span>' if a.get("era") else ""
        arts.append(f'<article class="item comp"><div class="comp-h"><h4 class="h4">{ext_link(esc(a.get("name")), a.get("url"))}</h4>{era}</div>'
                    f'{paras(a.get("why"))}</article>')
    songs = []
    for s in mk.get("comparable_songs") or []:
        name = f'{esc(smart(str(s.get("title"))))} <span class="by">\u00b7 {esc(s.get("artist"))}</span>'
        songs.append(f'<article class="item comp"><h4 class="h4">{ext_link(name, s.get("url"))}</h4>{paras(s.get("why"))}</article>')
    body = block("Sounds like", f'<div class="gc" style="--cols:{grid_cols(len(arts))}">{"".join(arts)}</div>' if arts else "")
    body += block("Comparable songs", f'<div class="gc" style="--cols:{grid_cols(len(songs))}">{"".join(songs)}</div>' if songs else "")
    if not body:
        body = '<p class="muted">No comparables in this report.</p>'
    return {"headline": ((r.get("dimensions") or {}).get("comparables") or {}).get("summary"), "body": body}


def resolve_edit_points(report_eps, meas_eps):
    out = []
    for e in report_eps or []:
        t = to_seconds(e.get("time"))
        if t is None:
            continue
        typ = "in" if str(e.get("type", "")).lower() == "in" else "out"
        snap, gap = None, 1.51
        for me in meas_eps or []:
            mt = num(me.get("time"))
            if mt is not None and abs(mt - t) < gap:
                snap, gap = mt, abs(mt - t)
        out.append({"type": typ, "t": snap if snap is not None else t, "name": e.get("name") or "",
                    "mmss": mmss(t)})
    return out


def sync_body(r):
    sy = r.get("sync") or {}
    sell = "".join(f"<li>{rich(s)}</li>" for s in sy.get("sell") or [])
    ep_rows = []
    for e in sy.get("edit_points") or []:
        typ = "in" if str(e.get("type", "")).lower() == "in" else "out"
        ep_rows.append(f'<li class="ep-row ep-{typ}"><div class="ep-line"><span class="pill p-{typ}">{typ.capitalize()}</span>'
                       f'<span class="ep-name">{rich(e.get("name"), pills=False)}</span>{rich(e.get("time"))}</div>'
                       f'<p class="ep-note">{rich(e.get("note"))}</p></li>')
    legend = ('<ul class="legend"><li><i class="lg lg-in"></i>In point</li><li><i class="lg lg-out"></i>Out point</li>'
              '<li><i class="lg lg-curve"></i>Energy, 5-second average (0\u2013100)</li></ul>')
    ep_html = (f'<div class="panel"><div class="scroll"><div class="minw-map"><div class="chart wide" id="ch-edits"></div>'
               f'</div></div>{legend}</div>')
    if ep_rows:
        ep_html += f'<ol class="eps">{"".join(ep_rows)}</ol>'
    scenes = []
    for s in sy.get("scene_archetypes") or []:
        medium = f'<span class="tag">{esc(s["medium"])}</span>' if s.get("medium") else ""
        foot = cuts_row(s.get("cuts"), s.get("cut_15"))
        scenes.append(f'<article class="item scene"><div class="mo-top">{rich(s.get("time"))}{medium}</div>'
                      f'<h4 class="h4">{rich(s.get("name"))}</h4>{paras(s.get("why"))}'
                      f'{"<div class=" + chr(34) + "card-foot" + chr(34) + ">" + foot + "</div>" if foot else ""}</article>')
    body = paras(sy.get("pitch"), "lead") if sy.get("pitch") else ""
    body += block("The sync sell", f'<ul class="sell">{sell}</ul>' if sell else "")
    body += block("Edit points", ep_html)
    body += block("Scene fit", f'<div class="gc" style="--cols:{grid_cols(len(scenes))}">{"".join(scenes)}</div>' if scenes else "")
    obs = sy.get("observations") or []
    body += disclosure("Further observations", headed(obs), len(obs), open_label="Hide further observations")
    body += issues(sy.get("issues"))
    return {"headline": sy.get("headline"), "body": body}


def growth_body(r):
    gr = r.get("growth") or {}
    opps = "".join(f'<li class="item"><span class="opp-n">{i:02d}</span><div><h4 class="h4">{rich(o.get("what"))}</h4>'
                   f'{paras(o.get("why"))}</div></li>' for i, o in enumerate(gr.get("opportunities") or [], 1))
    return {"headline": gr.get("headline"), "body": f'<ol class="opps">{opps}</ol>' if opps else ""}


def notes_body(r, m):
    notes = list((r.get("technical") or {}).get("notes") or [])
    lis = "".join(f"<li>{rich(x)}</li>" for x in notes)
    if m.get("measured_with"):
        lis += f'<li>Measurement version: <span class="tm">{esc(m["measured_with"])}</span>.</li>'
    method = ('<p class="method">Method: tempo, key, loudness, true peak, band balance, fingerprint, sections, moments, '
              'drops and edit points are measured from the audio file; the prose is written from a listening '
              'model\u2019s answers and checked against those measurements. Times are m:ss from the start of the file.</p>')
    return {"body": disclosure("Show method notes", f'<ul class="notes">{lis}</ul>' if lis else "", len(notes),
                               open_label="Hide method notes", index_label="Method notes") + method}


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_report(r):
    warn = [f"report is missing '{k}'" for k in REQUIRED if k not in r]
    sc = r.get("score") or {}
    subs = sc.get("subscores") or {}
    if subs and all(num(subs.get(k)) is not None for k, _, _ in SUBSCORES):
        expect = sum(num(subs[k]) * w for k, _, w in SUBSCORES) / 10
        if num(sc.get("total")) is not None and abs(num(sc["total"]) - expect) > 1:
            warn.append(f"score.total {sc['total']} differs from the rubric ({expect:.1f})")
    for key, _, _ in DIMENSIONS:
        d = (r.get("dimensions") or {}).get(key)
        if d is not None and len(d.get("bullets") or []) != 3:
            warn.append(f"dimensions.{key} has {len(d.get('bullets') or [])} bullets, expected 3")
    for i, mo in enumerate((r.get("first_impression") or {}).get("standout_moments") or []):
        if not mo.get("cuts") and not mo.get("cut_15"):
            warn.append(f"first_impression.standout_moments[{i}] has no cuts")
    for i, s in enumerate((r.get("sync") or {}).get("scene_archetypes") or []):
        if not s.get("cuts"):
            warn.append(f"sync.scene_archetypes[{i}] has no cuts")
    return warn


# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------

THEME_KEYS = ("color_scheme", "fonts", "tokens", "accents")


def load_theme(value):
    """A bare name loads themes/<name>.json beside this script; otherwise value is a path."""
    path = value
    if not (value.endswith(".json") or os.sep in value or "/" in value):
        path = os.path.join(HERE, "themes", f"{value}.json")
    with open(path, encoding="utf-8") as f:
        theme = json.load(f)
    missing = [k for k in THEME_KEYS if k not in theme]
    if missing:
        raise ValueError(f"theme {path} is missing {', '.join(missing)}")
    theme.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    return theme


def available_themes():
    d = os.path.join(HERE, "themes")
    return sorted(f[:-5] for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []


def theme_css(theme):
    def accent_tokens(accs):
        out = {}
        for i, a in enumerate(accs, 1):
            out[f"--acc-{i}"] = a["color"]
            out[f"--acc-{i}-soft"] = a["soft"]
        return out

    def block_of(tokens):
        return "".join(f"{k}:{v};" for k, v in tokens.items())

    light = dict(theme["tokens"], **accent_tokens(theme["accents"]))
    schemes = theme["color_scheme"].split()
    css = f":root{{{block_of(light)}color-scheme:{schemes[0]};}}\n"
    if theme.get("dark_tokens"):
        dark = dict(theme["dark_tokens"], **accent_tokens(theme.get("dark_accents") or theme["accents"]))
        css += (f'@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{block_of(dark)}color-scheme:dark;}}}}\n'
                f':root[data-theme="dark"]{{{block_of(dark)}color-scheme:dark;}}\n')
    return css


def accent_style(theme, i):
    k = i % len(theme["accents"]) + 1
    return f"--sa:var(--acc-{k});--sa-soft:var(--acc-{k}-soft)"


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_page(r, m, theme, extra, date_label, audio=None):
    idn = r.get("identity") or {}
    ep = (r.get("verdict") or {}).get("emotional_position") or {}
    v_rep, a_rep = unit(ep.get("valence")), unit(ep.get("arousal"))
    from_report = v_rep is not None and a_rep is not None
    emo = {
        "v": v_rep if from_report else unit(m.get("valence")),
        "a": a_rep if from_report else unit(m.get("arousal")),
        "label": ep.get("label") or idn.get("primary_mood") or "",
        "from_report": from_report,
    }
    if emo["v"] is None or emo["a"] is None:
        emo["v"] = emo["a"] = None

    secs = [{"id": sid, "nav": label} for sid, label in CORE]
    used = {s["id"] for s in secs} | {"dimensions", "notes", "main", "player"}
    for x in extra:
        title = str(x.get("title") or "Extra")
        sid = "x-" + slug(x.get("nav") or title)
        while sid in used:
            sid += "-2"
        used.add(sid)
        words = re.findall(r"\S+", smart(title))
        secs.append({"id": sid, "nav": smart(str(x.get("nav") or " ".join(words[:2]))), "extra": x})
    secs.append({"id": "notes", "nav": "Notes"})
    for i, s in enumerate(secs):
        s["n"] = i + 1
        s["acc"] = accent_style(theme, i)
    by_id = {s["id"]: s for s in secs}
    # The schema's deep_dive names this section "sonic-identity"; keep both spellings working.
    by_id.setdefault("sonic", by_id["sonic-identity"])

    builders = {
        "verdict": lambda: verdict_body(r, emo, by_id),
        "first-listen": lambda: first_listen_body(r, m),
        "sonic-identity": lambda: sonic_body(r, m),
        "production": lambda: production_body(r, m),
        "songwriting": lambda: songwriting_body(r),
        "structure": lambda: structure_body(r, m),
        "market": lambda: market_body(r),
        "comparables": lambda: comparables_body(r),
        "sync": lambda: sync_body(r),
        "growth": lambda: growth_body(r),
        "notes": lambda: notes_body(r, m),
    }
    parts = []
    for i, s in enumerate(secs):
        if "extra" in s:
            s.update({"headline": smart(str(s["extra"].get("title") or "")),
                      "body": f'<div class="extra">{enrich_html(s["extra"].get("html") or "")}</div>'})
        else:
            s.update(builders[s["id"]]())
        anchor_subsections(s, used)
        parts.append(wrap_section(s, secs[i - 1] if i else None, secs[i + 1] if i + 1 < len(secs) else None))
        if s["id"] == "first-listen":
            parts.append(dimensions_strip(r, by_id))
    parts.append(FEEDBACK)

    data = {
        "m": m,
        "r": {
            "emo": {"v": emo["v"], "a": emo["a"], "label": smart(str(emo["label"]))},
            "moods": [{"tag": x.get("tag"), "pct": num(x.get("pct"))} for x in (r.get("sonic_identity") or {}).get("moods") or []],
            "bands": {b.get("band"): smart(str(b.get("annotation") or "")) for b in (r.get("production_craft") or {}).get("bands") or []},
            "edit_points": resolve_edit_points((r.get("sync") or {}).get("edit_points"), m.get("edit_points")),
        },
    }

    title = str(idn.get("title") or "Untitled")
    dur = num(m.get("duration_seconds")) or to_seconds(idn.get("duration_mmss")) or 0
    audio_url = media_url(audio)
    player_html = player(audio_url, title, idn.get("artists") or "", dur) if audio_url else ""
    fonts = "".join(f'<link rel="stylesheet" href="{esc(u)}">\n' for u in theme.get("fonts") or [])
    preconnect = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                  '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n') if fonts else ""
    return (
        "<!doctype html>\n"
        f'<html lang="en" data-report-theme="{esc(theme["name"])}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f'<meta name="color-scheme" content="{esc(theme["color_scheme"])}">\n'
        f"<title>{esc(smart(title))} \u00b7 Analyst report</title>\n"
        '<link rel="icon" href="data:,">\n'
        f"{preconnect}{fonts}"
        f"<style>{theme_css(theme)}{BASE_CSS}{theme.get('css') or ''}</style>\n</head>\n"
        f'<body{" class=" + chr(34) + "has-player" + chr(34) if player_html else ""}>\n{theme.get("decor_html") or ""}'
        f"{hero(r, m, date_label)}\n{nav(secs)}\n"
        f'<div class="wrap layout"><main id="main">{"".join(parts)}</main>{toc(secs)}</div>\n'
        f'<footer class="wrap foot"><p>{esc(smart(title))} \u00b7 analyst report \u00b7 {esc(date_label)}</p></footer>\n'
        f"{player_html}\n"
        f'<script type="application/json" id="report-data">{json_for_script(data)}</script>\n'
        f"<script>{JS}</script>\n</body>\n</html>\n"
    )


# ---------------------------------------------------------------------------
# Shared layout CSS (colours come only from theme tokens)
# ---------------------------------------------------------------------------

BASE_CSS = """
:root{--sa:var(--accent-text);--sa-soft:var(--accent-soft)}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%;scroll-padding-top:76px;scroll-padding-bottom:88px}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font-body);font-size:16px;line-height:1.6;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;overflow-wrap:break-word}
body.has-player{padding-bottom:calc(80px + env(safe-area-inset-bottom,0px))}
a{color:var(--link)}
h1,h2,h3,h4{text-wrap:balance}
p{margin:0 0 14px}
.wrap{width:100%;max-width:1080px;margin-left:auto;margin-right:auto;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
@media (min-width:1200px){.wrap{max-width:1320px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 196px;column-gap:44px;align-items:start}}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.muted{color:var(--muted)}.small{font-size:13.5px;line-height:1.5}
.nw{white-space:nowrap}

/* hero */
.hero{padding-top:clamp(28px,6vw,64px);padding-bottom:28px}
.eyebrow{font-family:var(--eyebrow-font);font-size:12px;letter-spacing:var(--eyebrow-tracking);text-transform:uppercase;color:var(--muted);margin:0 0 18px}
.title{font-size:clamp(20px,2.4vw,24px);font-weight:600;letter-spacing:-.01em;line-height:1.25;margin:0}
.who{display:flex;flex-wrap:wrap;gap:4px 16px;margin:6px 0 0;color:var(--muted);font-size:14.5px;line-height:1.5}
.who-a{color:var(--text);font-weight:600}.who-k{color:var(--faint)}
.tag{display:inline-flex;align-items:center;font-family:var(--font-label);font-size:12px;letter-spacing:.04em;text-transform:uppercase;padding:2px 8px;border-radius:999px;box-shadow:inset 0 0 0 1px var(--line2);color:var(--muted);line-height:1.45;white-space:nowrap}
.hero-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,320px);gap:clamp(24px,4vw,48px);align-items:start;margin-top:clamp(22px,3vw,34px)}
@media (max-width:860px){.hero-grid{grid-template-columns:minmax(0,1fr)}}
.hero-main{max-width:820px}
.headline{font-family:var(--font-display);font-weight:var(--display-weight);font-size:var(--headline-size);line-height:var(--display-lh);letter-spacing:var(--display-tracking);margin:0 0 18px;text-wrap:balance}
.subhead{font-size:clamp(16.5px,1.8vw,18.5px);line-height:1.55;color:var(--muted);margin:0;max-width:62ch}

/* typed bullets */
.bul{list-style:none;margin:22px 0 0;padding:0;display:grid;gap:10px}
.bul li{display:grid;grid-template-columns:24px minmax(0,1fr);gap:12px;align-items:start;line-height:1.5}
.b-i{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:12.5px;font-weight:700;line-height:1}
.b-ok .b-i{background:var(--ok-soft);color:var(--ok)}
.b-neu .b-i{background:var(--neutral-soft);color:var(--neutral)}
.b-risk .b-i{background:var(--risk-soft);color:var(--risk)}

/* facts strip */
.facts{display:grid;grid-template-columns:repeat(var(--fc,5),minmax(0,1fr));margin:clamp(28px,4vw,40px) 0 0;padding:0;border-top:1px solid var(--line)}
@media (max-width:640px){.facts{grid-template-columns:repeat(2,minmax(0,1fr))}}
.fact{min-width:0;padding:12px 14px 12px 0;border-bottom:1px solid var(--line)}
.fact dt{font-family:var(--font-label);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin:0 0 4px}
.fact dd{margin:0;font-size:15px;font-weight:600;line-height:1.3;font-variant-numeric:tabular-nums}
.fact .yes{color:var(--ok)}.fact .no{color:var(--risk)}
.facts-tight{margin-top:0}

/* score */
.score{background:var(--sc-bg);color:var(--sc-text);border-radius:var(--r-outer);padding:22px 22px 18px;box-shadow:inset 0 0 0 1px var(--sc-line),0 0 56px -18px var(--glow)}
.score .k{font-family:var(--font-label);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--sc-muted);margin:0 0 10px}
.score-top{display:flex;gap:16px;align-items:center}
.ring{width:128px;height:128px;flex:none}
.ring-track{fill:none;stroke:var(--sc-track);stroke-width:10}
.ring-val{fill:none;stroke:var(--hi);stroke-width:10;stroke-linecap:round}
.ring-n{fill:var(--sc-text);font-family:var(--font-label);font-size:38px;font-weight:600;font-variant-numeric:tabular-nums}
.ring-d{fill:var(--sc-muted);font-family:var(--font-label);font-size:12px;letter-spacing:.06em}
.score-line{font-size:14px;line-height:1.45;margin:0;color:var(--sc-text)}
.ss{list-style:none;margin:18px 0 0;padding:14px 0 0;border-top:1px solid var(--sc-line);display:grid;gap:8px}
.ss li{display:grid;grid-template-columns:minmax(0,1fr) 72px 22px;gap:10px;align-items:center;font-size:13px}
.ss-l{color:var(--sc-text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ss-w{color:var(--sc-muted);font-family:var(--font-label);font-size:12px;margin-left:7px}
.ss-bar{height:6px;border-radius:99px;background:var(--sc-track);overflow:hidden}
.ss-bar i{display:block;height:100%;border-radius:99px;background:var(--sc-bar)}
.ss-v{font-family:var(--font-label);font-size:12.5px;text-align:right;color:var(--sc-text);font-variant-numeric:tabular-nums}

/* nav */
.nav{position:sticky;top:0;z-index:30;background:var(--nav-bg);-webkit-backdrop-filter:saturate(1.4) blur(14px);backdrop-filter:saturate(1.4) blur(14px);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.nav-row{position:relative}
.nav-in{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;padding:8px 0}
.nav-in::-webkit-scrollbar{display:none}
.nav a{display:inline-flex;align-items:center;gap:7px;flex:none;white-space:nowrap;font-size:13px;font-weight:500;color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:999px;transition:background-color .15s,color .15s,box-shadow .15s}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--sa);flex:none}
.nav a:hover{color:var(--text)}
.nav a.on{color:var(--text);background:var(--sa-soft);box-shadow:inset 0 0 0 1px var(--sa)}
.nav a:focus-visible{outline:2px solid var(--sa);outline-offset:1px}
.nav-row::before,.nav-row::after{content:"";position:absolute;top:0;bottom:0;pointer-events:none;opacity:0;transition:opacity .2s}
.nav-row::before{left:0;width:36px;background:linear-gradient(270deg,var(--nav-fade0),var(--nav-solid) 70%)}
.nav-row::after{right:0;width:84px;background:linear-gradient(90deg,var(--nav-fade0),var(--nav-solid) 55%)}
.nav.less .nav-row::before,.nav.more .nav-row::after{opacity:1}
.nav-more{display:none;position:absolute;right:0;top:50%;transform:translateY(-50%);z-index:1;width:30px;height:30px;border-radius:50%;border:1px solid var(--line2);background:var(--nav-solid);color:var(--text);font:600 18px/1 var(--font-body);cursor:pointer;place-items:center;padding:0 0 2px}
.nav.more .nav-more{display:grid}

/* on-this-page index */
.toc{display:none}
@media (min-width:1200px){.toc{display:block;position:sticky;top:64px;padding:clamp(40px,6vw,64px) 0 24px;max-height:100vh;overflow:auto}}
.toc-k{font-family:var(--font-label);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.toc ol{list-style:none;margin:0;padding:0}
.toc-sec{display:none}
.toc-sec.cur{display:block}
.toc-s{display:flex;align-items:center;gap:8px;margin:0 0 10px;font-size:15px;font-weight:600;line-height:1.3;color:var(--text);text-decoration:none}
.toc-sub{box-shadow:inset 1px 0 0 var(--line)}
.toc-sub a{display:block;padding:5px 0 5px 14px;font-size:13.5px;line-height:1.4;color:var(--muted);text-decoration:none;transition:color .15s,box-shadow .15s}
.toc-sub a:hover{color:var(--text)}
.toc-sub a.on{color:var(--text);font-weight:600;box-shadow:inset 2px 0 0 var(--sa)}

/* sections */
.sec{position:relative;padding:clamp(40px,6vw,64px) 0 clamp(16px,2.4vw,24px)}
.sec::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,var(--sa),var(--rule-end) 45%)}
.sec::after{content:"";position:absolute;top:-1px;left:0;width:44px;height:3px;border-radius:0 0 3px 3px;background:var(--sa)}
.sec-h{margin:0 0 clamp(4px,1vw,8px);max-width:780px}
.kicker{display:flex;align-items:baseline;gap:10px;font-family:var(--eyebrow-font);font-size:12px;letter-spacing:var(--eyebrow-tracking);text-transform:uppercase;color:var(--sa);margin:0 0 12px;font-weight:600}
.kicker .num{font-family:var(--font-label);color:var(--faint);letter-spacing:.04em;font-weight:500}
.h2{font-family:var(--font-display);font-weight:var(--display-weight);font-size:var(--h2-size);line-height:1.15;letter-spacing:var(--display-tracking);margin:0}
.sub{font-size:17px;line-height:1.55;color:var(--muted);margin:12px 0 0;max-width:66ch}
.blk{margin:clamp(28px,4vw,40px) 0 0;min-width:0}
.sp{margin-top:14px}
.mk{display:flex;align-items:center;gap:12px;font-family:var(--font-label);font-size:12px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 14px;line-height:1.3}
.mk::after{content:"";flex:1;height:1px;background:var(--line)}
.prose p{max-width:70ch}
.prose p:last-child{margin-bottom:0}
.lead{font-size:clamp(18px,2.1vw,21px);line-height:1.55;max-width:62ch;margin:0}
.lead+.lead{margin-top:14px}
.sec-h+.lead{margin-top:clamp(20px,3vw,28px)}
.h3{font-size:clamp(18px,2vw,21px);font-weight:600;line-height:1.3;letter-spacing:-.01em;margin:0 0 10px}
.h4{font-size:16px;font-weight:600;line-height:1.35;margin:0 0 6px;letter-spacing:-.005em}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));column-gap:clamp(24px,3.5vw,44px)}
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr))}
.gc{display:grid;gap:14px;grid-template-columns:repeat(var(--cols,3),minmax(0,1fr))}
@media (max-width:900px){.gc{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){.gc{grid-template-columns:minmax(0,1fr)}}
.panel{background:var(--panel);border-radius:var(--r-panel);box-shadow:inset 0 0 0 1px var(--line);padding:clamp(16px,2.4vw,24px);min-width:0}
.item{background:var(--item);border-radius:var(--r-item);padding:16px 18px;min-width:0;box-shadow:var(--item-shadow)}
.item p{margin:0 0 8px;font-size:15px;line-height:1.55}
.item p:last-child{margin-bottom:0}
.by{font-weight:400;color:var(--muted)}
.callout{padding:18px 20px;border-radius:var(--r-panel);background:var(--sa-soft);box-shadow:inset 3px 0 0 var(--sa)}
.callout p{margin:0;max-width:72ch}
.callout p+p{margin-top:10px}
.cap{font-size:12.5px;line-height:1.5;color:var(--faint);margin:12px 0 0}

/* play pills */
.t{-webkit-appearance:none;appearance:none;display:inline-flex;align-items:baseline;gap:5px;font:inherit;font-family:var(--font-label);font-size:max(12px,.8em);font-weight:500;line-height:1.35;padding:1px 8px 1px 7px;margin:0 1px;border-radius:999px;border:1px solid var(--chip-border);background:var(--chip-bg);color:var(--chip-text);cursor:pointer;vertical-align:baseline;white-space:nowrap;letter-spacing:0;text-transform:none;font-variant-numeric:tabular-nums}
.t-g{color:var(--sa);font-family:var(--font-body);font-size:1em;line-height:1}
.t-k{color:var(--muted)}
.tm{font-family:var(--font-label);font-size:max(12px,.86em);white-space:nowrap;font-variant-numeric:tabular-nums;letter-spacing:0}
.t:hover{border-color:var(--sa)}
.t:focus-visible{outline:2px solid var(--sa);outline-offset:2px}
.t.on{background:var(--sa-soft);border-color:var(--sa);color:var(--text)}
.headline .t,.h2 .t,.emo-label .t{font-size:.6em;vertical-align:.16em}
.cuts{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.cuts-k,.use-k{font-family:var(--font-label);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin-right:2px}
.cuts .t{font-size:12px}
.use{display:flex;gap:10px;align-items:baseline;margin:0;font-size:13.5px!important;color:var(--muted)}
.card-foot{margin-top:auto;padding-top:12px;border-top:1px solid var(--line);display:grid;gap:8px}

/* verdict */
.review{display:grid;gap:clamp(22px,3vw,30px);max-width:760px;counter-reset:rv}
.rv{counter-increment:rv}
.rv .h3::before{content:counter(rv,decimal-leading-zero);font-family:var(--font-label);font-size:12px;font-weight:500;color:var(--faint);margin-right:12px;vertical-align:.18em}
.dd{display:inline-flex;align-items:center;gap:6px;margin-top:12px;font-size:14px;font-weight:600;color:var(--sa);text-decoration:none}
.dd:hover{text-decoration:underline}
.dds{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.dds a{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;background:var(--sa-soft);box-shadow:inset 0 0 0 1px var(--sa);color:var(--text);text-decoration:none;font-size:14px;font-weight:500}
.emo{display:grid;grid-template-columns:minmax(0,400px) minmax(0,1fr);gap:clamp(20px,4vw,40px);align-items:center}
@media (max-width:760px){.emo{grid-template-columns:minmax(0,1fr)}}
.emo-label{font-family:var(--font-display);font-weight:var(--display-weight);font-size:clamp(24px,3vw,32px);line-height:1.15;letter-spacing:var(--display-tracking);margin:0 0 16px}
.mini{display:flex;gap:32px;margin:0 0 14px}
.mini dt{font-family:var(--font-label);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.mini dd{margin:2px 0 0;font-family:var(--stat-font);font-size:26px;font-weight:var(--stat-weight);font-variant-numeric:tabular-nums}

/* moments, scenes, dimensions */
.moment,.scene,.ep,.comp{display:flex;flex-direction:column;gap:8px}
.moment .h4,.scene .h4{margin:2px 0 0}
.mo-top{display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:24px}
.mo-top>.t,.mo-top>.nw>.t{font-size:13px}
.best{box-shadow:inset 0 0 0 2px var(--hi)}
.badge{font-family:var(--font-label);font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:3px 9px;border-radius:999px;background:var(--hi);color:var(--hi-ink)}
.lyric{margin:0;font-style:italic;font-size:15.5px;line-height:1.45;color:var(--text);padding-left:12px;border-left:2px solid var(--line2)}
.comp-h{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
.comp-h .h4{margin:0}
.ext{color:var(--text);text-decoration:none;box-shadow:inset 0 -1px 0 var(--line2)}
.ext:hover{box-shadow:inset 0 -2px 0 var(--sa)}
.ext-i{color:var(--sa);margin-left:4px;font-size:.9em}
.dims{padding:clamp(36px,5vw,52px) 0 8px}
.dims>.kicker{color:var(--muted)}
.dim{display:flex;flex-direction:column;gap:8px}
.dim-t{font-family:var(--font-label);font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--sa);text-decoration:none;align-self:flex-start}
.dim-t:hover{text-decoration:underline}
.dim-s{font-size:16px;font-weight:600;line-height:1.35;margin:0}
.dim .bul{margin:4px 0 0;gap:8px}
.dim .bul li{grid-template-columns:20px minmax(0,1fr);gap:9px;font-size:14px;line-height:1.45}
.dim .b-i{width:20px;height:20px;font-size:12px}
.spec{margin:0}
.spec div{display:grid;grid-template-columns:96px minmax(0,1fr);gap:14px;padding:9px 0;border-top:1px solid var(--line)}
.spec div:last-child{border-bottom:1px solid var(--line)}
.spec dt{font-family:var(--font-label);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding-top:3px}
.spec dd{margin:0;font-size:15px;line-height:1.5}
.spec-out{margin-top:12px}

/* sonic identity */
.mbars,.sliders{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:11px}
.mbars li{display:grid;grid-template-columns:minmax(0,118px) minmax(0,1fr) 44px;gap:12px;align-items:center;font-size:14px}
.mb-l{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mb-track{height:8px;border-radius:99px;background:var(--band-a);box-shadow:inset 0 0 0 1px var(--line);overflow:hidden}
.mb-fill{display:block;height:100%;border-radius:99px;background:var(--alt)}
.mb-v{font-family:var(--font-label);font-size:13px;text-align:right;font-variant-numeric:tabular-nums}
.sl-row{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-size:13px;color:var(--muted);margin-bottom:7px}
.sl-v{font-family:var(--font-label);font-size:12px;color:var(--text);font-variant-numeric:tabular-nums}
.sl-track{position:relative;height:6px;border-radius:99px;background:var(--band-a);box-shadow:inset 0 0 0 1px var(--line)}
.sl-track::before{content:"";position:absolute;left:50%;top:-3px;bottom:-3px;width:1px;background:var(--line2)}
.sl-dot{position:absolute;top:50%;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px var(--halo)}
.note{margin:18px 0 0;font-size:14.5px;line-height:1.55;color:var(--muted)}
.radar svg{margin:0 auto}

/* charts */
.chart{min-width:0}
.chart svg{display:block;max-width:none}
.emo .chart svg,.radar svg{margin:0 auto}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain}
.minw-map{min-width:880px}.minw-bands{min-width:820px}
.na{color:var(--muted);font-size:14px;margin:0}
.legend{list-style:none;display:flex;flex-wrap:wrap;gap:6px 18px;margin:12px 0 0;padding:0;font-size:12.5px;color:var(--muted)}
.legend li{display:flex;align-items:center;gap:7px}
.lg{display:inline-block;width:12px;height:12px;flex:none}
.lg-curve{height:3px;border-radius:2px;background:var(--curve)}
.lg-raw{height:1px;background:var(--muted)}
.lg-mo{width:9px;height:9px;transform:rotate(45deg);background:var(--mark)}
.lg-mute{width:10px;height:9px;background:var(--risk);clip-path:polygon(0 0,100% 0,50% 100%)}
.lg-bd{background:var(--warn-soft);box-shadow:inset 0 0 0 1px var(--warn)}
.lg-band{background:var(--band-a);box-shadow:inset 0 0 0 1px var(--line2)}
.lg-in,.lg-out{width:10px;height:10px;border-radius:50%}
.lg-in{background:var(--ok)}.lg-out{background:var(--risk)}
.chart text{font-family:var(--font-body)}
.measure{position:absolute;left:-9999px;top:0;width:0;height:0;overflow:hidden;visibility:hidden}
.ax{font-family:var(--font-label);font-size:12px;fill:var(--faint)}
.ax-t{font-family:var(--font-label);font-size:12px;letter-spacing:.12em;fill:var(--faint)}
.ax-e{font-size:12px;font-weight:600;fill:var(--muted)}
.ax-ar{stroke:var(--faint);stroke-width:1}
.ax-hd{fill:var(--faint)}
.gl{stroke:var(--grid);stroke-width:1}
.base{stroke:var(--line2);stroke-width:1}
.tick{stroke:var(--line2);stroke-width:1}
.sb-a{fill:var(--band-a)}.sb-b{fill:var(--band-b)}
.sec-div{stroke:var(--line2);stroke-width:1;stroke-dasharray:3 3}
.sec-l{font-size:12.5px;font-weight:600;fill:var(--text)}
.sec-t{font-family:var(--font-label);font-size:12px;fill:var(--muted)}
.e-area{fill:var(--curve-fill)}
.e-line{fill:none;stroke:var(--curve);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.e-raw{fill:none;stroke:var(--curve-raw);stroke-width:1}
.bd{fill:var(--warn-soft)}
.bd-l{stroke:var(--warn);stroke-width:1;stroke-dasharray:2 2}
.mute-l{stroke:var(--risk);stroke-width:1;stroke-dasharray:2 3;opacity:.6}
.mute-t{fill:var(--risk)}
.mo-d{fill:var(--mark);stroke:var(--halo);stroke-width:2}
.mo-lead{stroke:var(--muted);stroke-width:1;stroke-dasharray:2 2;opacity:.75}
.lab{font-size:12px;font-weight:600;fill:var(--text)}
.lab-tm{font-family:var(--font-label);font-size:12px;font-weight:500;fill:var(--muted)}
.lab-bd{fill:var(--warn)}
.halo{paint-order:stroke fill;stroke:var(--halo);stroke-width:4px;stroke-linejoin:round}
.ep-area{fill:var(--curve-fill)}
.ep-line{fill:none;stroke:var(--curve);stroke-width:1.75;stroke-linejoin:round}
.ep-l{stroke-width:1.5}.ep-l-in{stroke:var(--ok)}.ep-l-out{stroke:var(--risk)}
.ep-c{stroke:var(--halo);stroke-width:2}.ep-c-in{fill:var(--ok)}.ep-c-out{fill:var(--risk)}
.ep-t{font-family:var(--font-label);font-size:12px;font-weight:600}
.ep-t-in{fill:var(--ok)}.ep-t-out{fill:var(--risk)}
.bar-track{fill:var(--band-a)}
.bar-clear{fill:var(--curve)}.bar-heavy{fill:var(--warn)}.bar-light{fill:var(--neutral-bar)}
.bar-v{font-family:var(--font-label);font-size:12px;font-weight:600;fill:var(--text)}
.bar-a{font-size:12px;fill:var(--muted)}
.bar-n{font-family:var(--font-label);font-size:12px;font-weight:600;letter-spacing:.06em;fill:var(--text)}
.bar-hz{font-family:var(--font-label);font-size:12px;fill:var(--muted)}
.bar-s{font-size:12px;fill:var(--faint)}
.emo-bg{fill:var(--band-a);stroke:var(--line);stroke-width:1}
.emo-mid{stroke:var(--line2);stroke-width:1;stroke-dasharray:4 4}
.emo-qt{font-size:12px;fill:var(--faint)}
.emo-halo{fill:var(--accent-halo)}
.emo-pt{fill:var(--accent);stroke:var(--halo);stroke-width:2}
.emo-guide{stroke:var(--accent);stroke-width:1;stroke-dasharray:2 3;opacity:.7}
.emo-l{font-size:13px;font-weight:700;fill:var(--text)}
.emo-v{font-family:var(--font-label);font-size:12px;fill:var(--muted)}
.rd-ring{fill:none;stroke:var(--grid);stroke-width:1}
.rd-outer{stroke:var(--line2)}
.rd-spoke{stroke:var(--grid);stroke-width:1}
.rd-shape{fill:var(--accent-halo);stroke:var(--accent);stroke-width:2;stroke-linejoin:round}
.rd-dot{fill:var(--accent);stroke:var(--halo);stroke-width:1.5}
.radar-alt .rd-shape{fill:var(--alt-soft);stroke:var(--alt)}
.radar-alt .rd-dot{fill:var(--alt)}
.rd-l{font-size:12.5px;font-weight:600;fill:var(--text)}
.rd-s{font-family:var(--font-label);font-size:12px;fill:var(--muted)}
.seek{cursor:pointer}
.seek:hover .mo-d{fill:var(--accent)}

/* production */
.band-notes{display:grid;list-style:none;margin:4px 0 0;padding:0}
.band-notes li{display:flex;flex-direction:column;align-items:flex-start;gap:6px;padding:10px 8px 0;border-top:1px solid var(--line);font-size:13px;line-height:1.45;color:var(--muted);min-width:0}
.pill{display:inline-flex;align-items:center;font-family:var(--font-label);font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:2px 8px;border-radius:999px;line-height:1.3}
.p-clear,.p-in{background:var(--ok-soft);color:var(--ok)}
.p-heavy{background:var(--warn-soft);color:var(--warn)}
.p-light{background:var(--neutral-soft);color:var(--neutral)}
.p-out{background:var(--risk-soft);color:var(--risk)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:14px}
.stat .k2{font-family:var(--font-label);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}
.stat .v{font-family:var(--stat-font);font-size:var(--stat-size);font-weight:var(--stat-weight);line-height:1.05;letter-spacing:-.02em;margin:0;font-variant-numeric:tabular-nums}
.stat .u{font-family:var(--font-body);font-size:14px;font-weight:500;letter-spacing:0;color:var(--muted);margin-left:6px}
.stat .c{font-size:13px;line-height:1.45;color:var(--muted);margin:10px 0 0}
.stat .v.yes{color:var(--ok)}.stat .v.no{color:var(--risk)}
.hbs{display:grid;gap:22px;max-width:760px}
.top{align-items:start}
.form-list{list-style:none;margin:0 0 6px;padding:0}
.form-list li{display:grid;grid-template-columns:minmax(0,64px) auto minmax(24px,1fr) 26px;gap:10px;align-items:center;padding:6px 0;border-bottom:1px solid var(--line);font-size:14px}
.fl-l{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.form-list .t{justify-self:start}
.fl-bar{height:6px;border-radius:99px;background:var(--band-a);box-shadow:inset 0 0 0 1px var(--line);overflow:hidden}
.fl-bar i{display:block;height:100%;border-radius:99px;background:var(--sa)}
.fl-v{font-family:var(--font-label);font-size:12px;text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}
.form-list+.cap{margin:8px 0 16px}
.ticks{list-style:none;margin:0;padding:0;display:grid;gap:8px;max-width:760px}
.ticks li{position:relative;padding-left:20px;line-height:1.5}
.ticks li::before{content:"";position:absolute;left:2px;top:.6em;width:7px;height:7px;border-radius:2px;background:var(--sa)}
.issue{display:flex;flex-direction:column;gap:8px}
.issue-h{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.issue-h .h4{margin:0}
.issue-h .t{flex:none;margin-top:1px}
.fix{margin-top:2px;padding:10px 12px 10px 14px;border-left:3px solid var(--sa);background:var(--sa-soft);border-radius:0 10px 10px 0}
.fix-k{display:block;font-family:var(--font-label);font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--sa);margin:0 0 4px}
.fix p{margin:0;font-size:14.5px}

/* songwriting */
.lines{list-style:none;margin:0;padding:0;max-width:820px}
.lines li{display:grid;grid-template-columns:72px minmax(0,1fr);gap:16px;padding:16px 0;border-top:1px solid var(--line)}
.lines li:last-child{border-bottom:1px solid var(--line)}
.ln-t .t{font-size:13px}
.ln-q{font-size:clamp(17px,2vw,20px);font-weight:600;line-height:1.35;letter-spacing:-.01em;margin:0 0 4px}
.ln-w{margin:0;color:var(--muted);font-size:15px}

/* market, sync, growth */
.chips{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.chips li{padding:6px 12px;border-radius:999px;background:var(--item);box-shadow:inset 0 0 0 1px var(--line);font-size:14px;line-height:1.3}
.kv{display:grid;gap:6px;margin:0 0 16px}
.kv div{display:grid;grid-template-columns:64px minmax(0,1fr);gap:12px}
.kv dt{font-family:var(--font-label);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);padding-top:3px}
.kv dd{margin:0;font-weight:600}
.tbl-wrap{overflow-x:auto}
.tbl{width:100%;min-width:560px;border-collapse:collapse;font-size:14.5px}
.tbl th{text-align:left;font-family:var(--font-label);font-size:12px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:0 14px 10px 0;border-bottom:1px solid var(--line2)}
.tbl td{padding:12px 14px 12px 0;border-bottom:1px solid var(--line);vertical-align:top}
.tbl td:first-child{font-weight:600}
.td-cut{white-space:nowrap}
.sell{list-style:none;margin:0;padding:0;display:grid;gap:10px;max-width:760px}
.sell li{position:relative;padding:12px 16px 12px 18px;border-radius:var(--r-item);background:var(--item);box-shadow:var(--item-shadow);font-size:16px;line-height:1.5}
.sell li::before{content:"";position:absolute;left:0;top:12px;bottom:12px;width:3px;border-radius:0 3px 3px 0;background:var(--sa)}
.eps{list-style:none;margin:16px 0 0;padding:0;max-width:820px}
.ep-row{padding:10px 4px 10px 16px;border-top:1px solid var(--line)}
.ep-row:last-child{border-bottom:1px solid var(--line)}
.ep-in{box-shadow:inset 3px 0 0 var(--ok)}.ep-out{box-shadow:inset 3px 0 0 var(--risk)}
.ep-line{display:flex;align-items:center;gap:10px;min-width:0}
.ep-line .pill{flex:none;min-width:44px;justify-content:center}
.ep-name{font-size:15px;font-weight:600;line-height:1.35;min-width:0}
.ep-line>.t,.ep-line>.nw{margin-left:auto;flex:none}
.ep-note{margin:3px 0 0;font-size:13px;line-height:1.45;color:var(--muted);max-width:70ch}
.opps{list-style:none;margin:clamp(20px,3vw,28px) 0 0;padding:0;display:grid;gap:12px;max-width:820px}
.opps li{display:grid;grid-template-columns:36px minmax(0,1fr);gap:14px}
.opp-n{font-family:var(--font-label);font-size:13px;font-weight:600;color:var(--sa);padding-top:1px}

/* disclosure */
.disc{margin-top:clamp(28px,4vw,40px)}
.disc>summary{display:flex;align-items:center;gap:12px;cursor:pointer;list-style:none;font-family:var(--font-label);font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding:12px 2px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.disc>summary::-webkit-details-marker{display:none}
.disc>summary::before{content:"";width:7px;height:7px;flex:none;border-right:2px solid var(--sa);border-bottom:2px solid var(--sa);transform:rotate(-45deg);transition:transform .15s;margin:0 2px}
.disc[open]>summary::before{transform:rotate(45deg)}
.disc>summary:hover{color:var(--text)}
.disc>summary:focus-visible{outline:2px solid var(--sa);outline-offset:2px}
.disc .count{margin-left:auto;color:var(--faint);font-weight:500}
.disc-body{padding-top:20px}

/* extra sections (trusted HTML) */
.extra{margin-top:clamp(20px,3vw,28px);overflow-x:auto}
.extra p{max-width:70ch;margin:0 0 12px}
.extra .lead{font-size:17px;line-height:1.55;color:var(--muted);margin:0 0 22px;max-width:66ch}
.extra .eyebrow,.extra .label,.extra [class~="eyebrow"]{display:block;margin:0 0 6px;font-family:var(--font-label);font-size:12px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.extra .grid2,.extra .grid3,.extra .grid4{display:grid;gap:14px;margin:0 0 22px}
.extra .grid2{grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr))}
.extra .grid3{grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))}
.extra .grid4{grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr))}
.extra .tile,.extra .note,.extra .panel{background:var(--item);border-radius:var(--r-item);padding:16px 18px;box-shadow:var(--item-shadow);min-width:0}
.extra .tile b,.extra .tile strong{display:block;font-size:17px;font-weight:600;line-height:1.3;margin:0 0 6px}
.extra .tile p,.extra .panel p,.extra .note p{font-size:14.5px;line-height:1.5;margin:0;color:var(--text)}
.extra .tile.own{box-shadow:inset 0 0 0 1px var(--sa)}
.extra .note{margin:0 0 22px;box-shadow:inset 3px 0 0 var(--sa)}
.extra ul,.extra ol{list-style:none;margin:0 0 18px;padding:0;display:grid;gap:8px}
.extra li{position:relative;padding-left:18px;line-height:1.5;font-size:15px}
.extra li::before{content:"";position:absolute;left:2px;top:.62em;width:6px;height:6px;border-radius:2px;background:var(--sa)}
.extra .panel ul{margin:0}
.extra code{font-family:var(--font-label);font-size:12px;padding:1px 6px;border-radius:6px;background:var(--chip-bg);color:var(--muted);white-space:nowrap}
.extra table{width:100%;min-width:560px;border-collapse:collapse;font-size:14.5px;margin:0 0 22px}
.extra th{text-align:left;font-family:var(--font-label);font-size:12px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:0 14px 10px 0;border-bottom:1px solid var(--line2)}
.extra td{padding:11px 14px 11px 0;border-bottom:1px solid var(--line);vertical-align:top}
.extra .foot{padding:0;margin:4px 0 0;font-size:13px;color:var(--muted)}
.extra b,.extra strong{font-weight:600}

/* prev / next, feedback, notes, footer */
.pn{display:flex;justify-content:space-between;gap:12px;margin-top:clamp(28px,4vw,40px);padding-top:14px;border-top:1px solid var(--line)}
.pn-a{display:flex;flex-direction:column;gap:2px;min-width:0;max-width:48%;padding:8px 12px;margin:0 -12px;border-radius:var(--r-item);text-decoration:none;color:var(--text)}
.pn-a:hover{background:var(--sa-soft)}
.pn-n{text-align:right;margin-left:auto}
.pn-k{font-family:var(--font-label);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.pn-t{font-size:15px;font-weight:600;color:var(--sa)}
.fb{display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px;margin:clamp(28px,4vw,40px) 0 0;padding:22px 0 0;border-top:1px solid var(--line)}
.fb-q{margin:0;font-weight:600}
.fb-b{display:flex;gap:8px}
.fb button{font:inherit;font-size:14px;font-weight:500;padding:6px 18px;border-radius:999px;border:1px solid var(--line2);background:var(--item);color:var(--text);cursor:pointer}
.fb button:hover{border-color:var(--accent-text)}
.fb button[aria-pressed="true"]{background:var(--accent-soft);border-color:var(--accent-text)}
.fb-thanks{margin:0;color:var(--muted);font-size:14px}
.notes{margin:0;padding-left:20px;color:var(--muted);display:grid;gap:6px;max-width:80ch;font-size:15px}
.method{margin:22px 0 0;font-size:13px;line-height:1.55;color:var(--faint);max-width:90ch}
.foot{padding-top:28px;padding-bottom:48px;font-size:12.5px;color:var(--faint)}
.foot p{margin:0}

/* mini player */
.player{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--player-bg);-webkit-backdrop-filter:saturate(1.3) blur(14px);backdrop-filter:saturate(1.3) blur(14px);border-top:1px solid var(--player-line);padding-bottom:env(safe-area-inset-bottom,0px)}
.pl-in{display:flex;align-items:center;gap:14px;height:64px}
.pl-btn{flex:none;width:40px;height:40px;border-radius:50%;border:0;display:grid;place-items:center;background:var(--accent-text);color:var(--accent-ink);cursor:pointer;padding:0}
.pl-btn:focus-visible,.pl-wave:focus-visible{outline:2px solid var(--accent-text);outline-offset:2px}
.pl-ic{width:18px;height:18px}.pl-ic path{fill:currentColor}
.pl-pause{display:none}.player.playing .pl-play{display:none}.player.playing .pl-pause{display:inline}
.pl-meta{display:flex;flex-direction:column;min-width:0;flex:0 1 220px;line-height:1.3}
.pl-title{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pl-sub{font-size:12.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pl-wave{flex:1 1 auto;min-width:72px;height:36px;cursor:pointer;border-radius:6px}
.pl-wave svg{display:block;width:100%;height:100%}
.wv-b{fill:var(--wave)}.wv-p{fill:var(--wave-on)}
.pl-time{flex:none;font-family:var(--font-label);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.player{transition:transform .25s ease}
.player.away{transform:translateY(110%)}
.pl-msg{display:none;flex:none;font-size:13px;font-weight:600;color:var(--risk)}
.player.err .pl-time{display:none}.player.err .pl-msg{display:inline}
.pl-btn:disabled{opacity:.4;cursor:not-allowed}
@media (max-width:560px){.pl-in{gap:10px}.pl-meta{flex:1 1 0}.pl-sub,.pl-sep,#pl-dur{display:none}.pl-wave{flex:0 0 34%}}

@media (max-width:560px){
  body{font-size:15.5px}
  .item{padding:14px 15px}
  .lines li{grid-template-columns:60px minmax(0,1fr);gap:12px}
  .score{padding:18px}
  .mbars li{grid-template-columns:minmax(0,96px) minmax(0,1fr) 40px;gap:10px}
  .spec div{grid-template-columns:80px minmax(0,1fr);gap:10px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""

# ---------------------------------------------------------------------------
# Inline script: charts, play pills, mini player, nav, index, feedback
# ---------------------------------------------------------------------------

JS = r"""
(function () {
  'use strict';
  var node = document.getElementById('report-data');
  var D = {};
  try { D = JSON.parse(node ? node.textContent : '{}') || {}; } catch (err) { D = {}; }
  var M = D.m || {}, R = D.r || {};
  var E = (M.energy_curve || []).map(Number).filter(function (v) { return isFinite(v); });
  var DUR = Number(M.duration_seconds) || E.length;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function r1(n) { return Math.round(n * 10) / 10; }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function fin(v) { return typeof v === 'number' && isFinite(v); }
  function mmss(t) { t = Math.max(0, Math.floor(Number(t) + 1e-6)); var s = t % 60; return Math.floor(t / 60) + ':' + (s < 10 ? '0' : '') + s; }
  function cap(s) { s = String(s || '').replace(/_/g, ' '); return s.charAt(0).toUpperCase() + s.slice(1); }
  function T(x, y, s, cls, more) { return '<text x="' + r1(x) + '" y="' + r1(y) + '" class="' + cls + '"' + (more || '') + '>' + esc(s) + '</text>'; }
  function LN(x1, y1, x2, y2, cls) { return '<line x1="' + r1(x1) + '" y1="' + r1(y1) + '" x2="' + r1(x2) + '" y2="' + r1(y2) + '" class="' + cls + '"/>'; }
  function RC(x, y, w, h, cls, rx) { return '<rect x="' + r1(x) + '" y="' + r1(y) + '" width="' + r1(Math.max(0, w)) + '" height="' + r1(Math.max(0, h)) + '"' + (rx ? ' rx="' + r1(rx) + '"' : '') + ' class="' + cls + '"/>'; }
  function svg(w, h, inner, label) { return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + r1(w) + ' ' + r1(h) + '" width="' + r1(w) + '" height="' + r1(h) + '" role="img" aria-label="' + esc(label) + '">' + inner + '</svg>'; }
  function put(id, h) { var el = document.getElementById(id); if (el) el.innerHTML = h; }
  function na(id, msg) { put(id, '<p class="na">' + esc(msg) + '</p>'); }
  function hostWidth(host, min) { return Math.max(Math.floor(host.getBoundingClientRect().width) || 0, min || 0); }
  function smooth(a, w) {
    var h = Math.floor(w / 2), out = [];
    for (var i = 0; i < a.length; i++) { var s = 0, n = 0; for (var j = i - h; j <= i + h; j++) { if (j >= 0 && j < a.length) { s += a[j]; n++; } } out.push(s / n); }
    return out;
  }
  function eAt(arr, t) { return arr.length ? arr[clamp(Math.floor(t), 0, arr.length - 1)] : 0; }
  function curve(arr, X, Y, yB) {
    var pts = [[X(0), Y(arr[0])]];
    arr.forEach(function (v, i) { pts.push([X(Math.min(DUR, i + 0.5)), Y(v)]); });
    pts.push([X(DUR), Y(arr[arr.length - 1])]);
    var line = 'M' + pts.map(function (p) { return r1(p[0]) + ' ' + r1(p[1]); }).join(' L');
    return { line: line, area: line + ' L' + r1(X(DUR)) + ' ' + r1(yB) + ' L' + r1(X(0)) + ' ' + r1(yB) + ' Z' };
  }

  // ---- Text measurement with the real fonts and classes -----------------
  var meter = null, widths = {};
  function tw(s, cls) {
    s = String(s); var key = cls + '|' + s;
    if (widths[key] != null) return widths[key];
    if (!meter) {
      var box = document.createElement('div');
      box.className = 'chart measure'; box.setAttribute('aria-hidden', 'true');
      box.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><text></text></svg>';
      document.body.appendChild(box); meter = box.querySelector('text');
    }
    meter.setAttribute('class', cls); meter.textContent = s;
    var w = 0; try { w = meter.getComputedTextLength(); } catch (err) { w = 0; }
    if (!w) w = s.length * 7.2;
    return (widths[key] = w);
  }
  function wrapW(s, cls, maxW, maxLines) {
    var words = String(s || '').split(/\s+/).filter(Boolean), lines = [], cur = '';
    words.forEach(function (w) { var next = cur ? cur + ' ' + w : w; if (!cur || tw(next, cls) <= maxW) cur = next; else { lines.push(cur); cur = w; } });
    if (cur) lines.push(cur);
    if (lines.length > maxLines) { lines = lines.slice(0, maxLines); lines[maxLines - 1] += '\u2026'; }
    return lines.map(function (l) {
      if (tw(l, cls) <= maxW) return l;
      var base = l.replace(/\u2026$/, '');
      while (base.length > 1 && tw(base + '\u2026', cls) > maxW) base = base.slice(0, -1);
      return base.replace(/\s+$/, '') + '\u2026';
    });
  }

  // ---- Label lanes with leaders that never cross another label ------------
  // Each item: {x, variants:[{name, tm}]}. Lane 0 sits nearest the plot; a label in lane L has a
  // leader at x through lanes 0..L-1, so no lower-lane label may cover x, and no higher-lane leader
  // may pass through this label. Items that cannot be placed keep their marker and tooltip only.
  function labelWidth(v, nameCls, tmCls) { return (v.name ? tw(v.name, nameCls) + tw('\u00a0', nameCls) : 0) + tw(v.tm, tmCls); }
  function place(items, maxLanes, xmin, xmax, nameCls, tmCls) {
    var placed = [], pad = 7;
    function clear(x0, x1, lane, x) {
      for (var i = 0; i < placed.length; i++) {
        var p = placed[i];
        if (p.lane === lane && x0 < p.x1 + pad && x1 > p.x0 - pad) return false;
        if (p.lane > lane && p.x > x0 - pad && p.x < x1 + pad) return false;
        if (p.lane < lane && x > p.x0 - pad && x < p.x1 + pad) return false;
      }
      return true;
    }
    // Higher-priority labels (lower prio) claim space first; then left to right.
    var order = items.slice().sort(function (a, b) { return ((a.prio || 0) - (b.prio || 0)) || (a.x - b.x); });
    order.forEach(function (it, idx) {
      // Cheapest valid spot: full label before short, then cover as few later markers as
      // possible (their leaders would be blocked), then the lowest lane.
      var best = null;
      it.lane = -1;
      for (var v = 0; v < it.variants.length; v++) {
        var va = it.variants[v], w = labelWidth(va, it.nameCls || nameCls, it.tmCls || tmCls);
        var opts = [['start', it.x - 3, it.x - 3 + w], ['end', it.x + 3 - w, it.x + 3], ['middle', it.x - w / 2, it.x + w / 2]];
        for (var lane = 0; lane < maxLanes; lane++) {
          for (var o = 0; o < opts.length; o++) {
            var x0 = opts[o][1], x1 = opts[o][2];
            if (x0 < xmin || x1 > xmax || !clear(x0, x1, lane, it.x)) continue;
            var covered = 0;
            for (var k = idx + 1; k < order.length; k++) { if (order[k].x > x0 - pad && order[k].x < x1 + pad) covered++; }
            var cost = v * 1000 + covered * 100 + lane * 10 + o;
            if (!best || cost < best.cost) best = { cost: cost, lane: lane, anchor: opts[o][0], x0: x0, x1: x1, v: va };
          }
        }
      }
      if (best) { it.lane = best.lane; it.anchor = best.anchor; it.x0 = best.x0; it.x1 = best.x1; it.v = best.v; placed.push(it); }
    });
    var used = 0; placed.forEach(function (p) { used = Math.max(used, p.lane + 1); });
    return used;
  }
  function labelSvg(it, y, nameCls, tmCls) {
    var tx = it.anchor === 'start' ? it.x - 3 : it.anchor === 'end' ? it.x + 3 : it.x;
    var a = it.anchor === 'start' ? '' : ' text-anchor="' + it.anchor + '"';
    var inner = it.v.name ? esc(it.v.name) + '\u00a0<tspan class="' + (it.tmCls || tmCls) + '">' + esc(it.v.tm) + '</tspan>' : esc(it.v.tm);
    return '<text x="' + r1(tx) + '" y="' + r1(y) + '" class="' + (it.v.name ? (it.nameCls || nameCls) : (it.tmCls || tmCls)) + ' halo"' + a + '>' + inner + '</text>';
  }
  // Simple lanes for labels without leaders (section names under the song map).
  function lanes(items, max) {
    var ends = [], used = 0;
    items.slice().sort(function (a, b) { return a.x0 - b.x0; }).forEach(function (it) {
      var lane = -1, i;
      for (i = 0; i < max; i++) { if (ends[i] === undefined || ends[i] <= it.x0) { lane = i; break; } }
      if (lane < 0) { lane = 0; for (i = 1; i < max; i++) { if (ends[i] < ends[lane]) lane = i; } }
      it.lane = lane; ends[lane] = it.x1 + 8; used = Math.max(used, lane + 1);
    });
    return used;
  }
  function yAxis(g, ml, W, mr, Y, top, yB, noTitle) {
    [25, 50, 75, 100].forEach(function (v) { g.push(LN(ml, Y(v), W - mr, Y(v), 'gl')); });
    [0, 50, 100].forEach(function (v) { g.push(T(ml - 6, Y(v) + 4, String(v), 'ax', ' text-anchor="end"')); });
    if (noTitle) return;
    var mid = (top + yB) / 2;
    g.push(T(16, mid, 'ENERGY', 'ax-t', ' text-anchor="middle" transform="rotate(-90 16 ' + r1(mid) + ')"'));
  }
  var ABBR = { intro: 'Intro', verse: 'V', chorus: 'Ch', bridge: 'Br', outro: 'Out', pre_chorus: 'Pre', 'pre-chorus': 'Pre', breakdown: 'Bd', instrumental: 'Inst', interlude: 'Int', hook: 'Hook', post_chorus: 'Post' };

  // ---- Song map: energy curve, sections, moments, drops -------------------
  function drawSongMap() {
    var id = 'ch-songmap', host = document.getElementById(id);
    if (!host) return;
    if (!E.length || !DUR) return na(id, 'No energy curve in this measurement.');
    // Drawn at the panel's own width; on a phone the margins shrink and section names abbreviate.
    var W = hostWidth(host, 0), narrow = W < 600, ml = narrow ? 30 : 50, mr = narrow ? 8 : 18, PH = narrow ? 150 : 180, laneH = 19;
    var X = function (t) { return ml + clamp(t, 0, DUR) / DUR * (W - ml - mr); };
    var ES = smooth(E, 5);
    var items = (M.moments || []).filter(function (m) { return fin(m.start); }).map(function (m) {
      var tm = m.mmss || mmss(m.start), name = cap(m.type);
      var prio = { vocal_hook: 0, climax: 1, chorus_lift: 1, drop: 1 }[m.type];
      return { kind: 'mo', m: m, x: X(m.start), prio: prio == null ? 2 : prio, variants: [{ name: name, tm: tm }, { name: name.split(' ')[0], tm: tm }, { name: '', tm: tm }] };
    });
    (M.mute_drops || []).forEach(function (d) {
      if (d.type !== 'breakdown' || !fin(d.start)) return;
      var x0 = X(d.start), x1 = X(fin(d.end) ? d.end : d.start + 2), tm = d.mmss || mmss(d.start);
      items.push({ kind: 'bd', d: d, x: (x0 + x1) / 2, bx0: x0, bx1: x1, prio: 3, nameCls: 'lab lab-bd', variants: [{ name: 'Breakdown', tm: tm }, { name: '', tm: tm }] });
    });
    var nTop = place(items, narrow ? 4 : 3, 4, W - 4, 'lab', 'lab-tm');
    host.setAttribute('data-unlabelled', String(items.filter(function (i) { return i.lane < 0; }).length));
    var top = 14 + Math.max(1, nTop) * laneH + 8, yB = top + PH;
    var Y = function (v) { return yB - clamp(v, 0, 100) / 100 * PH; };
    var secs = (M.sections || []).filter(function (s) { return fin(s.start); });
    var labs = secs.map(function (s) {
      var key = String(s.label || '').toLowerCase(), full = cap(s.label);
      var name = narrow ? (ABBR[key] || full.slice(0, 3)) : full, tm = s.mmss || mmss(s.start);
      var x = X(s.start) + (narrow ? 3 : 6), w = Math.max(tw(name, 'sec-l'), tw(tm, 'sec-t'));
      return { kind: 'sec', name: name, full: full, tm: tm, x: x, x0: x - 2, x1: x + w + 2 };
    });
    var nSec = lanes(labs, narrow ? 4 : 3);
    var endTm = mmss(DUR), endX0 = X(DUR) - tw(endTm, 'sec-t') - 2;
    if (!labs.some(function (it) { return it.lane === 0 && it.x1 + 6 > endX0; })) labs.push({ kind: 'end', tm: endTm, x: X(DUR), lane: 0 });
    var H = yB + 14 + Math.max(1, nSec) * 34;
    var g = [];
    secs.forEach(function (s, i) { g.push(RC(X(s.start), top, X(fin(s.end) ? s.end : DUR) - X(s.start), PH, i % 2 ? 'sb-b' : 'sb-a')); });
    yAxis(g, ml, W, mr, Y, top, yB, narrow);
    items.forEach(function (it) {
      if (it.kind !== 'bd') return;
      var d = it.d;
      g.push('<g class="seek" data-t="' + Math.floor(d.start) + '"><title>' + esc('Breakdown ' + (d.mmss || mmss(d.start)) + (fin(d.depth_db) ? ' \u00b7 ' + d.depth_db + ' dB' : '') + (fin(d.end) ? ' for ' + r1(d.end - d.start) + ' s' : '')) + '</title>' + RC(it.bx0, top, Math.max(2, it.bx1 - it.bx0), PH, 'bd') + '</g>');
    });
    var raw = curve(E, X, Y, yB), sm = curve(ES, X, Y, yB);
    g.push('<path d="' + sm.area + '" class="e-area"/><path d="' + raw.line + '" class="e-raw"/><path d="' + sm.line + '" class="e-line"/>');
    g.push(LN(ml, yB, W - mr, yB, 'base'));
    (M.mute_drops || []).forEach(function (d) {
      if (d.type === 'breakdown' || !fin(d.start)) return;
      var x = X(d.start);
      g.push('<g class="seek" data-t="' + Math.floor(d.start) + '"><title>' + esc('Mute drop ' + (d.mmss || mmss(d.start)) + (fin(d.depth_db) ? ' \u00b7 ' + d.depth_db + ' dB' : '') + (fin(d.beats) ? ' for ' + d.beats + ' beats' : '')) + '</title>' +
        LN(x, top + 9, x, yB, 'mute-l') + '<polygon points="' + r1(x - 5) + ',' + r1(top) + ' ' + r1(x + 5) + ',' + r1(top) + ' ' + r1(x) + ',' + r1(top + 8) + '" class="mute-t"/></g>');
    });
    secs.forEach(function (s, i) { if (i > 0) g.push(LN(X(s.start), top, X(s.start), yB + 6, 'sec-div')); });
    labs.forEach(function (it) {
      var y = yB + 22 + it.lane * 34;
      if (it.kind === 'end') { g.push(T(it.x, y + 15, it.tm, 'sec-t', ' text-anchor="end"')); return; }
      g.push('<g><title>' + esc(it.full + ' ' + it.tm) + '</title>' + T(it.x, y, it.name, 'sec-l') + T(it.x, y + 15, it.tm, 'sec-t') + '</g>');
    });
    items.forEach(function (it) {
      var ly = top - 12 - it.lane * laneH;
      if (it.kind === 'bd') {
        if (it.lane >= 0) g.push('<g class="seek" data-t="' + Math.floor(it.d.start) + '">' + LN(it.x, ly + 5, it.x, top, 'bd-l') + labelSvg(it, ly, 'lab', 'lab-tm') + '</g>');
        return;
      }
      var m = it.m, dy = Y(eAt(ES, m.start));
      var tip = cap(m.type) + ' ' + (m.mmss || mmss(m.start)) + (m.section ? ' \u00b7 ' + m.section : '') + (m.also && m.also.length ? ' \u00b7 also ' + m.also.join(', ').replace(/_/g, ' ') : '');
      g.push('<g class="seek" data-t="' + Math.floor(m.start) + '"><title>' + esc(tip) + '</title>' +
        (it.lane >= 0 ? LN(it.x, ly + 5, it.x, dy - 8, 'mo-lead') : '') +
        '<polygon points="' + r1(it.x) + ',' + r1(dy - 6.5) + ' ' + r1(it.x + 6.5) + ',' + r1(dy) + ' ' + r1(it.x) + ',' + r1(dy + 6.5) + ' ' + r1(it.x - 6.5) + ',' + r1(dy) + '" class="mo-d"/>' +
        (it.lane >= 0 ? labelSvg(it, ly, 'lab', 'lab-tm') : '') + '</g>');
    });
    put(id, svg(W, H, g.join(''), 'Song map: measured energy per second with sections, moments and drops'));
  }

  // ---- Edit points: energy line with In / Out markers ---------------------
  function drawEdits() {
    var id = 'ch-edits', host = document.getElementById(id);
    if (!host) return;
    if (!E.length || !DUR) return na(id, 'No energy curve in this measurement.');
    var W = hostWidth(host, 880), ml = 50, mr = 18, PH = 150, laneH = 19;
    var X = function (t) { return ml + clamp(t, 0, DUR) / DUR * (W - ml - mr); };
    var ES = smooth(E, 5), seen = {}, marks = [];
    (R.edit_points || []).forEach(function (e) {
      if (!fin(e.t)) return;
      var key = e.type + '@' + Math.round(e.t);
      if (seen[key]) return; seen[key] = 1;
      var c = e.type === 'in' ? 'in' : 'out', tm = mmss(e.t);
      marks.push({ e: e, c: c, x: X(e.t), tmCls: 'ep-t ep-t-' + c, variants: [{ name: '', tm: (c === 'in' ? 'In ' : 'Out ') + tm }, { name: '', tm: tm }] });
    });
    var n = place(marks, 5, 4, W - 4, 'ep-t', 'ep-t');
    host.setAttribute('data-unlabelled', String(marks.filter(function (i) { return i.lane < 0; }).length));
    var top = 12 + Math.max(1, n) * laneH + 10, yB = top + PH, H = yB + 32;
    var Y = function (v) { return yB - clamp(v, 0, 100) / 100 * PH; };
    var g = [];
    (M.sections || []).forEach(function (s, i) { if (fin(s.start)) g.push(RC(X(s.start), top, X(fin(s.end) ? s.end : DUR) - X(s.start), PH, i % 2 ? 'sb-b' : 'sb-a')); });
    yAxis(g, ml, W, mr, Y, top, yB);
    var sm = curve(ES, X, Y, yB);
    g.push('<path d="' + sm.area + '" class="ep-area"/><path d="' + sm.line + '" class="ep-line"/>');
    g.push(LN(ml, yB, W - mr, yB, 'base'));
    var step = DUR > 150 ? 30 : DUR > 60 ? 15 : 10;
    for (var t = 0; t <= DUR + 0.01; t += step) {
      var tx = X(t), lab = mmss(t), half = tw(lab, 'ax') / 2;
      g.push(LN(tx, yB, tx, yB + 5, 'tick') + T(clamp(tx, half + 2, W - half - 2), yB + 20, lab, 'ax', ' text-anchor="middle"'));
    }
    marks.forEach(function (it) {
      var dy = Y(eAt(ES, it.e.t)), ly = top - 10 - Math.max(0, it.lane) * laneH;
      g.push('<g class="seek" data-t="' + Math.floor(it.e.t) + '"><title>' + esc((it.c === 'in' ? 'In ' : 'Out ') + mmss(it.e.t) + (it.e.name ? ' \u00b7 ' + it.e.name : '')) + '</title>' +
        LN(it.x, it.lane >= 0 ? ly + 5 : top, it.x, yB, 'ep-l ep-l-' + it.c) +
        '<circle cx="' + r1(it.x) + '" cy="' + r1(dy) + '" r="5" class="ep-c ep-c-' + it.c + '"/>' +
        (it.lane >= 0 ? labelSvg(it, ly, 'ep-t', it.tmCls) : '') + '</g>');
    });
    put(id, svg(W, H, g.join(''), 'Edit points: in and out markers on the measured energy curve'));
  }

  // ---- Frequency balance: seven bands -------------------------------------
  var BAND_NAMES = { sub: 'SUB', low: 'LOW', low_mid: 'LOW-MID', mid: 'MID', high_mid: 'HIGH-MID', high: 'HIGH', air: 'AIR' };
  var BAND_ORDER = ['sub', 'low', 'low_mid', 'mid', 'high_mid', 'high', 'air'];
  function hz(v) { v = Number(v); return v >= 1000 ? r1(v / 1000) + ' kHz' : Math.round(v) + ' Hz'; }
  function drawBands() {
    var id = 'ch-bands', host = document.getElementById(id);
    if (!host) return;
    var B = (M.band_profile || []).slice().sort(function (a, b) {
      var ia = BAND_ORDER.indexOf(a.band), ib = BAND_ORDER.indexOf(b.band);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    if (!B.length) return na(id, 'No band profile in this measurement.');
    var W = hostWidth(host, 820), n = B.length, cw = W / n, PH = 170, ann = R.bands || {}, g = [];
    var rows = B.map(function (b) { return { lv: clamp(Number(b.level_pct) || 0, 0, 100), lines: wrapW(ann[b.band] || '', 'bar-a', cw - 14, 3) }; });
    var TOP = 16;
    rows.forEach(function (it) {
      var above = it.lines.length ? 26 + (it.lines.length - 1) * 15 + 11 : 19;
      TOP = Math.max(TOP, 6 + above - PH * (1 - it.lv / 100));
    });
    TOP = Math.ceil(TOP);
    var yB = TOP + PH, H = yB + 60;
    [25, 50, 75, 100].forEach(function (v) { g.push(LN(0, yB - v / 100 * PH, W, yB - v / 100 * PH, 'gl')); });
    B.forEach(function (b, i) {
      var cx = cw * i + cw / 2, bw = Math.min(56, cw * 0.46), lv = rows[i].lv, h = lv / 100 * PH, y = yB - h;
      var st = String(b.status || 'clear').toLowerCase(), name = BAND_NAMES[b.band] || String(b.band || '').toUpperCase();
      g.push('<g><title>' + esc(name + ' ' + hz(b.lo_hz) + '\u2013' + hz(b.hi_hz) + ' \u00b7 level ' + lv + ' \u00b7 ' + r1(Number(b.share_pct) || 0) + '% of energy \u00b7 ' + st) + '</title>' +
        RC(cx - bw / 2, TOP, bw, PH, 'bar-track', 6) + (h > 0 ? RC(cx - bw / 2, y, bw, Math.max(h, 2), 'bar-' + st, Math.min(6, h / 2)) : '') + '</g>');
      g.push(T(cx, y - 8, String(Math.round(lv)), 'bar-v', ' text-anchor="middle"'));
      var lines = rows[i].lines;
      lines.forEach(function (ln, j) { g.push(T(cx, y - 26 - (lines.length - 1 - j) * 15, ln, 'bar-a', ' text-anchor="middle"')); });
      g.push(T(cx, yB + 20, name, 'bar-n', ' text-anchor="middle"'));
      g.push(T(cx, yB + 36, hz(b.lo_hz), 'bar-hz', ' text-anchor="middle"'));
      g.push(T(cx, yB + 52, r1(Number(b.share_pct) || 0) + '% energy', 'bar-s', ' text-anchor="middle"'));
    });
    g.push(LN(0, yB, W, yB, 'base'));
    put(id, svg(W, H, g.join(''), 'Frequency balance: measured level per band, with what lives in each band'));
  }

  // ---- Emotional position: valence x arousal -----------------------------
  function arrowRight(x1, x2, y) { return LN(x1, y, x2, y, 'ax-ar') + '<polygon points="' + r1(x2) + ',' + r1(y - 3.5) + ' ' + r1(x2 + 7) + ',' + r1(y) + ' ' + r1(x2) + ',' + r1(y + 3.5) + '" class="ax-hd"/>'; }
  function arrowUp(x, y1, y2) { return LN(x, y1, x, y2, 'ax-ar') + '<polygon points="' + r1(x - 3.5) + ',' + r1(y2) + ' ' + r1(x + 3.5) + ',' + r1(y2) + ' ' + r1(x) + ',' + r1(y2 - 7) + '" class="ax-hd"/>'; }
  function drawEmotion() {
    var id = 'ch-emotion', host = document.getElementById(id), e = R.emo || {};
    if (!host) return;
    if (!fin(e.v) || !fin(e.a)) return na(id, 'No valence or arousal reading.');
    var W = clamp(hostWidth(host), 260, 380), x0 = 46, y0 = 10, P = W - x0 - 12, H = y0 + P + 38;
    var X = function (v) { return x0 + clamp(v, 0, 1) * P; }, Y = function (a) { return y0 + (1 - clamp(a, 0, 1)) * P; };
    var g = [RC(x0, y0, P, P, 'emo-bg', 12)];
    [0.25, 0.75].forEach(function (f) { g.push(LN(x0 + f * P, y0, x0 + f * P, y0 + P, 'gl') + LN(x0, y0 + f * P, x0 + P, y0 + f * P, 'gl')); });
    g.push(LN(x0 + P / 2, y0, x0 + P / 2, y0 + P, 'emo-mid') + LN(x0, y0 + P / 2, x0 + P, y0 + P / 2, 'emo-mid'));
    var q = P / 2 - 20;
    g.push(T(x0 + 10, y0 + 22, wrapW('Tense \u00b7 Angry', 'emo-qt', q, 1)[0], 'emo-qt') + T(x0 + P - 10, y0 + 22, wrapW('Joyful \u00b7 Excited', 'emo-qt', q, 1)[0], 'emo-qt', ' text-anchor="end"'));
    g.push(T(x0 + 10, y0 + P - 12, wrapW('Sad \u00b7 Low', 'emo-qt', q, 1)[0], 'emo-qt') + T(x0 + P - 10, y0 + P - 12, wrapW('Serene \u00b7 Content', 'emo-qt', q, 1)[0], 'emo-qt', ' text-anchor="end"'));
    var by = y0 + P + 26, wn = tw('Negative', 'ax-e'), wp = tw('Positive', 'ax-e');
    g.push(T(x0, by, 'Negative', 'ax-e') + T(x0 + P, by, 'Positive', 'ax-e', ' text-anchor="end"'));
    if (P - wn - wp > 60) g.push(arrowRight(x0 + wn + 12, x0 + P - wp - 20, by - 4));
    var lx = 26, wc = tw('Calm', 'ax-e'), we = tw('Energetic', 'ax-e');
    g.push(T(lx, y0 + P, 'Calm', 'ax-e', ' transform="rotate(-90 ' + lx + ' ' + (y0 + P) + ')"'));
    g.push(T(lx, y0, 'Energetic', 'ax-e', ' text-anchor="end" transform="rotate(-90 ' + lx + ' ' + y0 + ')"'));
    if (P - wc - we > 60) g.push(arrowUp(lx - 4, y0 + P - wc - 12, y0 + we + 20));
    var px = X(e.v), py = Y(e.a);
    g.push(LN(px, py, px, y0 + P, 'emo-guide') + LN(x0, py, px, py, 'emo-guide'));
    g.push('<circle cx="' + r1(px) + '" cy="' + r1(py) + '" r="15" class="emo-halo"/><circle cx="' + r1(px) + '" cy="' + r1(py) + '" r="6.5" class="emo-pt"/>');
    var right = px < x0 + P * 0.58, tx = right ? px + 18 : px - 18, anchor = right ? '' : ' text-anchor="end"';
    var lines = wrapW(e.label || '', 'emo-l', right ? x0 + P - 6 - tx : tx - x0 - 6, 2);
    var ty = clamp(py - 3 - (lines.length - 1) * 8, y0 + 36, y0 + P - 28 - lines.length * 16);
    lines.forEach(function (ln, j) { g.push(T(tx, ty + j * 16, ln, 'emo-l halo', anchor)); });
    g.push(T(tx, ty + lines.length * 16, 'V ' + e.v.toFixed(2) + ' \u00b7 A ' + e.a.toFixed(2), 'emo-v halo', anchor));
    put(id, svg(W, H, g.join(''), 'Emotional position: valence ' + e.v.toFixed(2) + ', arousal ' + e.a.toFixed(2) + (e.label ? ', ' + e.label : '')));
  }

  // ---- Radar (mood profile, sonic fingerprint) ----------------------------
  function radar(id, axes, label) {
    var host = document.getElementById(id);
    if (!host) return;
    if (!axes.length) return na(id, 'No data.');
    var W = clamp(hostWidth(host), 260, 440), n = axes.length, room = 0;
    axes.forEach(function (ax) { room = Math.max(room, Math.min(tw(ax.label, 'rd-l'), 104)); });
    var r = clamp((W - 2 * (room + 22)) / 2, 52, 104), cx = W / 2, cy = r + 54, H = 2 * r + 112;
    function pt(i, f) { var a = -Math.PI / 2 + i * 2 * Math.PI / n; return [cx + Math.cos(a) * r * f, cy + Math.sin(a) * r * f, a]; }
    function poly(f) { var s = []; for (var i = 0; i < n; i++) { var p = pt(i, f); s.push(r1(p[0]) + ',' + r1(p[1])); } return s.join(' '); }
    var g = [];
    [0.25, 0.5, 0.75, 1].forEach(function (f) { g.push('<polygon points="' + poly(f) + '" class="rd-ring' + (f === 1 ? ' rd-outer' : '') + '"/>'); });
    for (var i = 0; i < n; i++) { var p = pt(i, 1); g.push(LN(cx, cy, p[0], p[1], 'rd-spoke')); }
    g.push('<polygon points="' + axes.map(function (ax, k) { var q = pt(k, clamp(ax.v, 0, 1)); return r1(q[0]) + ',' + r1(q[1]); }).join(' ') + '" class="rd-shape"/>');
    axes.forEach(function (ax, k) { var q = pt(k, clamp(ax.v, 0, 1)); g.push('<circle cx="' + r1(q[0]) + '" cy="' + r1(q[1]) + '" r="3.5" class="rd-dot"/>'); });
    axes.forEach(function (ax, k) {
      var q = pt(k, 1), c = Math.cos(q[2]), s = Math.sin(q[2]);
      var lx = cx + c * (r + 14), ly = cy + s * (r + 14);
      var anchor = c > 0.3 ? 'start' : c < -0.3 ? 'end' : 'middle';
      var avail = anchor === 'start' ? W - lx - 4 : anchor === 'end' ? lx - 4 : 2 * Math.min(lx, W - lx) - 8;
      var lines = wrapW(ax.label, 'rd-l', avail, 2);
      var block = lines.length * 15 + 15, y;
      if (s < -0.6) y = ly - block + 12; else if (s > 0.6) y = ly + 12; else y = ly - block / 2 + 11;
      lines.forEach(function (ln, j) { g.push(T(lx, y + j * 15, ln, 'rd-l', ' text-anchor="' + anchor + '"')); });
      g.push(T(lx, y + lines.length * 15, ax.sub, 'rd-s', ' text-anchor="' + anchor + '"'));
    });
    put(id, svg(W, H, g.join(''), label));
  }

  function safe(fn) { try { fn(); } catch (err) { if (window.console) console.error(err); } }
  function drawAll() {
    safe(drawEmotion);
    safe(function () {
      radar('ch-mood', (R.moods || []).filter(function (x) { return fin(x.pct); }).map(function (x) {
        return { label: x.tag, sub: Math.round(x.pct) + '%', v: x.pct / 100 };
      }), 'Mood profile');
    });
    safe(function () {
      var fp = M.fingerprint || {}, axes = [['organic_electronic', 'Electronic'], ['sparse_dense', 'Dense'], ['dark_bright', 'Bright'], ['intimate_anthemic', 'Anthemic'], ['smooth_textured', 'Textured'], ['slow_fast', 'Fast']];
      radar('ch-fp', axes.filter(function (a) { return fin(fp[a[0]]); }).map(function (a) {
        return { label: a[1], sub: Number(fp[a[0]]).toFixed(2), v: Number(fp[a[0]]) };
      }), 'Sonic fingerprint');
    });
    safe(drawSongMap); safe(drawEdits); safe(drawBands); safe(drawWave);
  }

  // ---- Mini player ---------------------------------------------------------
  var audio = document.querySelector('audio[data-report-player]');
  var bar = document.getElementById('player');
  var wave = document.getElementById('pl-wave');
  function audioDur() { return audio && isFinite(audio.duration) && audio.duration > 0 ? audio.duration : DUR; }
  function drawWave() {
    if (!wave) return;
    var n = 96, W = 960, H = 36, bw = W / n, g = ['<defs><clipPath id="pl-clip"><rect id="pl-prog" x="0" y="0" width="0" height="' + H + '"/></clipPath></defs>'], b = [];
    for (var i = 0; i < n; i++) {
      var v = E.length ? E[Math.min(E.length - 1, Math.floor(i / n * E.length))] : 30;
      var h = Math.max(3, clamp(v, 0, 100) / 100 * (H - 4));
      b.push(RC(i * bw + 1.5, (H - h) / 2, bw - 3, h, '', 1.5).replace(' class=""', ''));
    }
    g.push('<g class="wv-b">' + b.join('') + '</g><g class="wv-p" clip-path="url(#pl-clip)">' + b.join('') + '</g>');
    wave.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" aria-hidden="true">' + g.join('') + '</svg>';
    progress();
  }
  function progress() {
    if (!audio || !wave) return;
    var t = audio.currentTime || 0, d = audioDur(), p = document.getElementById('pl-prog');
    if (p) p.setAttribute('width', String(d ? clamp(t / d, 0, 1) * 960 : 0));
    var cur = document.getElementById('pl-cur'); if (cur) cur.textContent = mmss(t);
    wave.setAttribute('aria-valuenow', String(Math.floor(t))); wave.setAttribute('aria-valuetext', mmss(t));
  }
  var btn = bar ? bar.querySelector('.pl-btn') : null;
  function failed() {
    // The source cannot load: say so, and stop offering a play button that does nothing.
    if (!bar) return;
    bar.classList.add('err'); bar.classList.remove('playing', 'away');
    if (btn) { btn.disabled = true; btn.setAttribute('aria-label', 'Audio unavailable'); }
  }
  function play() {
    if (!audio || (btn && btn.disabled)) return;
    var pr = audio.play();
    if (pr && pr.catch) pr.catch(function () { if (audio.error) failed(); });
  }
  // Seeks wait for metadata. A server without HTTP range support leaves nothing seekable, so the
  // file is then fetched once as a blob (fully seekable); if that fetch is refused, play on.
  var pending = null, wholeTried = false;
  function canSeek(t) {
    var s = audio.seekable;
    for (var i = 0; i < s.length; i++) { if (s.start(i) <= t && s.end(i) >= t) return true; }
    return false;
  }
  function loadWhole() {
    var src = audio.currentSrc || audio.src, wasPlaying = !audio.paused;
    if (wasPlaying) audio.pause();
    fetch(src).then(function (r) { if (!r.ok) throw new Error(String(r.status)); return r.blob(); }).then(function (b) {
      audio.src = URL.createObjectURL(b);
      audio.load();
      if (wasPlaying) play();
    }).catch(function () { var t = pending; pending = null; try { audio.currentTime = t; } catch (err) { /* not seekable */ } });
  }
  function applySeek() {
    if (pending == null || audio.readyState < 1) return;
    if (!canSeek(pending) && pending > 0 && !wholeTried && window.fetch && !/^blob:/.test(audio.currentSrc || '')) {
      wholeTried = true; loadWhole(); return;
    }
    var t = pending; pending = null;
    try { audio.currentTime = t; } catch (err) { /* not seekable */ }
    progress();
  }
  function seekTo(t, andPlay) {
    if (!audio) return;
    pending = t;
    var cur = document.getElementById('pl-cur'); if (cur) cur.textContent = mmss(t);
    if (audio.readyState >= 1) applySeek();
    else if (!andPlay) { audio.preload = 'metadata'; audio.load(); }
    if (andPlay) play();
  }
  if (audio) audio.addEventListener('loadedmetadata', applySeek);
  if (audio && bar) {
    btn.addEventListener('click', function () { if (audio.paused) play(); else audio.pause(); });
    audio.addEventListener('play', function () { bar.classList.add('playing'); bar.classList.remove('away'); btn.setAttribute('aria-label', 'Pause'); });
    audio.addEventListener('pause', function () { bar.classList.remove('playing'); btn.setAttribute('aria-label', 'Play'); });
    audio.addEventListener('timeupdate', progress);
    audio.addEventListener('loadedmetadata', function () { var d = document.getElementById('pl-dur'); if (d) d.textContent = mmss(audioDur()); wave.setAttribute('aria-valuemax', String(Math.floor(audioDur()))); });
    audio.addEventListener('error', failed);
    var src = audio.querySelector('source');
    if (src) src.addEventListener('error', failed);
    // On a phone the bar stays out of the way while the hero (verdict and score) is on screen.
    var heroEl = document.querySelector('.hero');
    if (heroEl && 'IntersectionObserver' in window && window.matchMedia) {
      var phone = window.matchMedia('(max-width: 760px)'), heroIn = true;
      var syncAway = function () { bar.classList.toggle('away', phone.matches && heroIn && audio.paused && !bar.classList.contains('err')); };
      new IntersectionObserver(function (es) { heroIn = es[0].isIntersecting; syncAway(); }).observe(heroEl);
      if (phone.addEventListener) phone.addEventListener('change', syncAway);
      audio.addEventListener('pause', syncAway);
    }
    wave.addEventListener('click', function (ev) { var r = wave.getBoundingClientRect(); seekTo(clamp((ev.clientX - r.left) / r.width, 0, 1) * audioDur(), true); });
    wave.addEventListener('keydown', function (ev) {
      var step = ev.key === 'ArrowRight' ? 5 : ev.key === 'ArrowLeft' ? -5 : 0;
      if (step) { ev.preventDefault(); seekTo(clamp((audio.currentTime || 0) + step, 0, audioDur()), false); }
    });
  }

  // ---- Play pills and chart markers ---------------------------------------
  document.addEventListener('click', function (ev) {
    var el = ev.target && ev.target.closest ? ev.target.closest('button.t, .seek[data-t]') : null;
    if (!el) return;
    var t = Number(el.getAttribute('data-t'));
    if (!isFinite(t)) return;
    var prev = document.querySelectorAll('button.t.on');
    for (var i = 0; i < prev.length; i++) prev[i].classList.remove('on');
    if (el.tagName === 'BUTTON') el.classList.add('on');
    try { el.dispatchEvent(new CustomEvent('report:seek', { detail: { t: t }, bubbles: true })); } catch (err) { /* old browser */ }
    if (window.parent && window.parent !== window) { try { window.parent.postMessage({ type: 'report:seek', t: t }, '*'); } catch (err) { /* cross-origin */ } }
    seekTo(t, true);
  });

  // ---- Feedback (stays on the page) ---------------------------------------
  var fb = document.querySelector('.fb');
  if (fb) fb.addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('button[data-fb]');
    if (!b) return;
    [].forEach.call(fb.querySelectorAll('button[data-fb]'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var th = fb.querySelector('.fb-thanks'); if (th) th.hidden = false;
  });

  // ---- Nav overflow cue, nav + index highlight ----------------------------
  var navEl = document.querySelector('.nav'), strip = navEl && navEl.querySelector('.nav-in');
  function navCue() {
    if (!strip) return;
    var more = strip.scrollLeft + strip.clientWidth < strip.scrollWidth - 4;
    navEl.classList.toggle('more', more);
    navEl.classList.toggle('less', strip.scrollLeft > 4);
  }
  if (strip) {
    strip.addEventListener('scroll', navCue, { passive: true });
    var moreBtn = navEl.querySelector('.nav-more');
    if (moreBtn) moreBtn.addEventListener('click', function () { strip.scrollBy({ left: Math.max(160, strip.clientWidth * 0.6), behavior: 'smooth' }); });
  }
  // Section in view: highlight its nav link and show it (with its subsections) in the index.
  var navLinks = [].slice.call(document.querySelectorAll('.nav a[href^="#"]'));
  var tocSecs = [].slice.call(document.querySelectorAll('.toc-sec'));
  var subLinks = [].slice.call(document.querySelectorAll('.toc-sub a[href^="#"]'));
  if ('IntersectionObserver' in window) {
    var navById = {}, tocById = {}, subById = {};
    navLinks.forEach(function (a) { navById[a.getAttribute('href').slice(1)] = a; });
    tocSecs.forEach(function (li) { tocById[li.getAttribute('data-sec')] = li; });
    subLinks.forEach(function (a) { subById[a.getAttribute('href').slice(1)] = a; });
    var secIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var id = en.target.id;
        if (!en.isIntersecting || !(navById[id] || tocById[id])) return;
        navLinks.forEach(function (x) { x.classList.remove('on'); x.removeAttribute('aria-current'); });
        tocSecs.forEach(function (x) { x.classList.toggle('cur', x === tocById[id]); });
        var a = navById[id];
        if (a) {
          a.classList.add('on'); a.setAttribute('aria-current', 'true');
          if (strip) {
            var l = a.offsetLeft - strip.offsetLeft, rr = l + a.offsetWidth;
            if (l < strip.scrollLeft + 24) strip.scrollLeft = Math.max(0, l - 24);
            else if (rr > strip.scrollLeft + strip.clientWidth - 48) strip.scrollLeft = rr - strip.clientWidth + 48;
          }
        }
        navCue();
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(navById).concat(Object.keys(tocById)).forEach(function (k) { var el = document.getElementById(k); if (el) secIO.observe(el); });
    var subIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var a = subById[en.target.id];
        if (!en.isIntersecting || !a) return;
        subLinks.forEach(function (x) { x.classList.toggle('on', x === a); });
      });
    }, { rootMargin: '-15% 0px -70% 0px' });
    Object.keys(subById).forEach(function (k) { var el = document.getElementById(k); if (el) subIO.observe(el); });
  }

  // Toggles whose label changes while open ("Show method notes" / "Hide method notes").
  document.addEventListener('toggle', function (ev) {
    var d = ev.target;
    if (!d || d.tagName !== 'DETAILS') return;
    var l = d.querySelector(':scope > summary .disc-l');
    if (l && l.getAttribute('data-open')) l.textContent = l.getAttribute(d.open ? 'data-open' : 'data-closed');
  }, true);

  drawAll();
  navCue();
  var lastW = window.innerWidth, timer = null;
  window.addEventListener('resize', function () {
    clearTimeout(timer);
    timer = setTimeout(function () { navCue(); if (window.innerWidth !== lastW) { lastW = window.innerWidth; drawAll(); } }, 150);
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { widths = {}; drawAll(); navCue(); });
})();
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a song analyst report to one self-contained HTML page.")
    ap.add_argument("report", help="report JSON (references/schema.json)")
    ap.add_argument("measurement", help="measurement JSON from the measure step")
    ap.add_argument("out", help="output .html path")
    names = available_themes()
    ap.add_argument("--theme", required=True,
                    help="theme name (" + (", ".join(names) or "none installed") + ") or a path to a theme .json")
    ap.add_argument("--extra", help='JSON array of {"title", "kicker", "nav", "html"} appended after Growth')
    ap.add_argument("--audio", help="audio URL for the sticky mini player")
    ap.add_argument("--date", help="report date YYYY-MM-DD (default: today)")
    a = ap.parse_args(argv)

    try:
        theme = load_theme(a.theme)
    except (OSError, ValueError) as err:
        ap.error(f"cannot load theme {a.theme!r}: {err}")
    report, meas = load_json(a.report), load_json(a.measurement)
    extra = load_json(a.extra) if a.extra else []
    if not isinstance(extra, list) or not all(isinstance(x, dict) for x in extra):
        ap.error('--extra must be a JSON array of {"title", "kicker", "nav", "html"} objects')
    if a.audio and not media_url(a.audio):
        ap.error("--audio must be an http(s) URL or a relative path")
    day = dt.date.fromisoformat(a.date) if a.date else dt.date.today()
    date_label = f"{day.day} {day:%B} {day.year}"

    for w in check_report(report):
        print(f"warning: {w}", file=sys.stderr)
    page = build_page(report, meas, theme, extra, date_label, a.audio)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {a.out} ({len(page.encode('utf-8')) // 1024} KB, theme {theme['name']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
