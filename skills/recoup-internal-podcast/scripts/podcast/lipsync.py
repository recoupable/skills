"""Measure lip sync: mouth-region motion vs voice envelope. Positive = picture lags the voice.

Usage:
  CROP=w:h:x:y python3 scripts/podcast/lipsync.py <video> <audio> <start_s> [<start_s> ...]

Pick CROP by drawing it on a frame first (ffmpeg drawbox) and confirming it covers the MOUTH; a box
that misses half the mouth gives weak, misleading correlations (first episode: 0.07-0.2 until fixed).
Use 30-45s windows where that person is talking. When the raw recording measures in sync but viewers
see drift, check the camera's frame rate (camera_check.py) before blaming the edit.
"""
import os, subprocess, sys

try:
    import numpy as np
except ImportError:
    sys.exit('needs numpy — pip3 install numpy')
if len(sys.argv) < 4:
    sys.exit(__doc__)
CROP = os.environ.get('CROP', '170:100:350:215')


def motion(f, ss, dur):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ss), '-t', str(dur), '-i', f, '-vf', f'fps=30,crop={CROP},scale=68:40,format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 40, 68).astype(float)
    return np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))


def env(f, ss, dur):
    a = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ss), '-t', str(dur), '-i', f, '-vn', '-ac', '1', '-ar', '3000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.abs(np.frombuffer(a, np.int16).astype(float)); n = len(x) // 100
    return x[:n * 100].reshape(n, 100).mean(1)


v, a = sys.argv[1], sys.argv[2]
for ss in map(float, sys.argv[3:]):
    m = motion(v, ss, 40); e = env(a, ss, 40); n = min(len(m), len(e))
    if n < 60 or m[:n].std() == 0 or e[:n].std() == 0:
        print(f'{ss:7.1f}: silent or too short'); continue
    m = (m[:n] - m[:n].mean()) / m[:n].std(); e = (e[:n] - e[:n].mean()) / e[:n].std()
    sc = {L: np.dot(m[max(0, L):n + min(0, L)], e[max(0, -L):n - max(0, L)]) / n for L in range(-45, 46)}
    L = max(sc, key=sc.get)
    print(f'{ss:7.1f}: picture lags voice {L / 30:+.2f}s (corr {sc[L]:.2f})')
