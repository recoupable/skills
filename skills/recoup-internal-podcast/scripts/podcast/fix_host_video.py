"""Rebuild the host camera at a constant 30 fps, motion-interpolating the stretches where Restream
dropped frames while the host was speaking (edit/interp-spans.json from camera_check.py).

Usage:
  python3 scripts/podcast/fix_host_video.py <project> [start_seconds=6.0]

Writes <project>/raw/host-video-fixed.mp4 where t = raw - start. cut.py picks it up automatically
(set "host_video_fixed_start" in chapters.json if start isn't 6.0). Interpolation runs ~8x slower than
realtime on an Intel laptop; the rest is a fast fps conversion. Set FIX_WORKERS=<n> to render segments in
parallel. Segments land in edit/fixseg/ so an interrupted run resumes. Check the result with lipsync.py and a frame strip before cutting.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = os.path.abspath(sys.argv[1]); T0 = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
SRC = f'{PROJ}/raw/host-video.mkv'
END = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', SRC],
                           capture_output=True, text=True).stdout)
spans = json.load(open(f'{PROJ}/edit/interp-spans.json'))
segs = []; t = T0
for a, b in spans:
    if b <= t:
        continue
    if a > t:
        segs.append((t, a, False))
    segs.append((max(a, t), b, True)); t = b
if t < END:
    segs.append((t, END, False))
D = f'{PROJ}/edit/fixseg'; os.makedirs(D, exist_ok=True)
lst = [f'{D}/{i:03d}.mp4' for i in range(len(segs))]


def render(i):
    (a, b, interp), out = segs[i], lst[i]
    if os.path.exists(out):
        return
    vf = ('minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1' if interp else 'fps=30') + ',scale=896:504,setsar=1'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-i', SRC, '-vf', vf, '-frames:v', str(round((b - a) * 30)),
                    '-fps_mode', 'cfr', '-c:v', 'libx264', '-crf', '16', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-an', out + '.tmp.mp4'], check=True)
    os.replace(out + '.tmp.mp4', out)
    print(f'{i:03d} {a:8.2f}-{b:8.2f} {"INTERP" if interp else "cfr"}', flush=True)


# Segments are independent; FIX_WORKERS > 1 renders them in parallel (minterpolate is mostly single-threaded).
with ThreadPoolExecutor(int(os.environ.get('FIX_WORKERS', '1'))) as ex:
    list(ex.map(render, range(len(segs))))
open(f'{D}/list.txt', 'w').write(''.join(f"file '{os.path.basename(x)}'\n" for x in lst))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{D}/list.txt', '-c', 'copy', f'{PROJ}/raw/host-video-fixed.mp4'], check=True)
print('fixed:', f'{PROJ}/raw/host-video-fixed.mp4', 'starts at raw', T0)
