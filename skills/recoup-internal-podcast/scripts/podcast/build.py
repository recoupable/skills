"""Build one chapter composition (news-desk format) from the episode project.

Usage:
  python3 scripts/podcast/build.py <project> <chapter-id> [--recut]

Reads <project>/episode.json (names, ghost word), <project>/edit/chapters.json (cut list),
<project>/edit/specs.py (SPECS: cards, lower thirds, ticker per chapter) and the per-speaker
transcripts <project>/edit/transcripts/{host,guest}.json (ElevenLabs Scribe word timestamps).
Writes <project>/comp/chapters/<id>/index.html; cuts media first via cut.py when missing (or --recut).

Every graphic is anchored to a transcript PHRASE in raw recording time, ('h'|'g', "phrase", search_after),
and mapped through the chapter's cut pieces, so trimming the edit never knocks a card off its line.
Card types: headline, tline, stat, versus, quote, list, evidence (a real capture, huashu-art-motion Vox grammar). Shots: 'B' = card + picture-in-picture anchors,
'C' = full-frame card; the gaps between cards are shot 'A' (two anchors).
Owner rules built in (Sweetman): shot A is GUEST FOCUS by default, guest tile large, host a small inset (2026-10-06:
"minimize my video... keeping ancillary content as the main focus or the guest"); set "layout": "equal" in
episode.json for the old side-by-side. Any card may carry art=[('file in <project>/edit/art', 'line 1', 'line 2'), ...]
(1-2 covers; album/single art when a record is named, 2026-10-10; list sources in edit/art/SOURCES.md). The build
warns on any camera-only stretch over 15 s (card-density rule, 30 s 2026-10-10, 15 s 2026-10-18): add a card there.
An evidence card puts a real capture on screen: img='file in <project>/edit/refs' (listed in edit/refs/SOURCES.md),
mark=(x, y, w, h) in % of the image (measured on the capture, not eyeballed) swept with the highlighter on
mark_at=('g'|'h', "phrase", after), and an optional verbatim tag line. A chapter opens on a full-frame
chapter card unless its spec sets no_chapter (the cold open).
Scripts ship alongside this skill (scripts/podcast/, templates/podcast/news-desk.html).
"""
import html as H
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', '..', 'templates', 'podcast', 'news-desk.html')
BRAND = os.path.join(HERE, '..', '..', 'brand')

args = sys.argv[1:]
if len(args) < 2:
    sys.exit(__doc__)
PROJ, CID, RECUT = os.path.abspath(args[0]), args[1], '--recut' in args
EP = json.load(open(os.path.join(PROJ, 'episode.json')))
CH = json.load(open(os.path.join(PROJ, 'edit/chapters.json')))
_spec = importlib.util.spec_from_file_location('specs', os.path.join(PROJ, 'edit/specs.py'))
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
SPECS = _m.SPECS


def words(who):
    L = [dict(x) for x in json.load(open(os.path.join(PROJ, f'edit/transcripts/{who}.json')))['words'] if x['type'] == 'word']
    for x in L:                       # Scribe stretches some words across silences; clamp them
        if x['end'] - x['start'] > 1.5:
            x['start'] = x['end'] - 0.6
    return L


W = {'h': words('host'), 'g': words('guest')}
norm = lambda t: re.sub(r"[^\w'%]", '', t.lower())


def find(who, phrase, after=0.0):
    p = [norm(t) for t in phrase.split()]
    L = W[who]; tx = [norm(x['text']) for x in L]
    for i in range(len(tx)):
        if L[i]['start'] >= after and tx[i:i + len(p)] == p:
            return L[i]['start'], L[i + len(p) - 1]['end']
    raise SystemExit(f'phrase not found: {who} "{phrase}" after {after}')


class Chapter:
    def __init__(self, cid):
        self.c = [c for c in CH['chapters'] if c['id'] == cid][0]
        self.P = self.c['pieces']
        self.total = round(sum(p['out'] - p['in'] for p in self.P), 2)

    def t(self, raw):
        """raw recording seconds -> chapter seconds (inside a kept piece; else the next piece's start)."""
        c = 0.0
        for p in self.P:
            if p['in'] <= raw < p['out']:
                return round(c + raw - p['in'], 2)
            c += p['out'] - p['in']
        c = 0.0
        for p in self.P:
            if raw < p['in']:
                return round(c, 2)
            c += p['out'] - p['in']
        return self.total

    def anchor(self, a, end=False):
        if isinstance(a, (int, float)):
            return float(a)
        who, phrase, after = a
        s, e = find(who, phrase, after)
        return self.t(e if end else s)

    def muted(self, who, raw):
        for p in self.P:
            if p['in'] <= raw < p['out']:
                if who == 'g' and p.get('host_only'):
                    return True
                for a, b in p.get('mute_host' if who == 'h' else 'mute_guest', []):
                    if a <= raw < b:
                        return True
                return False
        return True

    def speaking(self):
        out = {}
        for who in ('h', 'g'):
            spans = []
            for x in W[who]:
                if self.muted(who, x['start']):
                    continue
                a = self.t(x['start']); b = self.t(min(x['end'], x['start'] + 1.2))
                if b < a:
                    continue
                if spans and a - spans[-1][1] < 1.0:
                    spans[-1][1] = b
                else:
                    spans.append([a, b])
            out[who] = [[round(a, 2), round(b, 2)] for a, b in spans if b - a > 0.4]
        return out


e = H.escape
GUEST_FOCUS_A = ('A: { g: { left: 150, top: 175, width: 1004, height: 565, opacity: 1, scale: 1 }, '
                 'h: { left: 1300, top: 510, width: 408, height: 230, opacity: 1, scale: 1 } },')
ART_CSS = """
  .card.has-art > :not(.art):not(.stamp) { max-width: 760px; }
  .ccard.has-art > :not(.art):not(.stamp) { max-width: 1000px; }
  .card.has-two > :not(.art):not(.stamp) { max-width: 590px; }
  .ccard.has-two > :not(.art):not(.stamp) { max-width: 880px; }
  .card .art { position: absolute; right: 80px; top: 50%; margin-top: -250px; display: flex; gap: 28px; }
  .card .art figure { margin: 0; width: 360px; display: flex; flex-direction: column; gap: 16px; }
  .card .art.two figure { width: 250px; }
  .card .art img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 18px; box-shadow: 0 0 0 3px var(--border), 0 24px 60px rgba(21,46,55,.22); }
  .card .art figcaption { font-size: 24px; line-height: 1.25; color: var(--forest); }
  .card .art figcaption b { display: block; font-weight: 700; }
  .card .art figcaption span { opacity: .7; font-size: 20px; }
"""


def card_html(k, c):
    t = c['type']; cls = 'ccard' if c['shot'] == 'C' else 'bcard'
    src = f'<div class="src mono st"><b>{e(c["src"])}</b>{e(c.get("meta", ""))}</div>'
    foot = ''
    if c.get('foot'):
        l, r = (c['foot'] + [''])[:2]
        foot = f'<div class="foot mono st"><span>{e(l)}</span><span>{e(r)}</span></div>'
    if t == 'headline':
        stamp = ''
        if c.get('stamp'):
            a, b, d = c['stamp']
            stamp = f'<div class="stamp mono"><span class="a">{e(a)}</span><span class="b">{e(b)}</span><span class="a">{e(d)}</span></div>'
        p = f'<p class="st">{e(c["p"])}</p>' if c.get('p') else ''
        body = f'<div class="topline st"></div>{src}<h2 class="st">{e(c["h"])}</h2>{p}{foot}{stamp}'
    elif t == 'tline':
        rows = ''.join(f'<div class="row st{" hl" if hl else ""}"><div class="d mono">{e(d)}</div><div class="e">{e(x)}</div></div>' for d, x, hl in c['rows'])
        body = f'{src}<h3 class="st">{e(c["h"])}</h3><div class="rows">{rows}</div>{foot}'
    elif t == 'stat':
        q = f'<div class="q st">{c["q"]}</div>' if c.get('q') else ''
        scale = f'<div class="bar st"><i></i></div><div class="scale mono st"><span>{e(c["left"])}</span><span>{e(c["right"])}</span></div>' if c.get('left') else ''
        body = f'{src}<div class="big st"><div class="num">{e(c["num"])}</div><div class="unit">{e(c["unit"])}</div></div>{scale}{q}{foot}'
    elif t == 'versus':
        (wa, va, pa), (wb, vb, pb) = c['a'], c['b']
        body = (f'{src}<div class="cols"><div class="col a st"><div class="who mono">{e(wa)}</div><div class="v">{e(va)}</div><p>{e(pa)}</p></div>'
                f'<div class="col b st"><div class="who mono">{e(wb)}</div><div class="v">{e(vb)}</div><p>{e(pb)}</p></div></div>{foot}')
    elif t == 'quote':
        body = f'{src}<div class="qmark st">“</div><blockquote class="st">{c["q"]}</blockquote>{foot}'
    elif t == 'evidence':
        x, y, w, hh = c.get('mark', (0, 0, 0, 0))
        mark = f'<i class="mark" style="left:{x}%;top:{y}%;width:{w}%;height:{hh}%"></i>' if c.get('mark') else ''
        tag = f'<div class="etag">{c["tag"]}</div>' if c.get('tag') else ''
        h3 = f'<h3>{e(c["h"])}</h3>' if c.get('h') else ''
        body = (f'<div class="print"><span class="tape l"></span><span class="tape r"></span><div class="shot">'
                f'<img src="assets/refs/{e(os.path.basename(c["img"]))}" alt="">{mark}</div></div>'
                f'<div class="side">{src}{h3}{tag}{foot}</div>')
    elif t == 'list':
        chips = ''.join(f'<div class="chip st"><span class="mono">{i + 1:02d}</span>{e(x)}</div>' for i, x in enumerate(c['items']))
        h3 = f'<h3 class="st">{e(c["h"])}</h3>' if c.get('h') else ''
        body = f'{src}{h3}<div class="chips">{chips}</div>{foot}'
    else:
        raise SystemExit(f'unknown card type {t}')
    if c.get('art'):
        figs = ''.join(f'<figure><img src="assets/art/{e(os.path.basename(a))}" alt=""><figcaption><b>{e(l1)}</b><span>{e(l2)}</span></figcaption></figure>'
                       for a, l1, l2 in c['art'])
        body += f'<div class="art st{" two" if len(c["art"]) > 1 else ""}">{figs}</div>'
        cls += ' has-art' + (' has-two' if len(c['art']) > 1 else '')
    return f'<section id="{k}" class="card {cls} {t} clip" data-start="{c["_s"]:g}" data-duration="{round(c["_e"] - c["_s"], 2):g}" data-track-index="{c["_track"]}">{body}</section>'


def build():
    ch = Chapter(CID); spec = SPECS[CID]; c = ch.c
    d = os.path.join(PROJ, 'comp/chapters', CID); os.makedirs(f'{d}/assets', exist_ok=True)
    if RECUT or not os.path.exists(f'{d}/assets/mix.m4a'):
        subprocess.run([sys.executable, os.path.join(HERE, 'cut.py'), PROJ, CID], check=True)
    for sub in ('fonts', 'logos'):
        if not os.path.exists(f'{d}/assets/{sub}'):
            shutil.copytree(os.path.join(BRAND, sub), f'{d}/assets/{sub}')
    for cd in spec['cards']:
        if cd.get('img'):
            os.makedirs(f'{d}/assets/refs', exist_ok=True)
            shutil.copy(os.path.join(PROJ, 'edit/refs', cd['img']), f'{d}/assets/refs/')
        for a, *_ in cd.get('art', []):
            os.makedirs(f'{d}/assets/art', exist_ok=True)
            shutil.copy(os.path.join(PROJ, 'edit/art', a), f'{d}/assets/art/')
    hf = f'{d}/hyperframes.json'
    if not os.path.exists(hf):
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, open(hf, 'w'), indent=2)
    D = ch.total
    CARD_GAP = 0.35
    MAX_CAMERAS_ONLY = 15
    CH_MIN = 0.3 if spec.get('no_chapter') else 2.7
    cards = []
    for i, cd in enumerate(spec['cards']):
        cd = dict(cd)
        cd['_s'] = max(ch.anchor(cd['at']) + cd.get('lead', -0.2), CH_MIN)
        cd['_e'] = ch.anchor(cd['end'], end=True) + cd.get('tail', 0.4) if 'end' in cd else cd['_s'] + cd['dur']
        cd['_e'] = min(cd['_e'], D)
        cd['_track'] = 30 + i
        if 'mark_at' in cd:
            cd['_mark'] = ch.anchor(cd['mark_at'])
        cards.append(cd)
    cards.sort(key=lambda x: x['_s'])
    for a, b in zip(cards, cards[1:]):           # no overlaps
        if a['_e'] > b['_s'] - CARD_GAP:
            a['_e'] = round(b['_s'] - CARD_GAP, 2)
    first = c['pieces'][0]                        # a host splice at the top hides under the chapter card
    CH_END = round(max(2.6, (first['out'] - first['in'] + 0.4) if first.get('host_only') else 2.6), 2)
    if spec.get('no_chapter'):
        CH_END = 0.0
    shots = [(0.0, 'A')] if spec.get('no_chapter') else [(0.0, 'C')]
    cur = shots[0][1]; t_free = CH_END
    for cd in cards:
        if cd['_s'] - t_free > 0.9 and cur != 'A':
            shots.append((round(t_free - 0.1, 2), 'A')); cur = 'A'
        if cur != cd['shot']:
            shots.append((round(cd['_s'] - 0.15, 2), cd['shot'])); cur = cd['shot']
        t_free = cd['_e']
    if t_free < D - 0.5 and cur != 'A':
        shots.append((round(t_free - 0.1, 2), 'A'))
    t_cov = CH_END                                 # card-density rule: no camera-only stretch over 15 s
    for cd in cards + [dict(_s=D, _e=D)]:
        if cd['_s'] - t_cov > MAX_CAMERAS_ONLY:
            print(f'WARN {CID}: {cd["_s"] - t_cov:.1f}s with cameras only at {t_cov:.1f}-{cd["_s"]:.1f}s; add a card')
        t_cov = max(t_cov, cd['_e'])
    lts = []
    for i, lt in enumerate(spec.get('lower_thirds', [])):
        s = max(ch.anchor(lt['at']) + 0.3, CH_END + 0.3 if CH_END else 0.4)
        lts.append(dict(lt, _s=round(s, 2), _e=round(min(s + lt.get('dur', 6.0), D), 2), _id=f'lt{i}'))
        for cd in cards:                          # a lower third under a card renders hidden or half-covered
            if cd['_s'] < lts[-1]['_e'] and lts[-1]['_s'] < cd['_e']:
                print(f'WARN {CID}: lower third "{lt["n"]}" ({lts[-1]["_s"]:.1f}-{lts[-1]["_e"]:.1f}s) overlaps a {cd["shot"]} card '
                      f'({cd["_s"]:.1f}-{cd["_e"]:.1f}s); move it to an open shot or shorten dur')
    sp = ch.speaking()

    cards_html = '\n  '.join(card_html(f'k{i}', cd) for i, cd in enumerate(cards))
    lt_html = '\n  '.join(
        f'<div id="{lt["_id"]}" class="lt clip {"lt-g" if lt["who"] == "g" else "lt-h"}" data-start="{lt["_s"]:g}" data-duration="{round(lt["_e"] - lt["_s"], 2):g}" data-track-index="{20 + i}">'
        f'<div class="bar"></div><div class="body"><div class="k mono">{e(lt["k"])}</div><div class="n">{e(lt["n"])}</div><div class="t">{e(lt["t"])}</div></div></div>'
        for i, lt in enumerate(lts))
    ticker = ''.join(f'<span>{e(x)}</span>' for x in (spec['ticker'] * 4))
    title = e(c['title'])
    js_cards = []
    for i, cd in enumerate(cards):
        k = f'#k{i}'; s = cd['_s']; en = cd['_e']
        if cd['type'] == 'evidence':                # Vox grammar: real material is simply there on the cut; elements step at 12 fps
            js_cards.append(f'tl.fromTo("{k}", {{ opacity: 0 }}, {{ opacity: 1, duration: .12 }}, {s:g});')
            if cd.get('tag'):
                js_cards.append(f'tl.fromTo("{k} .etag", {{ x: 90, rotation: 12, opacity: 0 }}, {{ x: 0, rotation: -2, opacity: 1, duration: .55, ease: "steps(7)" }}, {s + 0.4:g});')
            if cd.get('mark'):
                ms = max(cd.get('_mark', s + 0.6), s + 0.3)
                js_cards.append(f'tl.fromTo("{k} .mark", {{ scaleX: 0 }}, {{ scaleX: 1, duration: .9, ease: "steps(11)" }}, {ms:g});')
        else:
            frm = '{ y: 70, opacity: 0 }' if cd['shot'] == 'C' else '{ x: -80, opacity: 0 }'
            js_cards.append(f'tl.fromTo("{k}", {frm}, {{ x: 0, y: 0, opacity: 1, duration: .55, ease: "power3.out" }}, {s:g});')
            js_cards.append(f'stag("{k}", {s + 0.25:g}, {min(0.16, max(0.08, (en - s - 1.5) / 12)):.3f});')
        if cd['type'] == 'stat' and cd.get('left'):
            js_cards.append(f'tl.fromTo("{k} .bar i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 2.2, ease: "power2.inOut" }}, {s + 1.0:g});')
        if cd['type'] == 'headline' and cd.get('stamp'):
            js_cards.append(f'tl.fromTo("{k} .stamp", {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: 8, duration: .6, ease: "back.out(2)" }}, {s + 0.9:g});')
        js_cards.append(f'tl.to("{k}", {{ opacity: 0, y: -30, duration: .3, ease: "power2.in" }}, {en - 0.3:g});')
    js_lts = []
    for lt in lts:
        dx = -60 if lt['who'] == 'g' else 60
        js_lts.append(f'tl.fromTo("#{lt["_id"]}", {{ x: {dx}, opacity: 0 }}, {{ x: 0, opacity: 1, duration: .6, ease: "expo.out" }}, {lt["_s"]:g});')
        js_lts.append(f'tl.fromTo("#{lt["_id"]} .bar", {{ scaleY: 0 }}, {{ scaleY: 1, transformOrigin: "top", duration: .5, ease: "power2.out" }}, {lt["_s"] + 0.1:g});')
        js_lts.append(f'tl.to("#{lt["_id"]}", {{ x: {dx // 2}, opacity: 0, duration: .4, ease: "power2.in" }}, {lt["_e"] - 0.4:g});')
    js_shots = '\n  '.join(f'shot("{k}", {t:g});' for t, k in shots)

    out = open(TEMPLATE).read().replace('</style>', ART_CSS + '</style>', 1)
    if EP.get('layout', 'guest_focus') == 'guest_focus':
        out2 = re.sub(r'A: \{ g: \{[^}]*\}, h: \{[^}]*\} \},', GUEST_FOCUS_A, out, count=1)
        out2 = out2.replace('tl.to(REG, { opacity: kind === "A" ? 1 : 0, duration: .35 }', 'tl.to(REG, { opacity: 0, duration: .35 }')
        assert out2 != out, 'guest-focus layout: shot A pattern not found in the template'
        out = out2
    for k, v in {'{{TITLE}}': f'Recoup Podcast: {e(EP["guest"]["name"])}, {c["num"]} {title}', '{{DUR}}': f'{D:g}',
                 '{{CHAPTER_LABEL}}': f'{c["num"]} · {title}', '{{CHAPTER_NUM}}': c['num'], '{{CHAPTER_TITLE}}': title,
                 '{{CH_END}}': f'{CH_END:g}', '{{CARDS}}': cards_html, '{{LOWER_THIRDS}}': lt_html, '{{TICKER}}': ticker,
                 '{{SPEAK}}': json.dumps(sp), '{{SHOTS}}': js_shots, '{{JS_CARDS}}': '\n  '.join(js_cards),
                 '{{JS_LTS}}': '\n  '.join(js_lts), '{{GHOST}}': e(EP.get('ghost', 'RIGHTS × AI')),
                 '{{GUEST_NAME}}': e(EP['guest']['name']), '{{HOST_NAME}}': e(EP['host']['name'])}.items():
        out = out.replace(k, v)
    if spec.get('no_chapter'):
        out = re.sub(r'<!--CHAPTER-->.*?<!--/CHAPTER-->', '', out, flags=re.S)
        out = re.sub(r'//CHAPTER-JS.*?//END-CHAPTER-JS', '', out, flags=re.S)
        out = out.replace(f'{c["num"]} · {title}', title)
    open(f'{d}/index.html', 'w').write(out)
    print(f'{CID}: {D:.2f}s, {len(cards)} cards, {len(lts)} lower thirds, shots: ' + ' '.join(f'{k}@{t:g}' for t, k in shots))


if __name__ == '__main__':
    build()
