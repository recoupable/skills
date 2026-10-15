"""Audio-only rough cut of edit/chapters.json, for the owner to check every splice by ear before any
graphics are built or rendered (a bad splice found after rendering costs a chapter re-render).

Usage:
  python3 scripts/podcast/rough_audio.py <project>

Inputs:  <project>/raw/{host,guest}-audio.m4a, <project>/edit/chapters.json
Outputs: <project>/exports/rough-cut-audio.m4a          pieces in order, mute_* ranges silenced,
                                                       host_only pieces from the host track alone
         <project>/exports/rough-cut-audio-chapters.txt chapter start times in the rough cut
Takes ~1 min for a 30 min episode. Reveal both files in Finder for review.
"""
import json, os, shutil, subprocess, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = os.path.abspath(sys.argv[1]); TMP = f'{PROJ}/exports/rough'
os.makedirs(TMP, exist_ok=True)
d = json.load(open(f'{PROJ}/edit/chapters.json'))


def silence(ranges, start):
    if not ranges:
        return 'anull'
    return ','.join(f"volume=enable='between(t,{a - start:.3f},{b - start:.3f})':volume=0" for a, b in ranges)


parts, marks, t = [], [], 0.0
for c in d['chapters']:
    marks.append((t, c['id'], c['title']))
    for p in c['pieces']:
        i, dur = p['in'], p['out'] - p['in']
        out = f'{TMP}/p{len(parts):03d}.wav'
        fade = f'afade=t=in:d=0.02,afade=t=out:st={dur - 0.03:.3f}:d=0.03'
        if p.get('host_only'):
            cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(i), '-t', str(dur), '-i', f'{PROJ}/raw/host-audio.m4a',
                   '-af', fade, '-ar', '48000', '-ac', '1', out]
        else:
            fc = (f"[0:a]{silence(p.get('mute_guest'), i)}[g];[1:a]{silence(p.get('mute_host'), i)}[h];"
                  f"[g][h]amix=inputs=2:normalize=0,{fade}[a]")
            cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(i), '-t', str(dur), '-i', f'{PROJ}/raw/guest-audio.m4a',
                   '-ss', str(i), '-t', str(dur), '-i', f'{PROJ}/raw/host-audio.m4a',
                   '-filter_complex', fc, '-map', '[a]', '-ar', '48000', '-ac', '1', out]
        subprocess.run(cmd, check=True)
        parts.append(out); t += dur
with open(f'{TMP}/list.txt', 'w') as f:
    f.write(''.join(f"file '{os.path.basename(p)}'\n" for p in parts))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{TMP}/list.txt', '-af', 'loudnorm=I=-16',
                '-c:a', 'aac', '-b:a', '160k', f'{PROJ}/exports/rough-cut-audio.m4a'], check=True)
shutil.rmtree(TMP)
with open(f'{PROJ}/exports/rough-cut-audio-chapters.txt', 'w') as f:
    f.write(''.join(f"{int(s // 60)}:{int(s % 60):02d} {cid} {title}\n" for s, cid, title in marks))
print(f'rough cut {int(t // 60)}:{int(t % 60):02d} -> {PROJ}/exports/rough-cut-audio.m4a')
