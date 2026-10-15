"""Transcribe each speaker track with ElevenLabs Scribe (word timestamps), then write a merged,
speaker-labelled transcript. Never Whisper (owner rule).

Usage:
  ELEVENLABS_API_KEY=... python3 scripts/podcast/transcribe.py <project>

Inputs:  <project>/raw/host-audio.m4a, <project>/raw/guest-audio.m4a (Restream per-speaker tracks)
Outputs: <project>/edit/transcripts/{host,guest}.json  (raw Scribe JSON; words[] with start/end)
         <project>/edit/transcript-merged.md            (timecoded, both speakers interleaved)
Scribe sometimes stretches one word across a long silence; the merge clamps any word >1.5s to its
last 0.6s, otherwise speaker turns land minutes early.
"""
import json, os, subprocess, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = os.path.abspath(sys.argv[1]); KEY = os.environ.get('ELEVENLABS_API_KEY')
if not KEY:
    sys.exit('set ELEVENLABS_API_KEY')
os.makedirs(f'{PROJ}/edit/transcripts', exist_ok=True)
for who in ('host', 'guest'):
    out = f'{PROJ}/edit/transcripts/{who}.json'
    if os.path.exists(out):
        print(who, 'exists, skipping'); continue
    for model in ('scribe_v2', 'scribe_v1'):
        r = subprocess.run(['curl', '-s', '-o', out, '-w', '%{http_code}', '-X', 'POST', 'https://api.elevenlabs.io/v1/speech-to-text',
                            '-H', f'xi-api-key: {KEY}', '-F', f'model_id={model}', '-F', f'file=@{PROJ}/raw/{who}-audio.m4a',
                            '-F', 'language_code=en', '-F', 'timestamps_granularity=word', '-F', 'tag_audio_events=true',
                            '-F', 'diarize=false'], capture_output=True, text=True)
        print(who, model, 'HTTP', r.stdout)
        if r.stdout == '200':
            break
    else:
        sys.exit(f'{who}: transcription failed: ' + open(out).read()[:300])

segs = []
for who, name in (('host', 'HOST'), ('guest', 'GUEST')):
    W = [dict(x) for x in json.load(open(f'{PROJ}/edit/transcripts/{who}.json'))['words'] if x['type'] in ('word', 'audio_event')]
    cur = None
    for x in W:
        if x['end'] - x['start'] > 1.5:
            x['start'] = x['end'] - 0.6
        if cur and x['start'] - cur['end'] > 1.2:
            segs.append(cur); cur = None
        cur = cur or {'who': name, 'start': x['start'], 'end': x['end'], 'text': ''}
        cur['end'] = x['end']; cur['text'] = (cur['text'] + ' ' + x['text']).strip()
    if cur:
        segs.append(cur)
segs.sort(key=lambda s: s['start'])
fmt = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"
with open(f'{PROJ}/edit/transcript-merged.md', 'w') as f:
    f.write('# Merged transcript (ElevenLabs Scribe, per-speaker tracks; raw-file timecodes)\n\n')
    for s in segs:
        f.write(f"**[{fmt(s['start'])}] {s['who']}:** {s['text']}\n\n")
print(len(segs), 'segments ->', f'{PROJ}/edit/transcript-merged.md')
