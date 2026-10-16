"""Remove sounds an AI enhancer invented in the host's silences, then write the gated host track.

Usage:
  python3 scripts/podcast/gate_host_audio.py <project> [--enhanced raw/host-audio-enhanced.wav] [--floor -45] [--out raw/host-audio-enhanced-gated.wav]

Adobe Podcast Enhance can turn the host mic's room noise into a short, low, voice-like sound while the
guest is talking (second episode: 8 spots, -24 to -38 dB, where the original mic sat at -50 to -58 dB and
the host said nothing; the owner heard one as "a very low voice for ~1 second, kinda creepy").
This script:
  1. scans: lists every span where the enhanced track is louder than -45 dBFS while the host has no
     transcript word nearby, and marks which spans the edit uses and whether the original mic was quiet
     there (invented) or not (a real laugh/"mm" the transcript missed);
  2. gates: silences the enhanced track (30 ms ramps) wherever the host has no word (+-0.4 s) AND the
     original mic is under --floor (+-0.2 s). Invented sounds become silence; speech and real sounds stay.
Writes <project>/raw/host-audio-enhanced-gated.wav. Pass that to assemble.py --host-audio.
Reads raw/host-audio.m4a (original) and edit/transcripts/host.json (Scribe words). Needs ffmpeg and numpy.
"""
import json, os, subprocess, sys

try:
    import numpy as np
except ImportError:
    sys.exit('needs numpy — pip3 install numpy')
args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
PROJ = os.path.abspath(args[0])
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
ENH = os.path.join(PROJ, opt('--enhanced', 'raw/host-audio-enhanced.wav'))
FLOOR = float(opt('--floor', '-45'))
OUT = os.path.join(PROJ, opt('--out', 'raw/host-audio-enhanced-gated.wav'))
SR = 48000; B = SR // 10                        # 100 ms analysis bins


def pcm(f):
    a = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(a, np.float32).copy()


def db(x):
    m = len(x) // B
    return 20 * np.log10(np.sqrt((x[:m * B].reshape(m, B) ** 2).mean(1)) + 1e-9)


E = pcm(ENH); H = pcm(os.path.join(PROJ, 'raw/host-audio.m4a'))
n = min(len(E), len(H)); nb = n // B + 1
Edb, Hdb = db(E[:n]), db(H[:n])
talk = np.zeros(nb, bool)
for x in json.load(open(os.path.join(PROJ, 'edit/transcripts/host.json')))['words']:
    if x['type'] not in ('word', 'audio_event'):
        continue
    s, e = x['start'], x['end']
    if e - s > 1.5:                             # Scribe stretches some words across silences
        s = e - 0.6
    talk[max(0, int((s - 0.4) * 10)):int((e + 0.4) * 10) + 1] = True

# 1. scan
pieces = []
if os.path.exists(os.path.join(PROJ, 'edit/chapters.json')):
    for c in json.load(open(os.path.join(PROJ, 'edit/chapters.json')))['chapters']:
        for p in c['pieces']:
            pieces.append((c['id'], p))
used = lambda t: next((cid for cid, p in pieces if p['in'] <= t <= p['out']
                       and not any(a <= t <= b for a, b in p.get('mute_host', []))), None)
flag = (Edb > -45) & ~talk[:len(Edb)]
i = 0; found = 0
while i < len(flag):
    if not flag[i]:
        i += 1; continue
    j = i
    while j < len(flag) and flag[j]:
        j += 1
    a, b = i / 10, j / 10; found += 1
    kind = 'INVENTED' if Hdb[i:j].max() < FLOOR else 'real sound, kept'
    print(f'raw {a:7.1f}-{b:7.1f}  enhanced {Edb[i:j].max():5.1f} dB  original {Hdb[i:j].max():5.1f} dB  '
          f'{kind}  {"in " + used(a) if used(a) else "not in the edit"}')
    i = j
print(found, 'spans where the enhanced host track sounds without a host word')

# 2. gate
loud = np.zeros(nb, bool); loud[:len(Hdb)] = Hdb > FLOOR
wide = loud.copy()
for k in (1, 2):
    wide[k:] |= loud[:-k]; wide[:-k] |= loud[k:]
keep = (talk | wide).astype(np.float32)
gain = np.convolve(np.repeat(keep, B)[:n], np.ones(int(0.03 * SR), np.float32) / int(0.03 * SR), 'same')
out = (E[:n] * gain).astype(np.float32)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', OUT],
               input=out.tobytes(), check=True)
spoken = talk[:len(Edb)]
change = np.abs(db(out)[spoken] - Edb[spoken]).max() if spoken.any() else 0.0
print(f'gated {float(1 - keep.mean()) * 100:.1f}% of the track; max level change where the host speaks: {change:.2f} dB -> {OUT}')
