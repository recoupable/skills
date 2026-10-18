"""Capture a real page for an evidence card: hide fixed/sticky chrome, crop around a phrase, measure its highlight box.
python3 scripts/podcast/capture_ref.py <url> "<phrase to highlight>" <out.jpg> [crop_height_css=560] [above_css=150]
Prints mark=(x, y, w, h) in % of the cropped image. Viewport 1280x900 @2x (agent-browser)."""
import json, subprocess, sys
import os
url, phrase, out = sys.argv[1:4]
out = os.path.abspath(out)
H = int(sys.argv[4]) if len(sys.argv) > 4 else 560
A = int(sys.argv[5]) if len(sys.argv) > 5 else 150
ab = lambda *a: subprocess.run(['agent-browser', *a], capture_output=True, text=True).stdout
ab('open', url); ab('set', 'viewport', '1280', '900', '2'); ab('wait', '1500')
js = """(()=>{const P=%s;for(const el of document.querySelectorAll('*')){const s=getComputedStyle(el);if(s.position==='fixed'||s.position==='sticky')el.style.setProperty('display','none','important')}
document.querySelectorAll('[id*=cookie],[class*=cookie],[class*=consent],[id*=consent]').forEach(e=>e.remove());
const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n,hit=null;const norm=x=>x.replace(/\\s+/g,' ');
while(n=w.nextNode()){const i=norm(n.textContent).indexOf(P);if(i>=0&&n.parentElement.offsetParent){hit=[n,n.textContent.indexOf(P.split(' ')[0])];break}}
if(!hit)return JSON.stringify({err:'phrase not found'});
const [node]=hit;const raw=node.textContent;let st=raw.indexOf(P);if(st<0)st=hit[1];
const r=document.createRange();r.setStart(node,st);r.setEnd(node,Math.min(raw.length,st+P.length));
const y0=node.parentElement.getBoundingClientRect().top+scrollY-%d;document.documentElement.style.scrollBehavior='auto';window.scrollTo({top:y0,behavior:'instant'});
window.__R=r;window.__P=node;const rects=[...r.getClientRects()];const b=r.getBoundingClientRect();
let col=node.parentElement;while(col.parentElement&&col.getBoundingClientRect().width<560)col=col.parentElement;const c=col.getBoundingClientRect();
return JSON.stringify({b:[b.left,b.top,b.width,b.height],n:rects.length,col:[c.left,c.width]})})()""" % (json.dumps(phrase), A)
res = json.loads(json.loads(ab('eval', js).strip()))
if 'err' in res: sys.exit(res['err'])
ab('wait', '700')
res2 = json.loads(json.loads(ab('eval', "(()=>{const b=window.__R.getBoundingClientRect();let col=window.__P.parentElement;while(col.parentElement&&col.getBoundingClientRect().width<560)col=col.parentElement;const c=col.getBoundingClientRect();return JSON.stringify({b:[b.left,b.top,b.width,b.height],n:window.__R.getClientRects().length,col:[c.left,c.width],vw:innerWidth,vh:innerHeight})})()").strip()))
res.update(res2)
tmp = out + '.full.png'; ab('screenshot', tmp)
bx, by, bw, bh = res['b']; cx, cw = res['col']
x0 = max(0, cx - 24); W = min(1280 - x0, cw + 48); y0 = max(0, by - A + 10 if by > A else 0)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-vf', f'crop={int(W*2)}:{int(H*2)}:{int(x0*2)}:{int(y0*2)}', '-q:v', '3', out], check=True)
pad = 4
m = ((bx - x0 - pad) / W * 100, (by - y0 - pad) / H * 100, (bw + 2 * pad) / W * 100, (bh + 2 * pad) / H * 100)
print(json.dumps({'mark': [round(v, 1) for v in m], 'lines': res['n']}))
