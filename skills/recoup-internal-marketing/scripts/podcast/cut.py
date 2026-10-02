"""Cut one chapter's media (both cameras + the mixed audio) from the master cut list.

Usage:
  python3 scripts/podcast/cut.py <project> <chapter-id>                 # cameras + mix.m4a
  python3 scripts/podcast/cut.py <project> <chapter-id> --audio-only \
      [--host-audio raw/host-audio-enhanced.wav] [--mix-name mix-enhanced.m4a]

<project>/edit/chapters.json holds, per chapter, `pieces` in RAW recording seconds:
  {"in": 957.55, "out": 959.40}                       plain piece
  "mute_host": [[a, b], ...] / "mute_guest": [[a, b]]  silence one track inside the piece (raw seconds)
  "host_only": true                                    guest track silent for the piece (a host splice)
  "video_from": 957.00                                 take the PICTURE from another raw time (cover the
                                                       splice with a full-frame card so lips never show)
and top-level `offsets` {"guest": 0.12, "host": 0.133}: seconds the camera file lags its audio track
(measure with camera_check.py). Output goes to <project>/comp/chapters/<id>/assets/.
Needs ffmpeg on PATH.
"""
import json, os, subprocess, sys

args = sys.argv[1:]
if len(args) < 2:
    sys.exit(__doc__)
PROJ, CID = os.path.abspath(args[0]), args[1]
AUDIO_ONLY = '--audio-only' in args
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
HOST_AUDIO = os.path.join(PROJ, opt('--host-audio', 'raw/host-audio.m4a'))
GUEST_AUDIO = os.path.join(PROJ, 'raw/guest-audio.m4a')
MIX_NAME = opt('--mix-name', 'mix.m4a')
spec = json.load(open(os.path.join(PROJ, 'edit/chapters.json')))
ch = [c for c in spec['chapters'] if c['id'] == CID][0]
P = ch['pieces']; off = spec['offsets']
out = os.path.join(PROJ, 'comp/chapters', CID, 'assets'); os.makedirs(out, exist_ok=True)
FIXED = os.path.join(PROJ, 'raw/host-video-fixed.mp4')          # optional, from fix_host_video.py
FIXED_T0 = spec.get('host_video_fixed_start', 6.0)


def run(a):
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, check=True)


for who in ([] if AUDIO_ONLY else ['guest', 'host']):
    src = os.path.join(PROJ, f'raw/{who}-video.mkv'); shift = 0.0
    if who == 'host' and os.path.exists(FIXED):
        src, shift = FIXED, FIXED_T0      # fixed file: t = raw - FIXED_T0, constant 30 fps
    f = []
    for i, p in enumerate(P):
        a = p.get('video_from', p['in']) + off[who] - shift; d = p['out'] - p['in']
        f.append(f"[0:v]trim=start={a:.3f}:duration={d:.3f},setpts=PTS-STARTPTS,fps=30,scale=896:504,setsar=1[v{i}]")
    f.append(''.join(f'[v{i}]' for i in range(len(P))) + f"concat=n={len(P)}:v=1:a=0[v]")
    run(['-i', src, '-filter_complex', ';'.join(f), '-map', '[v]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', f'{out}/{who}.mp4'])


def mutes(p, key):
    rs = [(a - p['in'], b - p['in']) for a, b in p.get(key, []) if b > p['in'] and a < p['out']]
    return ''.join(f"volume=enable='between(t,{max(a, 0):.3f},{b:.3f})':volume=0," for a, b in rs)


f = []
for i, p in enumerate(P):
    d = p['out'] - p['in']; fade = f"afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015"
    f.append(f"[0:a]atrim=start={p['in']:.3f}:duration={d:.3f},asetpts=PTS-STARTPTS,{mutes(p, 'mute_host')}{fade}[h{i}]")
    gv = 'volume=0,' if p.get('host_only') else mutes(p, 'mute_guest')
    f.append(f"[1:a]atrim=start={p['in']:.3f}:duration={d:.3f},asetpts=PTS-STARTPTS,{gv}{fade}[g{i}]")
    f.append(f"[h{i}][g{i}]amix=inputs=2:normalize=0,aformat=channel_layouts=stereo[m{i}]")
f.append(''.join(f'[m{i}]' for i in range(len(P))) + f"concat=n={len(P)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
run(['-i', HOST_AUDIO, '-i', GUEST_AUDIO, '-filter_complex', ';'.join(f), '-map', '[a]', '-ar', '48000', '-c:a', 'aac',
     '-b:a', '256k', f'{out}/{MIX_NAME}'])
print(CID, 'cut:', round(sum(p['out'] - p['in'] for p in P), 2), 's ->', out)
