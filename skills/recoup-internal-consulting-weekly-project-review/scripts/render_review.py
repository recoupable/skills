#!/usr/bin/env python3
"""Render audience-facing project reviews; private evidence is deliberately omitted."""
import argparse
import html
import json
import re
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def validate(data):
    for key in ("title", "meeting", "period", "prepared", "projects", "other_projects", "decisions"):
        if key not in data:
            raise ValueError(f"Missing {key}")
    ids = set()
    for project in data["projects"]:
        if not re.fullmatch(r"[a-z][a-z0-9-]*", project["id"]) or project["id"] in ids:
            raise ValueError("Project ids must be unique lowercase slugs")
        ids.add(project["id"])
        for key in ("name", "description", "progress", "issues", "next_week", "discuss"):
            if key not in project:
                raise ValueError(f"Missing project {key}")
        for issue in project["issues"]:
            if issue["kind"] not in ("blocker", "slowdown", "check"):
                raise ValueError("Issue kind must be blocker, slowdown or check")
    for other in data["other_projects"]:
        if other["kind"] not in ("blocker", "slowdown", "check", "none"):
            raise ValueError("Invalid secondary project issue kind")


CSS = """
:root{--ink:#152e37;--muted:#586f78;--line:#dfe6e8;--accent:#007ebd;--green:#132b26;--lime:#d6ff62}
*{box-sizing:border-box}body{margin:0;background:#f5f6f4;color:var(--ink);font:16px/1.5 var(--brand-body-font,Arial),sans-serif}
button{font:inherit}button:focus-visible,a:focus-visible{outline:3px solid #007ebd;outline-offset:4px}
header{background:white;border-bottom:1px solid var(--line);padding:28px max(28px,calc((100vw - 1320px)/2));display:flex;gap:24px;align-items:center;justify-content:space-between}
.eyebrow{font-size:11px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;color:var(--muted)}h1{font-size:32px;line-height:1.15;margin:5px 0 7px;letter-spacing:-.04em;font-weight:500}h2{font-size:23px;font-weight:500;line-height:1.2;margin:0}p{margin:0}
.meta{font-size:13px;color:var(--muted)}.meeting{font-size:17px;color:var(--ink);margin-bottom:4px}.header-right{text-align:right}.draft{font-size:11px;font-weight:600;color:#675520;background:#faf2d9;border:1px solid #e8dcb7;border-radius:5px;padding:4px 8px;display:inline-block;margin-bottom:6px}
main{max-width:1376px;margin:0 auto;padding:24px 28px 40px}nav{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:22px}nav button,.back{border:1px solid var(--line);background:white;color:var(--ink);border-radius:6px;padding:8px 14px;cursor:pointer;font-size:13px}nav button[aria-pressed=true]{background:var(--green);border-color:var(--green);color:white}
.intro{display:flex;align-items:baseline;justify-content:space-between;gap:24px;margin-bottom:17px}.intro h2{font-size:19px}.intro p{font-size:12px;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:stretch}.project{background:white;border:1px solid var(--line);border-top:3px solid var(--green);border-radius:8px;padding:22px 23px 18px;min-width:0;display:flex;flex-direction:column}.project-top{display:flex;gap:12px;align-items:baseline}.number{font-size:11px;color:var(--muted)}.desc{color:var(--muted);font-size:13px;line-height:1.4;margin:8px 0 3px;min-height:37px}
.part{margin-top:19px}.part h3{font-size:11px;letter-spacing:.045em;text-transform:uppercase;font-weight:600;color:var(--muted);margin:0 0 7px}.part ul{list-style:none;padding:0;margin:0;display:grid;gap:7px}.part li{font-size:14px;line-height:1.45}.part li+li{border-top:1px solid #eef1f2;padding-top:7px}
.tag{display:inline-block;font-size:10px;line-height:1.2;padding:3px 5px;border-radius:3px;margin:0 5px 2px 0;font-weight:600;vertical-align:middle}.slowdown{background:#fff0d8;color:#7a4805}.blocker{background:#fbe5e3;color:#9a2c24}.check{background:#eef1f2;color:#52636b}.none{background:#e7f3ec;color:#276046}.discuss{padding-top:15px;margin-top:18px;border-top:1px solid var(--line)}.focus-link{margin-top:auto;padding-top:18px;align-self:flex-start;border:0;background:transparent;color:var(--accent);font-size:12px;cursor:pointer;padding-left:0}
.decisions{background:var(--green);color:white;border-radius:8px;margin-top:22px;padding:19px 23px;display:grid;grid-template-columns:160px 1fr;gap:20px}.decisions h2{font-size:18px}.decisions ol{margin:0;padding-left:20px;display:grid;gap:6px;font-size:13px}.decisions .eyebrow{color:#becdc6;margin-bottom:6px}
.others{margin-top:27px}.others h2{font-size:19px;margin-bottom:13px}.other-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.other{background:white;border:1px solid var(--line);border-radius:6px;padding:16px 18px;min-width:0}.other h3{font-size:15px;font-weight:500;margin:0 0 8px}.other p{font-size:12px;line-height:1.45;margin-top:6px}.other strong{font-weight:500}.foot{display:flex;gap:22px;justify-content:space-between;border-top:1px solid var(--line);margin-top:23px;padding-top:14px;font-size:11px;line-height:1.5;color:var(--muted)}
.focus{max-width:1040px;margin:0 auto}.focus .project{padding:35px 42px}.focus h2{font-size:34px}.focus .desc{font-size:17px;min-height:0;margin-bottom:8px}.focus .part{margin-top:24px}.focus .part h3{font-size:12px}.focus .part li{font-size:21px;line-height:1.5}.focus .tag{font-size:12px}.focus .focus-link{display:none}.focus .back{margin-bottom:15px}.focus .cols{display:grid;grid-template-columns:1fr 1fr;gap:34px}[hidden]{display:none!important}
@media(max-width:900px){.cards{grid-template-columns:1fr}.desc{min-height:0}.other-grid{grid-template-columns:1fr}.focus .cols{grid-template-columns:1fr}.focus .project{padding:24px}.focus .part li{font-size:18px}.intro{display:block}.intro p{margin-top:6px}}
@media(max-width:550px){header{padding:20px;display:block}.header-right{text-align:left;margin-top:14px}h1{font-size:29px}main{padding:20px 16px}.decisions{grid-template-columns:1fr;gap:12px}.foot{display:block}.focus h2{font-size:28px}}
@media print{body{background:white}header{padding:0 0 18px}main{padding:18px 0;max-width:none}nav,.focus-link,.back{display:none}.cards{display:block}.project{break-inside:avoid;margin-bottom:16px}.other-grid{display:block}.other{break-inside:avoid;margin-bottom:8px}.decisions{background:white;color:#152e37;border:1px solid #152e37;break-inside:avoid}.decisions .eyebrow{color:#586f78}.focus{display:none!important}#overview{display:block!important}.focus .cols{display:block}}
"""


def list_html(items):
    return "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"


def project_html(project, index, next_label, focused=False):
    issues = "".join(f'<li><span class="tag {esc(x["kind"])}">{esc({"blocker":"Blocker","slowdown":"Slowdown","check":"To confirm"}[x["kind"]])}</span>{esc(x["text"])}</li>' for x in project["issues"])
    first = f'<section class="part"><h3>Progress this week</h3>{list_html(project["progress"])}</section><section class="part"><h3>Blockers / slowdowns</h3><ul>{issues}</ul></section>'
    second = f'<section class="part"><h3>{esc(next_label)} <span style="font-weight:400;text-transform:none">(proposed)</span></h3>{list_html(project["next_week"])}</section><section class="part discuss"><h3>Discuss on Monday</h3>{list_html(project["discuss"])}</section>'
    body = f'<div class="cols"><div>{first}</div><div>{second}</div></div>' if focused else first + second
    return f'<article class="project"><div class="project-top"><span class="number">0{index}</span><h2>{esc(project["name"])}</h2></div><p class="desc">{esc(project["description"])}</p>{body}<button class="focus-link" data-view="{esc(project["id"])}">Open project view &rarr;</button></article>'


def render_html(data, brand_css=""):
    next_label = data.get("next_week_label", "By next week")
    nav = '<button data-view="overview" aria-pressed="true">All projects</button>' + "".join(f'<button data-view="{esc(p["id"])}" aria-pressed="false">{esc(p["name"])}</button>' for p in data["projects"])
    cards = "".join(project_html(p, i, next_label) for i, p in enumerate(data["projects"], 1))
    secondary = "".join(f'<article class="other"><h3>{esc(p["name"])}</h3><p><strong>Progress:</strong> {esc(p["progress"])}</p><p><span class="tag {esc(p["kind"])}">{esc({"blocker":"Blocker","slowdown":"Slowdown","check":"To confirm","none":"Continuing"}[p["kind"]])}</span>{esc(p["issue"])}</p><p><strong>By next week:</strong> {esc(p["next_week"])}</p><p><strong>Discuss:</strong> {esc(p["discuss"])}</p></article>' for p in data["other_projects"])
    decisions = '<section class="decisions"><div><div class="eyebrow">Monday discussion</div><h2>Decisions to make</h2></div><ol>' + "".join(f'<li>{esc(x)}</li>' for x in data["decisions"]) + '</ol></section>'
    focused = "".join(f'<section class="focus" id="view-{esc(p["id"])}" hidden><button class="back" data-view="overview">&larr; All projects</button>{project_html(p,i,next_label,True)}</section>' for i,p in enumerate(data["projects"],1))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data["title"])}</title><style>{brand_css}\n{CSS}</style></head><body>
<header><div><div class="eyebrow">Weekly project review</div><h1>{esc(data["title"])}</h1><p class="meta">{esc(data["period"])}</p></div><div class="header-right"><span class="draft">Draft for discussion</span><p class="meeting">{esc(data["meeting"])}</p><p class="meta">{esc(data["prepared"])}</p></div></header>
<main><nav aria-label="Project views">{nav}</nav><section id="overview"><div class="intro"><h2>The projects</h2><p>Progress, what is slowing us down, and what we want done next.</p></div><div class="cards">{cards}</div>{decisions}<section class="others"><h2>Other projects and ongoing work</h2><div class="other-grid">{secondary}</div></section></section>{focused}<footer class="foot"><p>{esc(data.get("note","Proposed work and dates are for discussion."))}</p><p>Blocker: work stops.<br>Slowdown: work continues, but could move faster.</p></footer></main>
<script>
function showView(name){{
 const allowed=['overview',...Array.from(document.querySelectorAll('.focus')).map(x=>x.id.slice(5))];
 if(!allowed.includes(name)) name='overview';
 document.getElementById('overview').hidden=name!=='overview';
 document.querySelectorAll('.focus').forEach(x=>x.hidden=x.id!=='view-'+name);
 document.querySelectorAll('nav button').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.view===name)));
 window.scrollTo(0,0);
}}
document.querySelectorAll('[data-view]').forEach(x=>x.addEventListener('click',()=>showView(x.dataset.view)));
document.addEventListener('keydown',e=>{{if(e.key==='Escape')showView('overview')}});
</script></body></html>'''


def render_pdf(data, path, font_path=None):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        raise SystemExit("PDF output needs reportlab; install with: pip3 install reportlab")
    font = "Helvetica"
    if font_path:
        pdfmetrics.registerFont(TTFont("ReviewBody", str(font_path)))
        font = "ReviewBody"
    W, H = 1190, 842
    c = canvas.Canvas(str(path), pagesize=(W, H))
    c.setTitle(data["title"])
    ink, muted, border = "#152E37", "#586F78", "#DFE6E8"
    def text(x, y, value, size=14, color=ink, width=1050, leading=None):
        # PDF typography uses ordinary spaces/hyphens, preserving explicit content.
        safe = html.escape(str(value).replace("\u2011","-").replace("\u2013","-").replace("\u2014","-"))
        style = ParagraphStyle("body", fontName=font, fontSize=size, leading=leading or size*1.35, textColor=HexColor(color))
        para = Paragraph(safe, style)
        _, height = para.wrap(width, H)
        para.drawOn(c,x,y-height)
        return y-height
    def header(page):
        text(40,H-29,"WEEKLY PROJECT REVIEW",11,muted)
        text(40,H-52,data["title"],30)
        text(40,H-96,data["period"],13,muted)
        text(W-330,H-34,data["meeting"],16,width=290)
        text(W-330,H-62,data["prepared"],12,muted,width=290)
        c.setStrokeColor(HexColor(border));c.line(40,H-126,W-40,H-126)
        text(40,35,data.get("note","Draft for discussion"),10,muted,width=W-120)
        text(W-65,35,str(page),10,muted,width=25)
    def section(x,y,label,items,width):
        y=text(x,y,label.upper(),10,muted,width=width)-8
        for item in items:
            y=text(x,y,item,14,width=width)-9
        return y-12
    header(1)
    gap=16; cardw=(W-80-gap*2)/3; top=H-151; bottom=207
    for i,p in enumerate(data["projects"]):
        if len(data["projects"])>3:
            raise ValueError("PDF overview supports up to three primary projects; use secondary projects for others")
        x=40+i*(cardw+gap)
        c.setStrokeColor(HexColor(border));c.roundRect(x,bottom,cardw,top-bottom,6,stroke=1,fill=0)
        c.setStrokeColor(HexColor("#132B26"));c.setLineWidth(3);c.line(x+1,top,x+cardw-1,top);c.setLineWidth(1)
        y=text(x+17,top-18,p["name"],23,width=cardw-34)-9
        y=text(x+17,y,p["description"],12,muted,width=cardw-34)-19
        y=section(x+17,y,"Progress this week",p["progress"],cardw-34)
        y=section(x+17,y,"Blockers / slowdowns",[f'{ {"blocker":"Blocker","slowdown":"Slowdown","check":"To confirm"}[v["kind"]]}: {v["text"]}' for v in p["issues"]],cardw-34)
        y=section(x+17,y,data.get("next_week_label","By next week")+" (proposed)",p["next_week"],cardw-34)
        y=section(x+17,y,"Discuss on Monday",p["discuss"],cardw-34)
        if y<bottom+2:
            raise ValueError(f"PDF card too long: {p['name']}; shorten copy before sharing")
    text(40,181,"DECISIONS TO MAKE TOGETHER",11,muted)
    y=155
    for i,item in enumerate(data["decisions"],1):
        y=text(40,y,f"{i}. {item}",14,width=W-80)-8
    if y<50:
        raise ValueError("Too many decisions for the PDF overview")
    c.showPage();header(2)
    text(40,H-151,"Other projects and ongoing work",25)
    y=H-199
    columns=[(40,165,"Project"),(224,200,"Progress this week"),(443,225,"Blockers / slowdowns"),(687,230,"By next week (proposed)"),(936,214,"Discuss")]
    for x,width,label in columns:
        text(x,y,label.upper(),10,muted,width=width)
    y-=30
    for p in data["other_projects"]:
        label={"blocker":"Blocker","slowdown":"Slowdown","check":"To confirm","none":"Continuing"}[p["kind"]]
        values=[p["name"],p["progress"],label+": "+p["issue"],p["next_week"],p["discuss"]]
        bottoms=[text(x,y,value,14 if i==0 else 12,width=width) for i,((x,width,_),value) in enumerate(zip(columns,values))]
        y=min(bottoms)-20
        c.setStrokeColor(HexColor(border));c.line(40,y+7,W-40,y+7)
        y-=13
    if y<75:
        raise ValueError("Secondary project copy exceeds the PDF page; shorten it")
    text(40,64,"Blocker: the named work cannot move. Slowdown: work continues, but addressing it would help.",11,muted)
    c.save()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--brand-css",type=Path)
    parser.add_argument("--pdf",type=Path)
    parser.add_argument("--font",type=Path)
    args=parser.parse_args()
    data=json.loads(args.input.read_text())
    validate(data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(render_html(data,args.brand_css.read_text() if args.brand_css else ""))
    if args.pdf:
        args.pdf.parent.mkdir(parents=True,exist_ok=True)
        render_pdf(data,args.pdf,args.font)
    print(f"Rendered {len(data['projects'])} main and {len(data['other_projects'])} other projects")


if __name__=="__main__":
    main()
