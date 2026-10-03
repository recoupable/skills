"""Build YouTube captions (SRT) for the assembled episode from the per-speaker ElevenLabs transcripts.

Usage:
  python3 scripts/podcast/make_srt.py <project>          -> <project>/exports/final/youtube-captions.srt

Block order matches assemble.py: exports/opening.mp4 (the ch00 cold open starts at 0; the intro after it has
no dialogue), then exports/<chapter>.mp4 for every other chapter in edit/chapters.json. Block offsets are the
exported block durations. Words are mapped piece by piece (splices may reuse raw ranges); muted words,
host_only guest words and false starts ("y-") are dropped. Speaker changes start with ">> ".

Name fixes: episode.json "caption_fixes": [["\\\\bJane\\\\b", "Jayne"], ...] (regex, replacement), applied last.
Cues shorter than 0.25 s (overlapping speech) are folded into the cue before them: YouTube rejects a file
with an inverted or near-zero cue ("File contains errors on lines ..."). The script asserts clean timing.
Upload in YouTube Studio: video -> Details -> Subtitles (or Languages) -> ⋮ -> Upload file -> With timing.
Needs ffprobe.
"""
import json, os, re, subprocess, sys

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
PROJ = os.path.abspath(args[0])
EP = json.load(open(os.path.join(PROJ, 'episode.json')))
CH = json.load(open(os.path.join(PROJ, 'edit/chapters.json')))['chapters']


def tx(who):
    L = [dict(x) for x in json.load(open(os.path.join(PROJ, f'edit/transcripts/{who}.json')))['words'] if x['type'] == 'word']
    for x in L:                       # Scribe stretches some words across silences; clamp them
        if x['end'] - x['start'] > 1.5:
            x['start'] = x['end'] - 0.6
    return L


W = {'g': tx('guest'), 'h': tx('host')}
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                     capture_output=True, text=True).stdout)
ids = [c['id'] for c in CH]
BLOCKS = ([('ch00', 'exports/opening.mp4')] if 'ch00' in ids else []) + [(c, f'exports/{c}.mp4') for c in ids if c != 'ch00']


def muted(p, who, raw):
    if who == 'g' and p.get('host_only'):
        return True
    return any(x <= raw < y for x, y in p.get('mute_host' if who == 'h' else 'mute_guest', []))


words = []; off = 0.0
for cid, f in BLOCKS:
    c = 0.0
    for p in [x for x in CH if x['id'] == cid][0]['pieces']:
        for who in ('g', 'h'):
            for x in W[who]:
                if not (p['in'] <= x['start'] < p['out']) or muted(p, who, x['start']):
                    continue
                t = x['text'].strip()
                if re.fullmatch(r"\w{1,2}-", t) or not re.search(r"\w", t):
                    continue
                a = off + c + x['start'] - p['in']; e = off + c + min(x['end'], p['out']) - p['in']
                words.append([a, max(e, a + 0.08), who, t])
        c += p['out'] - p['in']
    off += dur(os.path.join(PROJ, f))
words.sort()

cues = []; cur = []
def flush():
    if cur: cues.append(list(cur)); cur.clear()
for w in words:
    if cur:
        txt = ' '.join(c[3] for c in cur + [w])
        if (w[2] != cur[-1][2] or len(txt) > 84 or w[1] - cur[0][0] > 6.0 or w[0] - cur[-1][1] > 0.6
                or (re.search(r'[.?!]$', cur[-1][3]) and len(' '.join(c[3] for c in cur)) > 20)):
            flush()
    cur.append(w)
flush()


def wrap(s):
    if len(s) <= 42: return s
    ws = s.split(); best = None
    for i in range(1, len(ws)):
        l1, l2 = ' '.join(ws[:i]), ' '.join(ws[i:])
        sc = max(len(l1), len(l2))
        if best is None or sc < best[0]: best = (sc, l1 + '\n' + l2)
    return best[1]


ts = lambda t: f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}'
items = []; prev_who = None
for i, c in enumerate(cues):
    a = c[0][0]; b = c[-1][1]
    if i + 1 < len(cues): b = min(b + 0.4, cues[i + 1][0][0] - 0.02)
    txt = ' '.join(x[3] for x in c)
    if c[0][2] != prev_who: txt = '>> ' + txt
    prev_who = c[0][2]
    if items and b - a < 0.25:                    # fold a sliver cue into the previous one
        items[-1][1] = max(items[-1][1], a + 0.25, b)
        items[-1][2] += ('\n' if txt.startswith('>> ') else ' ') + txt
        continue
    items.append([a, b, txt])
for i in range(len(items) - 1):
    items[i][1] = min(items[i][1], items[i + 1][0] - 0.02)
assert all(b - a >= 0.2 for a, b, _ in items) and all(items[i][0] >= items[i - 1][1] for i in range(1, len(items))), 'bad cue timing'
srt = '\n'.join(f'{i + 1}\n{ts(a)} --> {ts(b)}\n' + '\n'.join(wrap(x) for x in t.split('\n')) + '\n' for i, (a, b, t) in enumerate(items))
for a_, b_ in EP.get('caption_fixes', []):
    srt = re.sub(a_, b_, srt)
os.makedirs(os.path.join(PROJ, 'exports/final'), exist_ok=True)
open(os.path.join(PROJ, 'exports/final/youtube-captions.srt'), 'w').write(srt)
print('cues', len(items), 'words', len(words), 'last end', round(items[-1][1], 2), 'total', round(off, 2))
