"""Episode covers in the Recoup Podcast series layout: 16:9 thumbnail (YouTube + Spotify video
thumbnail) and 1:1 episode art (Spotify).

Usage:
  python3 scripts/podcast/make_cover.py --bg <blue-sweep.png|webp> --lockup <recoup-podcast-white.png> \
     --cutout <guest-headshot-cutout.png> --title "<episode claim>" --guest "w/ Name" --role "Title, Company" \
     --out <dir>

Layout (from the reference thumbnail spec, fractions of the short side): 10% margins, lockup 12.5% tall at
top-left, title in the left 47.5% column stepping down from 8.9% until it clears the lockup row, guest
name + role under it; the background-removed guest photo on the right, head on the top margin.
Photo: the guest's own PUBLISHED headshot (speaker page, company site), never a call screenshot; cut it
out with rembg (bria-rmbg) and check the mask on a flat colour. Fonts: renders DM Sans 400/500/600 from
this skill's brand/fonts/dm-sans.woff2 (variable) on first run.
Needs Pillow; fontTools + brotli for the font instances.
"""
import argparse, os, sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('needs Pillow — pip3 install pillow')
HERE = os.path.dirname(os.path.abspath(__file__))
WOFF = os.path.join(HERE, '..', '..', 'brand', 'fonts', 'dm-sans.woff2')
ap = argparse.ArgumentParser()
for k in ('bg', 'lockup', 'cutout', 'title', 'guest', 'role', 'out'):
    ap.add_argument('--' + k, required=True)
ap.add_argument('--fonts', default=os.path.expanduser('~/.cache/recoup-podcast-fonts'))
A = ap.parse_args()


def font_file(w):
    p = os.path.join(A.fonts, f'DMSans-{w}.ttf')
    if not os.path.exists(p):
        try:
            from fontTools.ttLib import TTFont
            from fontTools.varLib import instancer
        except ImportError:
            sys.exit('needs fontTools + brotli — pip3 install fonttools brotli (or pass --fonts with DMSans-400/500/600.ttf)')
        os.makedirs(A.fonts, exist_ok=True)
        inst = instancer.instantiateVariableFont(TTFont(WOFF), {'wght': w}); inst.flavor = None; inst.save(p)
    return p


font = lambda w, px: ImageFont.truetype(font_file(w), px)


def wrap(d, text, f, max_w):
    lines, cur = [], ''
    for wd in text.split():
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = wd
    return lines + [cur]


def cover(W, H):
    S = min(W, H); margin = round(0.10 * S)
    im = Image.open(A.bg).convert('RGB'); sc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    d = ImageDraw.Draw(im)
    c = Image.open(A.cutout).convert('RGBA'); c = c.crop(c.getbbox())
    vis = H - margin if W > H else round(0.62 * H)
    c = c.resize((round(c.width * vis / c.height), vis), Image.LANCZOS)
    cx = round(W * (0.71 if W > H else 0.74)); im.paste(c, (cx - c.width // 2, H - vis), c)
    lh = round(0.125 * S); lk = Image.open(A.lockup).convert('RGBA')
    lk = lk.resize((round(lk.width * lh / lk.height), lh), Image.LANCZOS); im.paste(lk, (margin, margin), lk)
    col = round(W * (0.475 if W > H else 0.47))
    gf = font(600, round(0.041 * S)); rf = font(400, round(0.037 * S))
    rl = wrap(d, A.role, rf, col); bottom = H - round(0.18 * S); top = margin + lh + round(0.06 * S)
    gh = round(gf.size * 1.35) + len(rl) * round(rf.size * 1.3) + round(0.04 * S)
    for frac in (0.089, 0.08, 0.072, 0.064, 0.058, 0.052):
        tf = font(500, round(frac * S)); pitch = round(tf.size * 1.27); lines = wrap(d, A.title, tf, col)
        if bottom - gh - pitch * len(lines) >= top:
            break
    y = bottom
    for ln in reversed(rl):
        y -= round(rf.size * 1.3); d.text((margin, y), ln, font=rf, fill='#dff1ff')
    y -= round(gf.size * 1.35); d.text((margin, y), A.guest, font=gf, fill='#ffffff')
    y -= round(0.04 * S)
    for ln in reversed(lines):
        y -= pitch; d.text((margin, y), ln, font=tf, fill='#ffffff')
    return im


os.makedirs(A.out, exist_ok=True)
cover(2000, 1125).save(os.path.join(A.out, 'thumbnail-2000x1125.jpg'), quality=92, optimize=True)
cover(2000, 2000).save(os.path.join(A.out, 'cover-2000x2000.jpg'), quality=92, optimize=True)
print('wrote', A.out + '/thumbnail-2000x1125.jpg', 'and cover-2000x2000.jpg (check: title clear of the hair, face sharp)')
