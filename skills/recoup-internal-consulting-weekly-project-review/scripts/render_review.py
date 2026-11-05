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
.cards{display:flex;flex-direction:column;gap:22px}.project .cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px}.project{background:white;border:1px solid var(--line);border-top:3px solid var(--green);border-radius:8px;padding:22px 23px 18px;min-width:0;display:flex;flex-direction:column}.project-top{display:flex;gap:12px;align-items:baseline}.number{font-size:11px;color:var(--muted)}.desc{color:var(--muted);font-size:13px;line-height:1.4;margin:8px 0 3px;min-height:37px}
.part{margin-top:19px}.part h3{font-size:11px;letter-spacing:.045em;text-transform:uppercase;font-weight:600;color:var(--muted);margin:0 0 7px}.part ul{list-style:disc;padding-left:20px;margin:0;display:grid;gap:9px}.part .issues{list-style:none;padding-left:0}.issues li{display:flex;align-items:baseline;gap:8px}.part li{font-size:17px;line-height:1.65}.part li+li{border:0;padding-top:0}
.tag{display:inline-block;font-size:10px;line-height:1.2;padding:3px 5px;border-radius:3px;margin:0 5px 2px 0;font-weight:600;vertical-align:middle}.slowdown{background:#fff0d8;color:#7a4805}.blocker{background:#fbe5e3;color:#9a2c24}.check{background:#eef1f2;color:#52636b}.none{background:#e7f3ec;color:#276046}.discuss{padding-top:15px;margin-top:18px;border-top:1px solid var(--line)}.focus-link{margin-top:auto;padding-top:18px;align-self:flex-start;border:0;background:transparent;color:var(--accent);font-size:12px;cursor:pointer;padding-left:0}
.decisions{background:var(--green);color:white;border-radius:8px;margin-top:22px;padding:19px 23px;display:grid;grid-template-columns:160px 1fr;gap:20px}.decisions h2{font-size:18px}.decisions ol{margin:0;padding-left:20px;display:grid;gap:6px;font-size:13px}.decisions .eyebrow{color:#becdc6;margin-bottom:6px}
.others{margin-top:27px}.others h2{font-size:19px;margin-bottom:13px}.other-grid{display:flex;flex-direction:column;gap:18px}.other{background:white;border:1px solid var(--line);border-radius:6px;padding:16px 18px;min-width:0}.other h3{font-size:15px;font-weight:500;margin:0 0 8px}.other p{font-size:12px;line-height:1.45;margin-top:6px}.other strong{font-weight:500}.foot{display:flex;gap:22px;justify-content:space-between;border-top:1px solid var(--line);margin-top:23px;padding-top:14px;font-size:11px;line-height:1.5;color:var(--muted)}
.focus{max-width:1040px;margin:0 auto}.focus .project{padding:35px 42px}.focus h2{font-size:34px}.focus .desc{font-size:17px;min-height:0;margin-bottom:8px}.focus .part{margin-top:24px}.focus .part h3{font-size:12px}.focus .part li{font-size:21px;line-height:1.5}.focus .tag{font-size:12px}.focus .focus-link{display:none}.focus .back{margin-bottom:15px}.focus .cols{display:grid;grid-template-columns:1fr 1fr;gap:34px}[hidden]{display:none!important}
@media(max-width:900px){.project .cols{grid-template-columns:minmax(0,1fr)}.cards{grid-template-columns:1fr}.desc{min-height:0}.other-grid{grid-template-columns:1fr}.focus .cols{grid-template-columns:1fr}.focus .project{padding:24px}.focus .part li{font-size:18px}.intro{display:block}.intro p{margin-top:6px}}
@media(max-width:550px){header{padding:20px;display:block}.header-right{text-align:left;margin-top:14px}h1{font-size:29px}main{padding:20px 16px}.decisions{grid-template-columns:1fr;gap:12px}.foot{display:block}.focus h2{font-size:28px}}
@media print{body{background:white}header{padding:0 0 18px}main{padding:18px 0;max-width:none}nav,.focus-link,.back{display:none}.cards{display:block}.project{break-inside:avoid;margin-bottom:16px}.other-grid{display:block}.other{break-inside:avoid;margin-bottom:8px}.decisions{background:white;color:#152e37;border:1px solid #152e37;break-inside:avoid}.decisions .eyebrow{color:#586f78}.focus{display:none!important}#overview{display:block!important}.focus .cols{display:block}}
"""


def items(value):
    """Accept old secondary string fields while preserving each new list item."""
    return [value] if isinstance(value, str) else value


def list_html(values):
    return "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in items(values)) + "</ul>"


def secondary_project(project, index):
    return {
        "id": f"secondary-{index}", "name": project["name"],
        "description": project.get("description", ""),
        "progress": items(project["progress"]),
        "progress_note": project.get("progress_note", ""),
        "issues": [{"kind": project["kind"], "text": project["issue"]}],
        "next_week": items(project["next_week"]),
        "discuss": items(project["discuss"]),
    }


def project_html(project, index, next_label, focused=False, secondary=False):
    labels = {"blocker": "Blocker", "slowdown": "Slowdown", "check": "To confirm", "none": "Continuing"}
    issues = "".join(f'<li><span class="tag {esc(x["kind"])}">{esc(labels[x["kind"]])}</span><span>{esc(x["text"])}</span></li>' for x in project["issues"])
    note = f'<p class="progress-note">{esc(project["progress_note"])}</p>' if project.get("progress_note") else ""
    continuing = f'<section class="part continuing"><h3>Work continuing</h3>{list_html(project["continuing"])}</section>' if project.get("continuing") else ""
    first = f'<section class="part"><h3>Progress this week</h3>{list_html(project["progress"])}{note}</section><section class="part"><h3>Blockers / slowdowns</h3><ul class="issues">{issues}</ul></section>{continuing}'
    second = f'<section class="part"><h3>{esc(next_label)} <span class="proposed">Proposed</span></h3>{list_html(project["next_week"])}</section><section class="part discuss"><h3>Discuss on Monday</h3>{list_html(project["discuss"])}</section>'
    body = f'<div class="cols"><div>{first}</div><div>{second}</div></div>'
    link = "" if secondary else f'<button class="focus-link" data-view="{esc(project["id"])}">Open project view &rarr;</button>'
    description = f'<p class="desc">{esc(project["description"])}</p>' if project.get("description") else ""
    return f'<article class="project"><div class="project-top"><span class="number">{index:02d}</span><h2>{esc(project["name"])}</h2></div>{description}{body}{link}</article>'


def render_html(data, brand_css=""):
    next_label = data.get("next_week_label", "By next week")
    nav = '<button data-view="overview" aria-pressed="true">All projects</button>' + "".join(f'<button data-view="{esc(p["id"])}" aria-pressed="false">{esc(p["name"])}</button>' for p in data["projects"])
    cards = "".join(project_html(p, i, next_label) for i, p in enumerate(data["projects"], 1))
    secondary = "".join(project_html(secondary_project(p,i),i,next_label,secondary=True) for i,p in enumerate(data["other_projects"],len(data["projects"])+1))
    decisions = '<section class="decisions"><div><div class="eyebrow">Monday discussion</div><h2>Decisions to make</h2></div><ol>' + "".join(f'<li>{esc(x)}</li>' for x in data["decisions"]) + '</ol></section>'
    focused = "".join(f'<section class="focus" id="view-{esc(p["id"])}" hidden><button class="back" data-view="overview">&larr; All projects</button>{project_html(p,i,next_label,True)}</section>' for i,p in enumerate(data["projects"],1))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data["title"])}</title><style>{CSS}\n{brand_css}</style></head><body>
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
    theme = {"background":"#FFFFFF","card":"#FFFFFF","text":"#152E37","muted":"#586F78","line":"#DFE6E8","accent":"#007EBD","warning":"#986300","danger":"#A33333"}
    theme.update(data.get("pdf_theme", {}))
    for color in theme.values():
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ValueError("PDF theme colors must be six-digit hex values")
    W,H=1190,940
    c=canvas.Canvas(str(path),pagesize=(W,H))
    c.setTitle(data["title"])
    def text(x,y,value,size=15,color="text",width=1050):
        safe=html.escape(str(value).replace("\u2011","-").replace("\u2013","-").replace("\u2014","-"))
        style=ParagraphStyle("review",fontName=font,fontSize=size,leading=size*1.45,textColor=HexColor(theme[color]))
        para=Paragraph(safe,style)
        _,height=para.wrap(width,H)
        para.drawOn(c,x,y-height)
        return y-height
    def header(page):
        c.setFillColor(HexColor(theme["background"]));c.rect(0,0,W,H,fill=1,stroke=0)
        text(38,H-25,"WEEKLY PROJECT REVIEW",10,"accent")
        text(38,H-48,data["title"],29)
        text(38,H-96,data["period"],12,"muted")
        text(W-305,H-32,data["meeting"],16,width=265)
        text(W-305,H-62,data["prepared"],12,"muted",width=265)
        c.setStrokeColor(HexColor(theme["line"]));c.line(38,H-125,W-38,H-125)
        text(38,31,data.get("note","Draft for discussion"),10,"muted",width=W-140)
        text(W-60,31,str(page),10,"muted",width=25)
    def section(x,y,label,values,width):
        y=text(x,y,label,11,"accent",width)-8
        for value in values:
            c.setFillColor(HexColor(theme["accent"]));c.circle(x+2,y-7,1.7,fill=1,stroke=0)
            y=text(x+13,y,value,14,width=width-13)-6
        return y-12
    projects=list(data["projects"])+[secondary_project(p,i) for i,p in enumerate(data["other_projects"],len(data["projects"])+1)]
    for offset in range(0,len(projects),2):
        header(offset//2+1)
        for row,p in enumerate(projects[offset:offset+2]):
            x=38; width=W-76; top=H-145-row*378; bottom=top-360
            c.setFillColor(HexColor(theme["card"]));c.setStrokeColor(HexColor(theme["line"]));c.roundRect(x,bottom,width,360,12,fill=1,stroke=1)
            y=text(x+22,top-15,p["name"],22,width=width-44)-5
            if p.get("description"):
                y=text(x+22,y,p["description"],11,"muted",width-44)-10
            else:
                y-=9
            colw=(width-44-50)/3
            x1=x+22; x2=x1+colw+25; x3=x2+colw+25
            left=section(x1,y,"Progress this week",items(p["progress"]),colw)
            if p.get("progress_note"):
                left=text(x1,left+5,p["progress_note"],9,"muted",colw)-8
            issue_labels={"blocker":"Blocker","slowdown":"Slowdown","check":"To confirm","none":"Continuing"}
            middle=section(x2,y,"Blockers / slowdowns",[issue_labels[v["kind"]]+": "+v["text"] for v in p["issues"]],colw)
            if p.get("continuing"):
                middle=section(x2,middle,"Work continuing",p["continuing"],colw)
            right=section(x3,y,"By next week (proposed)",items(p["next_week"]),colw)
            right=section(x3,right,"Discuss on Monday",items(p["discuss"]),colw)
            if min(left,middle,right)<bottom+6:
                raise ValueError(f"PDF project too long: {p['name']}; preserve content by allocating more space ({min(left,middle,right):.0f} < {bottom+6:.0f})")
        c.showPage()
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
