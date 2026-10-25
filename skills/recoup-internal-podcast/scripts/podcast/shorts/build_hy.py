"""Build one HYBRID podcast short (1080x1920): guest video + full-frame motion-graphic beats.

Usage:
  python3 scripts/podcast/shorts/build_hy.py <project> <short-id> [<short-id> ...] [--recut]

Reads (all inside <project>):
  episode.json                  guest name/role, title; optional "shorts" block:
                                {"who": "Jane Doe · Example Rights Co", "end_url": "recoupable.dev/podcast",
                                 "end_label": "Full episode out now",
                                 "object_position": "50% 30%", "end_title": "<the published episode title>", "host_audio": "raw/host-audio-enhanced.wav",
                                 "guest_audio": "raw/guest-audio-enhanced.wav"}
  edit/shorts.json              cut list in RAW seconds, same piece format as chapters.json (in/out, mute_host,
                                mute_guest, host_only, video_from), top-level "offsets", and per short:
                                {"id": "s1", "day": "Mon", "hook": "...", "hook_size": 66, "pieces": [...]}
                                optional per short: "template": "kinetic" (templates/podcast/shorts/<name>.html, default
                                "hybrid"), "caption_words": 1 (words per caption line, default 3) and (kinetic only)
                                "rehook": {"text": "So who *paid?*", "at": "<anchor name>"} (swaps the title there),
                                "end_title" (this short's end-card line; default episode.json shorts.end_title).
                                In "hook"/"rehook" text, *word* is the italic serif accent.
  edit/transcripts/{host,guest}.json   ElevenLabs Scribe word timestamps (same files the episode uses)
  edit/shorts/<id>.html         the beats: <!--ANCHORS {json}--> then <!--CSS-->, <!--HTML-->, <!--JS--> sections.
                                Anchors are {"name": ["g"|"h", "phrase", raw_search_after]}; names ending in
                                _end anchor to the phrase's last word end. In JS, @name becomes that time in
                                short seconds, and JS must define SC = [[selector, start, end], ...]. Contiguous
                                scenes form one beat; during a beat the guest video morphs into the corner circle.
                                An anchor named "who" times the guest name tag (default 0.6 s).
Writes <project>/comp/shorts/<id>/index.html (+ assets: cut media via ../cut.py, brand fonts/logos).
Captions (2-3 words, active word lime) and the guest's speaking ring come from the transcripts.
Template: templates/podcast/shorts/hybrid.html. Scripts ship alongside this skill.
"""
import html as H
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, '..', '..', '..')
TEMPLATE = lambda name: os.path.join(SKILL, 'templates', 'podcast', 'shorts', f'{name}.html')
BRAND = os.path.join(SKILL, 'brand')
EXTRA_FONTS = os.path.join(SKILL, 'templates', 'podcast', 'shorts', 'fonts')
END = 2.6                                   # "Full episode out now" end card, minimum seconds
e = H.escape
acc = lambda t: re.sub(r'\*(.+?)\*', r'<span class="ser">\1</span>', e(t))   # *word* -> serif accent

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if len(args) < 2:
    sys.exit(__doc__)
PROJ, SIDS, RECUT = os.path.abspath(args[0]), args[1:], '--recut' in sys.argv
EP = json.load(open(os.path.join(PROJ, 'episode.json')))
CFG = EP.get('shorts', {})
SH = json.load(open(os.path.join(PROJ, 'edit/shorts.json')))


def words(who):
    L = [dict(x) for x in json.load(open(os.path.join(PROJ, f'edit/transcripts/{who}.json')))['words'] if x['type'] == 'word']
    for x in L:                       # Scribe stretches some words across silences; clamp them
        if x['end'] - x['start'] > 1.5:
            x['start'] = x['end'] - 0.6
    for a_, b_ in EP.get('caption_fixes', []):   # same name fixes as make_srt.py; a two-word match merges the pair
        i = 0
        while i < len(L):
            pair = i + 1 < len(L) and re.fullmatch(r'\W*' + a_ + r'\W*', L[i]['text'] + ' ' + L[i + 1]['text'])
            if pair:
                L[i] = dict(L[i], text=re.sub(a_, b_, L[i]['text'] + ' ' + L[i + 1]['text']), end=L[i + 1]['end'])
                del L[i + 1]
            else:
                L[i]['text'] = re.sub(a_, b_, L[i]['text'])
            i += 1
    return L


W = {'h': words('host'), 'g': words('guest')}
norm = lambda t: re.sub(r"[^\w'%]", '', t.lower())


def find(who, phrase, after=0.0):
    for a_, b_ in EP.get('caption_fixes', []):   # anchors may quote the raw transcript; words carry the fixed names
        phrase = re.sub(a_, b_, phrase)
    p = [norm(t) for t in phrase.split()]
    L = W[who]; tk = [(norm(t), i) for i, x in enumerate(L) for t in x['text'].split()]   # a merged fix like "Arty Shield" stays two tokens
    tx = [t for t, _ in tk]
    for j in range(len(tx)):
        if L[tk[j][1]]['start'] >= after and tx[j:j + len(p)] == p:
            return L[tk[j][1]]['start'], L[tk[j + len(p) - 1][1]]['end']
    raise SystemExit(f'phrase not found: {who} "{phrase}" after {after}')


class Short:
    def __init__(self, sid):
        self.c = [c for c in SH['shorts'] if c['id'] == sid][0]
        self.P = self.c['pieces']
        self.total = round(sum(p['out'] - p['in'] for p in self.P), 2)

    def t(self, raw):
        """raw recording seconds -> short seconds (inside a kept piece; else the next piece's start)."""
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
        s, en = find(who, phrase, after)
        return self.t(en if end else s)

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


def captions(sh):
    """Chunk spoken words (both speakers, unmuted) into caption lines of <= 3 words / 18 chars.
    Caption ids are c0..cN: never reuse those ids for scene elements."""
    ws = []
    for who in ('g', 'h'):
        for x in W[who]:
            if sh.muted(who, x['start']):
                continue
            t = x['text'].strip()
            if re.fullmatch(r"\w{1,2}-", t):          # false starts like "y-"
                continue
            a = sh.t(x['start']); b = sh.t(x['end'])
            if b <= a:
                continue
            ws.append([a, b, t.rstrip('-')])
    ws.sort()
    for k, w in enumerate(ws):            # a cut can land mid-sentence: the first word and any word after . ? ! get a capital
        if k == 0 or re.search(r'[.?!]["\u201d]?$', ws[k - 1][2]):
            w[2] = re.sub(r'^(["\u201c]?)(\w)', lambda m: m.group(1) + m.group(2).upper(), w[2])
    n = sh.c.get('caption_words', 3)
    chunks, cur = [], []
    for w in ws:
        if cur and (len(cur) >= n or len(' '.join(c[2] for c in cur + [w])) > 18 or w[0] - cur[-1][1] > 0.45
                    or re.search(r'[.,?!:]$', cur[-1][2])):
            chunks.append(cur); cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    html, js = [], []
    for i, c in enumerate(chunks):
        a = c[0][0]; b = chunks[i + 1][0][0] if i + 1 < len(chunks) else c[-1][1] + 0.3
        b = min(b, c[-1][1] + 0.6, sh.total)
        html.append(f'<div id="c{i}" class="cap">' + ''.join(f'<span>{e(w[2])}</span>' for w in c) + '</div>')
        js.append([f'c{i}', round(a, 2), round(b, 2), [[j, round(w[0], 2)] for j, w in enumerate(c)]])
    return '\n    '.join(html), json.dumps(js)


def spans(sh, who, pad_in=0.3, pad_out=0.5, gap=1.5, min_len=0.6):
    out = []
    for x in W[who]:
        if sh.muted(who, x['start']):
            continue
        a = sh.t(x['start']) - pad_in; b = sh.t(x['end']) + pad_out
        if out and a - out[-1][1] < gap:
            out[-1][1] = b
        else:
            out.append([a, b])
    return [[round(max(a, 0), 2), round(min(b, sh.total), 2)] for a, b in out if b - a >= min_len]


def build(sid):
    sh = Short(sid); c = sh.c
    src = open(os.path.join(PROJ, 'edit/shorts', f'{sid}.html')).read()
    anchors = json.loads(re.search(r'<!--ANCHORS (.*?)-->', src, re.S).group(1))
    part = lambda k: re.search(rf'<!--{k}-->(.*?)(?=<!--[A-Z]+-->|\Z)', src, re.S).group(1)
    d = os.path.join(PROJ, 'comp/shorts', sid); os.makedirs(f'{d}/assets', exist_ok=True)
    if RECUT or not os.path.exists(f'{d}/assets/mix.m4a'):
        cut = [sys.executable, os.path.join(HERE, '..', 'cut.py'), PROJ, sid, '--cutlist', 'edit/shorts.json',
               '--out', os.path.join('comp/shorts', sid, 'assets')]
        if CFG.get('host_audio'):
            cut += ['--host-audio', CFG['host_audio']]
        if CFG.get('guest_audio'):
            cut += ['--guest-audio', CFG['guest_audio']]
        subprocess.run(cut, check=True)
    for sub in ('fonts', 'logos'):
        if not os.path.exists(f'{d}/assets/{sub}'):
            shutil.copytree(os.path.join(BRAND, sub), f'{d}/assets/{sub}')
    for f in os.listdir(EXTRA_FONTS):     # template-only fonts kept outside the vendored brand/ tree
        shutil.copy2(os.path.join(EXTRA_FONTS, f), f'{d}/assets/fonts/{f}')
    hf = f'{d}/hyperframes.json'
    if not os.path.exists(hf):
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, open(hf, 'w'), indent=2)
    ep_title = c.get('end_title') or CFG.get('end_title', EP['title'])
    end = max(END, math.ceil((len(ep_title) / 15 + 1.5) * 10) / 10)   # the end card holds long enough to read its title
    CLIP = sh.total; D = round(CLIP + end, 2)
    T = {k: sh.anchor(tuple(a) if isinstance(a, list) else a, end=k.endswith('_end')) for k, a in anchors.items()}
    js = part('JS')
    for k in sorted(T, key=len, reverse=True):
        js = js.replace('@' + k, f'{T[k]:g}')
    assert not re.search(r'@[a-z]', js), re.findall(r'@\w+', js)
    caps_html, caps_js = captions(sh)
    hshot, c0 = [], 0.0                   # pieces with "shot": "host" show the host camera on the stage (host-first open)
    for p in sh.P:
        if p.get('shot') == 'host':
            hshot.append([round(c0, 2), round(c0 + p['out'] - p['in'], 2)])
        c0 += p['out'] - p['in']
    h = EP.get('host', {})
    hwho = CFG.get('host_who') or f"{h.get('name', 'Host')} · {h.get('role', '').split(',')[-1].strip()}"
    g = EP['guest']
    who = CFG.get('who') or f"{g['name']} · {g['role'].split(',')[-1].strip()}"
    rh = c.get('rehook', {})
    rep = {'TITLE': e(f'Recoup Podcast short: {c["hook"].replace("*", "")}'), 'HOOK': acc(c['hook']), 'HOOK_SIZE': str(c.get('hook_size', 66)),
           'REHOOK': acc(rh.get('text', '')), 'REHOOK_AT': f'{T[rh["at"]]:g}' if rh else '-1',
           'DUR': f'{D:g}', 'CLIP': f'{CLIP:g}', 'END': f'{end:g}', 'EP_TITLE': e(ep_title), 'WHO_AT': f'{T.get("who", 0.6):g}',
           'WHO_HOLD': f'{max(3.6, math.ceil((len(who) / 15 + 1.5) * 10) / 10):g}',
           'WHO': e(who), 'END_URL': e(CFG.get('end_url', 'recoupable.dev/podcast')),
           'END_LABEL': e(CFG.get('end_label', 'Full episode out now')), 'OBJ_POS': CFG.get('object_position', '50% 30%'),
           'CSS': part('CSS'), 'STAGE': part('HTML'), 'JS': js,
           'CAPS': caps_html, 'CAP_JS': caps_js, 'GRING': json.dumps(spans(sh, 'g', 0.1, 0.3, 1.0, 0.4)),
           'HSHOT': json.dumps(hshot), 'HWHO': e(hwho),
           'HVIDS': ''.join(f'<video id="vid-h{i}" src="assets/host.mp4" data-start="{a:g}" data-duration="{b - a:g}" data-media-start="{a:g}" '
                            f'data-track-index="{i + 1}" muted playsinline></video>' for i, (a, b) in enumerate(hshot))}
    out = open(TEMPLATE(c.get('template', 'hybrid'))).read()
    for k, v in rep.items():
        out = out.replace('{{' + k + '}}', v)
    assert '{{' not in out, re.findall(r'\{\{\w+\}\}', out)
    if re.search(r'id="c\d+"', part('HTML')):
        sys.exit(f'{sid}: a scene element uses a caption id (c0..cN); rename it')
    open(f'{d}/index.html', 'w').write(out)
    print(f'{sid}: {CLIP:.2f}s + {end}s end card; ' + ' '.join(f'{k}={v:.1f}' for k, v in T.items()))


for s in SIDS:
    build(s)
