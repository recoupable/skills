"""Build one chapter composition (news-desk format) from the episode project.

Usage:
  python3 scripts/podcast/build.py <project> <chapter-id> [--recut]

Reads <project>/episode.json (names, ghost word), <project>/edit/chapters.json (cut list),
<project>/edit/specs.py (SPECS: cards, lower thirds, ticker per chapter) and the per-speaker
transcripts <project>/edit/transcripts/{host,guest}.json (ElevenLabs Scribe word timestamps).
Writes <project>/comp/chapters/<id>/index.html; cuts media first via cut.py when missing (or --recut).

Every graphic is anchored to a transcript PHRASE in raw recording time, ('h'|'g', "phrase", search_after),
and mapped through the chapter's cut pieces, so trimming the edit never knocks a card off its line.
Card types: headline, tline, stat, versus, quote, list. Shots: 'B' = card + picture-in-picture anchors,
'C' = full-frame card; the gaps between cards are shot 'A' (two anchors). A chapter opens on a full-frame
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
    elif t == 'list':
        chips = ''.join(f'<div class="chip st"><span class="mono">{i + 1:02d}</span>{e(x)}</div>' for i, x in enumerate(c['items']))
        h3 = f'<h3 class="st">{e(c["h"])}</h3>' if c.get('h') else ''
        body = f'{src}{h3}<div class="chips">{chips}</div>{foot}'
    else:
        raise SystemExit(f'unknown card type {t}')
    return f'<section id="{k}" class="card {cls} {t} clip" data-start="{c["_s"]:g}" data-duration="{round(c["_e"] - c["_s"], 2):g}" data-track-index="{c["_track"]}">{body}</section>'


def build():
    ch = Chapter(CID); spec = SPECS[CID]; c = ch.c
    d = os.path.join(PROJ, 'comp/chapters', CID); os.makedirs(f'{d}/assets', exist_ok=True)
    if RECUT or not os.path.exists(f'{d}/assets/mix.m4a'):
        subprocess.run([sys.executable, os.path.join(HERE, 'cut.py'), PROJ, CID], check=True)
    for sub in ('fonts', 'logos'):
        if not os.path.exists(f'{d}/assets/{sub}'):
            shutil.copytree(os.path.join(BRAND, sub), f'{d}/assets/{sub}')
    hf = f'{d}/hyperframes.json'
    if not os.path.exists(hf):
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, open(hf, 'w'), indent=2)
    D = ch.total
    CARD_GAP = 0.35
    CH_MIN = 0.3 if spec.get('no_chapter') else 2.7
    cards = []
    for i, cd in enumerate(spec['cards']):
        cd = dict(cd)
        cd['_s'] = max(ch.anchor(cd['at']) + cd.get('lead', -0.2), CH_MIN)
        cd['_e'] = ch.anchor(cd['end'], end=True) + cd.get('tail', 0.4) if 'end' in cd else cd['_s'] + cd['dur']
        cd['_e'] = min(cd['_e'], D)
        cd['_track'] = 30 + i
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
    lts = []
    for i, lt in enumerate(spec.get('lower_thirds', [])):
        s = max(ch.anchor(lt['at']) + 0.3, CH_END + 0.3 if CH_END else 0.4)
        lts.append(dict(lt, _s=round(s, 2), _e=round(min(s + lt.get('dur', 6.0), D), 2), _id=f'lt{i}'))
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

    out = open(TEMPLATE).read()
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
