"""Build one HYBRID podcast short (1080x1920): guest video + full-frame motion-graphic beats.

Usage:
  python3 scripts/podcast/shorts/build_hy.py <project> <short-id> [<short-id> ...] [--recut]

Reads (all inside <project>):
  episode.json                  guest name/role, title; optional "shorts" block:
                                {"who": "Jane Doe · Example Rights Co", "end_url": "recoupable.dev/podcast",
                                 "object_position": "50% 30%", "host_audio": "raw/host-audio-enhanced.wav"}
  edit/shorts.json              cut list in RAW seconds, same piece format as chapters.json (in/out, mute_host,
                                mute_guest, host_only, video_from), top-level "offsets", and per short:
                                {"id": "s1", "day": "Mon", "hook": "...", "hook_size": 66, "pieces": [...]}
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
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, '..', '..', '..')
TEMPLATE = os.path.join(SKILL, 'templates', 'podcast', 'shorts', 'hybrid.html')
BRAND = os.path.join(SKILL, 'brand')
END = 2.6                                   # "Full episode out now" end card, seconds
e = H.escape

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
    chunks, cur = [], []
    for w in ws:
        if cur and (len(cur) >= 3 or len(' '.join(c[2] for c in cur + [w])) > 18 or w[0] - cur[-1][1] > 0.45
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
        subprocess.run(cut, check=True)
    for sub in ('fonts', 'logos'):
        if not os.path.exists(f'{d}/assets/{sub}'):
            shutil.copytree(os.path.join(BRAND, sub), f'{d}/assets/{sub}')
    hf = f'{d}/hyperframes.json'
    if not os.path.exists(hf):
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, open(hf, 'w'), indent=2)
    CLIP = sh.total; D = round(CLIP + END, 2)
    T = {k: sh.anchor(tuple(a), end=k.endswith('_end')) for k, a in anchors.items()}
    js = part('JS')
    for k in sorted(T, key=len, reverse=True):
        js = js.replace('@' + k, f'{T[k]:g}')
    assert not re.search(r'@[a-z]', js), re.findall(r'@\w+', js)
    caps_html, caps_js = captions(sh)
    g = EP['guest']
    who = CFG.get('who') or f"{g['name']} · {g['role'].split(',')[-1].strip()}"
    rep = {'TITLE': e(f'Recoup Podcast short: {c["hook"]}'), 'HOOK': e(c['hook']), 'HOOK_SIZE': str(c.get('hook_size', 66)),
           'DUR': f'{D:g}', 'CLIP': f'{CLIP:g}', 'END': f'{END:g}', 'EP_TITLE': e(EP['title']), 'WHO_AT': f'{T.get("who", 0.6):g}',
           'WHO': e(who), 'END_URL': e(CFG.get('end_url', 'recoupable.dev/podcast')), 'OBJ_POS': CFG.get('object_position', '50% 30%'),
           'CSS': part('CSS'), 'STAGE': part('HTML'), 'JS': js,
           'CAPS': caps_html, 'CAP_JS': caps_js, 'GRING': json.dumps(spans(sh, 'g', 0.1, 0.3, 1.0, 0.4))}
    out = open(TEMPLATE).read()
    for k, v in rep.items():
        out = out.replace('{{' + k + '}}', v)
    assert '{{' not in out, re.findall(r'\{\{\w+\}\}', out)
    if re.search(r'id="c\d+"', part('HTML')):
        sys.exit(f'{sid}: a scene element uses a caption id (c0..cN); rename it')
    open(f'{d}/index.html', 'w').write(out)
    print(f'{sid}: {CLIP:.2f}s + {END}s end card; ' + ' '.join(f'{k}={v:.1f}' for k, v in T.items()))


for s in SIDS:
    build(s)
