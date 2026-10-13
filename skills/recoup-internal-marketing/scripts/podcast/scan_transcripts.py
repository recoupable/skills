"""Scan the per-speaker Scribe transcripts for the things a cut list needs before anyone writes it.

Usage:
  python3 scripts/podcast/scan_transcripts.py <project>

Inputs:  <project>/edit/transcripts/{host,guest}.json (from transcribe.py)
Outputs: <project>/edit/words-{host,guest}.txt  one word per line: start end text (grep these for in/out points)
Prints:
  - DEAD AIR: both tracks wordless for >3 s. Inside the interview this is usually a line said while
    muted (2026-10-13: the host's sign-off was lost this way; the host's later repeat was spliced in).
  - HOST FRAGMENTS: a short host burst (<3 s), said while the guest is talking, then >8 s of host
    silence. These are early starts of the next question; mute them in place and splice onto the restart.
  - COVERAGE: first/last word per track, to confirm Scribe returned the whole recording.
Word ends longer than 1.5 s are capped (Scribe stretches a word across a mute). The merged transcript
clamps segment starts, so it can show a fragment minutes away from where it was said; always take timecodes from the word files, not from transcript-merged.md.
"""
import json, os, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = os.path.abspath(sys.argv[1])
W = {}
for who in ('host', 'guest'):
    W[who] = [dict(x) for x in json.load(open(f'{PROJ}/edit/transcripts/{who}.json'))['words'] if x['type'] == 'word']
    for x in W[who]:  # Scribe stretches a word across a mute gap; keep its start, cap its length
        if x['end'] - x['start'] > 1.5:
            x['end'] = x['start'] + 0.5
    with open(f'{PROJ}/edit/words-{who}.txt', 'w') as f:
        for x in W[who]:
            f.write(f"{x['start']:8.2f} {x['end']:8.2f} {x['text']}\n")
    print(f"COVERAGE {who}: {len(W[who])} words, {W[who][0]['start']:.1f}s to {W[who][-1]['end']:.1f}s")

allw = sorted([(x['start'], x['end'], who, x['text']) for who in W for x in W[who]])
print('\nDEAD AIR (>3 s, both tracks):')
end = allw[0][1]
for i in range(1, len(allw)):
    gap = allw[i][0] - end
    if gap > 3:
        nxt = ' '.join(a[3] for a in allw[i:i + 6])
        print(f"  {end:7.1f}-{allw[i][0]:7.1f} ({gap:4.1f}s)  ..{allw[i-1][2]}: {allw[i-1][3]}  ->  {allw[i][2]}: {nxt}")
    end = max(end, allw[i][1])

print('\nHOST FRAGMENTS (early starts to mute + splice onto the restart; check each by ear):')
H, G = W['host'], W['guest']; i = 0
guest_talking = lambda t: any(g['start'] < t and g['end'] > t - 1.5 for g in G)
while i < len(H):
    j = i
    while j + 1 < len(H) and H[j + 1]['start'] - H[j]['end'] < 1.0:
        j += 1
    burst = H[j]['end'] - H[i]['start']
    after = H[j + 1]['start'] - H[j]['end'] if j + 1 < len(H) else 0
    before = H[i]['start'] - H[i - 1]['end'] if i else 99
    if burst < 3 and after > 8 and before > 1.0 and guest_talking(H[i]['start']):
        restart = ' '.join(x['text'] for x in H[j + 1:j + 7])
        print(f"  {H[i]['start']:7.2f}-{H[j]['end']:7.2f} \"{' '.join(x['text'] for x in H[i:j+1])}\"  restart {H[j+1]['start']:7.2f} \"{restart}\"")
    i = j + 1
