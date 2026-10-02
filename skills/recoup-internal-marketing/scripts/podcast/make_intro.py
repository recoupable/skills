"""Build the episode's Wire intro (7s: rights-desk kinetic open -> dark frame with the Recoup Podcast
lockup, the episode title word by word, the guest, a topics ticker) and the opening block.

Usage:
  python3 scripts/podcast/make_intro.py <project> --show-assets <dir with recoup-podcast-white-transparent.png + intro-sting.wav>

Reads <project>/episode.json: title, date (YYYY-MM-DD), guest.name, guest.role, topics[] (6-8 short beats).
Writes <project>/comp/intro/ (HyperFrames project). Then render it and join the cold open in front:
  (cd <project>/comp/intro && npx --yes hyperframes render -o ../../exports/intro.mp4)
  ffmpeg -i exports/ch00.mp4 -i exports/intro.mp4 -filter_complex "[0:v]fps=30,format=yuv420p,setsar=1[v0];[1:v]fps=30,format=yuv420p,setsar=1[v1];[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -c:a aac -b:a 256k exports/opening.mp4
The show lockup PNG and Sid's sting are private brand assets (not in this public skill): pass their folder.
Chosen in a three-way cookoff (wire / signal waveform / paper marker) on the first episode.
"""
import argparse, html, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--show-assets', required=True)
A = ap.parse_args(); PROJ = os.path.abspath(A.project)
EP = json.load(open(f'{PROJ}/episode.json'))
D = f'{PROJ}/comp/intro'; os.makedirs(f'{D}/assets/logos', exist_ok=True)
shutil.copytree(os.path.join(HERE, '..', '..', 'brand', 'fonts'), f'{D}/assets/fonts', dirs_exist_ok=True)
for src, dst in (('recoup-podcast-white-transparent.png', 'logos/recoup-podcast-white-transparent.png'), ('intro-sting.wav', 'sting.wav')):
    p = os.path.join(A.show_assets, src)
    if not os.path.exists(p):
        sys.exit('missing show asset: ' + p)
    shutil.copyfile(p, f'{D}/assets/{dst}')
e = html.escape
s = open(os.path.join(HERE, '..', '..', 'templates', 'podcast', 'wire-intro.html')).read()
s = (s.replace('{{DATE}}', e(EP['date'])).replace('{{GUEST_NAME}}', e(EP['guest']['name'])).replace('{{GUEST_ROLE}}', e(EP['guest']['role']))
      .replace('{{TITLE_WORDS}}', ''.join(f'<span class="w">{e(w)}</span>' for w in EP['title'].split()))
      .replace('{{TOPICS}}', ''.join(f'<span>{e(t)}</span>' for t in (EP['topics'] * 2)[:10])))
open(f'{D}/index.html', 'w').write(s)
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
           "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
           "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, open(f'{D}/hyperframes.json', 'w'), indent=2)
print('intro project ->', D, '(snapshot before rendering: long titles wrap to a third line)')
