"""Assemble the final episode from approved blocks into ONE upload-ready file.

Usage:
  python3 scripts/podcast/assemble.py <project> [--host-audio raw/host-audio-enhanced.wav]

Blocks, in order: <project>/exports/opening.mp4 (cold open + intro), then exports/<chapter>.mp4 for every
chapter in edit/chapters.json except "ch00" (the cold open lives inside opening.mp4).
--host-audio swaps in a cleaned host track (e.g. Adobe Podcast Enhance, joined back to full length):
each chapter's mix is re-cut with the same pieces/mutes (cut.py --audio-only); the opening keeps its
audio (the host is muted in the cold open). No video re-render is needed for an audio change.

Video is re-encoded once, uniformly (H.264 High 4.1, CFR 30, bt709). Do not stream-copy-join the
blocks: the opening and the chapters come from different encoders, and Spotify for Creators rejected
the stream-copied file ("This video can't be published") although every player accepted it.
Audio: joined, two-pass loudnorm to -14 LUFS / -1 dBTP, AAC 256k stereo.
Outputs in <project>/exports/final/: episode.mp4, episode-audio.m4a, youtube-chapters.txt.
Needs ffmpeg/ffprobe.
"""
import json, os, subprocess, sys

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
PROJ = os.path.abspath(args[0]); HERE = os.path.dirname(os.path.abspath(__file__))
HOST = args[args.index('--host-audio') + 1] if '--host-audio' in args else None
E = f'{PROJ}/exports'; F = f'{E}/final'; os.makedirs(F, exist_ok=True)
CH = [c for c in json.load(open(f'{PROJ}/edit/chapters.json'))['chapters'] if c['id'] != 'ch00']
blocks = [(f'{E}/opening.mp4', 'Cold open + intro', None)] + [(f"{E}/{c['id']}.mp4", c['title'], c['id']) for c in CH]
for b, _, _ in blocks:
    if not os.path.exists(b):
        sys.exit('missing block: ' + b)
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', f], capture_output=True, text=True).stdout)
run = lambda a: subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, check=True)

t = 0.0; lines = []
for b, title, _ in blocks:
    lines.append(f"{int(t // 60)}:{int(t % 60):02d} {title}"); t += dur(b)
open(f'{F}/youtube-chapters.txt', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))

# audio sources per block
auds = []
for b, _, cid in blocks:
    if HOST and cid:
        subprocess.run([sys.executable, f'{HERE}/cut.py', PROJ, cid, '--audio-only', '--host-audio', HOST, '--mix-name', 'mix-final.m4a'], check=True)
        auds.append(f'{PROJ}/comp/chapters/{cid}/assets/mix-final.m4a')
    else:
        auds.append(b)
inp = sum((['-i', a] for a in auds), [])
fc = ''.join(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];' for i in range(len(auds))) + \
     ''.join(f'[a{i}]' for i in range(len(auds))) + f'concat=n={len(auds)}:v=0:a=1[a]'
run(inp + ['-filter_complex', fc, '-map', '[a]', '-c:a', 'pcm_s24le', f'{F}/audio.wav'])
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'{F}/audio.wav', '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
open(f'{F}/list.txt', 'w').write(''.join(f"file '{b}'\n" for b, _, _ in blocks))
run(['-f', 'concat', '-safe', '0', '-i', f'{F}/list.txt', '-i', f'{F}/audio.wav', '-map', '0:v', '-map', '1:a',
     '-c:v', 'libx264', '-preset', 'faster', '-crf', '17', '-profile:v', 'high', '-level:v', '4.1', '-pix_fmt', 'yuv420p',
     '-r', '30', '-fps_mode', 'cfr', '-g', '60', '-bf', '2', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
     '-af', ln, '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', f'{F}/episode.mp4'])
run(['-i', f'{F}/audio.wav', '-af', ln, '-c:a', 'aac', '-b:a', '192k', f'{F}/episode-audio.m4a'])
os.remove(f'{F}/audio.wav')
bad = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{F}/episode.mp4', '-f', 'null', '-'], capture_output=True, text=True).stderr.strip()
print('decode check:', 'clean' if not bad else bad[:300])
print('loudness in:', m['input_i'], 'LUFS ->', f'{F}/episode.mp4')
