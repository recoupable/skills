"""Check both Restream cameras before editing: per-file sync offset and dropped-frame stretches.

Usage:
  python3 scripts/podcast/camera_check.py <project>

1. Sync: correlates each camera file's embedded audio against its per-speaker audio track at two points
   and prints the offset (positive = the video file lags the track). Put the result in chapters.json
   "offsets" ({"guest": .., "host": ..}); measured 0.12 / 0.133 s on the first episode, constant.
2. Frame rate: counts video packets per second. Restream dropped the HOST camera to ~14 fps for long
   stretches on the first episode (guest stayed at 30): every frame shows twice and lips read as out of
   sync even though timing is right. Spans under 22 fps where the host is speaking are written to
   <project>/edit/interp-spans.json for fix_host_video.py (needs edit/transcripts/host.json).
Needs ffmpeg/ffprobe and numpy.
"""
import collections, json, os, subprocess, sys

try:
    import numpy as np
except ImportError:
    sys.exit('needs numpy — pip3 install numpy')
if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = os.path.abspath(sys.argv[1])


def env(f, ss, t=240):
    a = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ss), '-t', str(t), '-i', f, '-vn', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.abs(np.frombuffer(a, np.int16).astype(float)); x = x[:len(x) // 8 * 8].reshape(-1, 8).mean(1)
    return x - x.mean()


for who in ('guest', 'host'):
    for ss in (60, 1200):
        a = env(f'{PROJ}/raw/{who}-audio.m4a', ss); v = env(f'{PROJ}/raw/{who}-video.mkv', ss)
        n = min(len(a), len(v))
        if n < 6000:
            continue
        c = np.correlate(v[:n], a[2000:n - 2000], 'valid'); lag = int(np.argmax(c)) - 2000
        print(f'{who} @{ss}s: video lags track by {lag / 1000:+.3f}s')

spans_out = []
W = []
if os.path.exists(f'{PROJ}/edit/transcripts/host.json'):
    W = [x for x in json.load(open(f'{PROJ}/edit/transcripts/host.json'))['words'] if x['type'] == 'word']
for who in ('guest', 'host'):
    pts = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'packet=pts_time', '-of', 'csv=p=0',
                          f'{PROJ}/raw/{who}-video.mkv'], capture_output=True, text=True).stdout.split()
    c = collections.Counter(int(float(x)) for x in pts if x)
    end = max(c) if c else 0
    low = [s for s in range(end + 1) if c.get(s, 0) < 22]
    spans = []
    for s in low:
        if spans and s - spans[-1][1] <= 3:
            spans[-1][1] = s
        else:
            spans.append([s, s])
    spans = [x for x in spans if x[1] - x[0] >= 3]
    print(f'{who}: {sum(b - a for a, b in spans)}s under 22 fps in {len(spans)} stretches')
    if who == 'host' and W:
        lows = set(low); talk = []
        for x in W:
            a, b = x['start'] - 0.8, min(x['end'], x['start'] + 1.5) + 0.8
            if talk and a - talk[-1][1] < 1.5:
                talk[-1][1] = b
            else:
                talk.append([a, b])
        for a, b in talk:
            for s in range(int(a), int(b) + 1):
                if s in lows:
                    if spans_out and s - spans_out[-1][1] <= 2:
                        spans_out[-1][1] = s + 1
                    else:
                        spans_out.append([s, s + 1])
if spans_out:
    merged = []
    for a, b in ([max(6.0, a - 0.5), b + 0.5] for a, b in spans_out):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    json.dump(merged, open(f'{PROJ}/edit/interp-spans.json', 'w'))
    print(f'host speaking while under 22 fps: {len(merged)} spans, {round(sum(b - a for a, b in merged))}s '
          f'(~{round(sum(b - a for a, b in merged) * 8.3 / 60)} min to interpolate on an Intel laptop) -> edit/interp-spans.json')
