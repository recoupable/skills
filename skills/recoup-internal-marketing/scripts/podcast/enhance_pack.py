"""Pack only the audio the cut plays into one file for Adobe Podcast Enhance, then unpack the enhanced result.

Usage:
  python3 scripts/podcast/enhance_pack.py <project> pack   host|guest
  python3 scripts/podcast/enhance_pack.py <project> unpack host|guest <enhanced.wav>

pack   -> <project>/enhance/<track>-used.wav + <track>-used-map.json. Spans = the union of every piece in
          edit/chapters.json that plays this track (host_only pieces skipped for the guest), padded PAD s each
          side, minus this track's own silences of QUIET_MIN s or more (the other person talking). Segments are
          joined with GAP s of silence so the enhancer never blends across a join.
unpack -> <project>/raw/<track>-audio-enhanced.wav: full raw length, the enhanced audio back at its raw times,
          silence everywhere else. cut.py only reads inside the pieces, so the silence is never heard.
          Pass it to assemble.py with --host-audio / --guest-audio.

Why: a 33-minute raw track held ~24 minutes the cut uses (2026-10-14). Packing saves Adobe's free-tier
quota (30 min/file, 1 h/day), upload/processing/download time, and the split-and-rejoin step.
Re-pack after any cut-list change that adds audio (a restored span would otherwise play un-enhanced).
Test the round trip on the unenhanced pack first: unpack it and check 0 ms lag at several raw times.
Needs ffmpeg/ffprobe.
"""
import json, os, subprocess, sys

args = sys.argv[1:]
if len(args) < 3 or args[1] not in ('pack', 'unpack') or args[2] not in ('host', 'guest'):
    sys.exit(__doc__)
PROJ, MODE, TRACK = os.path.abspath(args[0]), args[1], args[2]
PAD, GAP, SR = 0.5, 0.5, 48000
QUIET_DB, QUIET_MIN = -50, 3.0
SRC = os.path.join(PROJ, f'raw/{TRACK}-audio.m4a')
OUT = os.path.join(PROJ, f'enhance/{TRACK}-used.wav'); MAP = os.path.join(PROJ, f'enhance/{TRACK}-used-map.json')
os.makedirs(os.path.join(PROJ, 'enhance'), exist_ok=True)


def run(a):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + a, check=True)


def quiet():
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', SRC, '-af', f'silencedetect=n={QUIET_DB}dB:d={QUIET_MIN}', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    st = [float(l.split('silence_start: ')[1]) for l in o.splitlines() if 'silence_start' in l]
    en = [float(l.split('silence_end: ')[1].split()[0]) for l in o.splitlines() if 'silence_end' in l]
    return [(a + PAD, b - PAD) for a, b in zip(st, en)]


def minus(a, b, Q):
    out = [[a, b]]
    for qa, qb in Q:
        nxt = []
        for x, y in out:
            if qb <= x or qa >= y:
                nxt.append([x, y]); continue
            if qa > x: nxt.append([x, qa])
            if qb < y: nxt.append([qb, y])
        out = nxt
    return [(x, y) for x, y in out if y - x > 0.05]


def spans():
    CH = json.load(open(os.path.join(PROJ, 'edit/chapters.json'))); Q = quiet()
    s = sorted(seg for c in CH['chapters'] for p in c['pieces'] if not (TRACK == 'guest' and p.get('host_only'))
               for seg in minus(max(0, p['in'] - PAD), p['out'] + PAD, Q))
    m = []
    for a, b in s:
        if m and a <= m[-1][1] + GAP: m[-1][1] = max(m[-1][1], b)
        else: m.append([a, b])
    return [[round(a, 3), round(b, 3)] for a, b in m]


if MODE == 'pack':
    S = spans(); f = []; L = []; t = 0.0
    for i, (a, b) in enumerate(S):
        f.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample={SR},aformat=channel_layouts=mono[s{i}];')
        f.append(f'anullsrc=r={SR}:cl=mono,atrim=0:{GAP}[g{i}];')
        L.append({'raw_in': a, 'raw_out': b, 'packed_in': round(t, 3)}); t += (b - a) + GAP
    run(['-i', SRC, '-filter_complex', ''.join(f) + ''.join(f'[s{i}][g{i}]' for i in range(len(S))) +
         f'concat=n={2 * len(S)}:v=0:a=1[o]', '-map', '[o]', '-c:a', 'pcm_s16le', OUT])
    json.dump({'track': TRACK, 'pad': PAD, 'gap': GAP, 'segments': L}, open(MAP, 'w'), indent=1)
    print(f'{len(S)} segments, {t / 60:.2f} min -> {OUT}' + ('  (OVER 30 min: Adobe free tier rejects it; split at a gap)' if t > 1800 else ''))
else:
    M = json.load(open(MAP)); E = os.path.abspath(args[3])
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC]))
    f = []
    for i, s in enumerate(M['segments']):
        d = s['raw_out'] - s['raw_in']
        f.append(f"[1:a]atrim={s['packed_in']}:{s['packed_in'] + d},asetpts=PTS-STARTPTS,aresample={SR},"
                 f"aformat=channel_layouts=mono,adelay={int(round(s['raw_in'] * 1000))}[s{i}];")
    n = len(M['segments'])
    dest = os.path.join(PROJ, f'raw/{TRACK}-audio-enhanced.wav')
    run(['-f', 'lavfi', '-i', f'anullsrc=r={SR}:cl=mono', '-i', E, '-filter_complex',
         f'[0:a]atrim=0:{dur}[b];' + ''.join(f) + '[b]' + ''.join(f'[s{i}]' for i in range(n)) +
         f'amix=inputs={n + 1}:normalize=0:duration=first[o]', '-map', '[o]', '-c:a', 'pcm_s16le', dest])
    print('->', dest)
