"""Per-section arrangement density: percussive share, onset rate, high-band share and sub share,
to see whether a section "thins" without getting quieter. Optional local probe; not needed for
the report.

usage: arrangement_density.py <audio file> <measurement.json> [--slice START END]

<audio file> is a local copy of the song (any format the audio library can decode).
measurement.json is the POST /api/songs/moments response (its sections are read).
--slice START END prints a finer look at that span in 4-second slices (seconds).

Needs numpy and librosa: pip3 install librosa
"""
import json
import sys


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help") or len(args) < 2:
        print(__doc__.strip())
        sys.exit(0 if args and args[0] in ("-h", "--help") else 2)
    span = None
    if "--slice" in args:
        i = args.index("--slice")
        span = (float(args[i + 1]), float(args[i + 2]))
        args = args[:i] + args[i + 3:]
    try:
        import numpy as np
        import librosa
    except ImportError:
        sys.exit("arrangement_density.py needs numpy and librosa: pip3 install librosa")

    y, sr = librosa.load(args[0], sr=22050, mono=True)
    meas = json.load(open(args[1]))
    H, P = librosa.effects.hpss(y)
    hop = 512
    rmsH = librosa.feature.rms(y=H, hop_length=hop)[0]
    rmsP = librosa.feature.rms(y=P, hop_length=hop)[0]
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=hop, units="time")
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    t = librosa.frames_to_time(np.arange(len(rmsH)), sr=sr, hop_length=hop)

    def perc_share(m):
        return float(np.sum(rmsP[m] ** 2) / (np.sum(rmsH[m] ** 2) + np.sum(rmsP[m] ** 2) + 1e-12) * 100)

    def band_share(m, lo=None, hi=None):
        seg = S[:, m]
        sel = np.ones_like(freqs, dtype=bool)
        if lo is not None:
            sel &= freqs >= lo
        if hi is not None:
            sel &= freqs < hi
        return float(seg[sel].sum() / (seg.sum() + 1e-12) * 100)

    print(f"{'section':12} {'start':>6} {'perc%':>6} {'onsets/s':>9} {'hi>2k%':>7} {'sub<120%':>9} {'rms dB':>7}")
    for s in meas["sections"]:
        m = (t >= s["start"]) & (t < s["end"])
        on = float(np.sum((onsets >= s["start"]) & (onsets < s["end"])) / max(1e-6, s["end"] - s["start"]))
        db = float(20 * np.log10(np.sqrt(np.mean((rmsH[m] ** 2 + rmsP[m] ** 2))) + 1e-9))
        print(f"{s['label']:12} {s.get('mmss') or mmss(s['start']):>6} {perc_share(m):6.1f} {on:9.2f} "
              f"{band_share(m, lo=2000):7.1f} {band_share(m, hi=120):9.1f} {db:7.1f}")

    if span:
        a0, a1 = span
        print(f"-- {mmss(a0)}–{mmss(a1)} in 4 s slices (perc%, onsets/s, hi>2k%)")
        a = a0
        while a < a1:
            m = (t >= a) & (t < a + 4)
            on = float(np.sum((onsets >= a) & (onsets < a + 4)) / 4)
            print(f"  {mmss(a)}  {perc_share(m):5.1f}  {on:5.2f}  {band_share(m, lo=2000):5.1f}")
            a += 4


if __name__ == "__main__":
    main()
