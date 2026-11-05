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
summary{cursor:pointer;list-style:none}summary::-webkit-details-marker{display:none}summary:focus-visible{outline:2px solid var(--accent);outline-offset:4px}
.chevron{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.6;flex:none;transition:transform .15s}details[open]>summary>.chevron{transform:rotate(90deg)}
.review-toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}.review-toolbar p{font-size:14px;color:var(--muted)}#collapse-all{border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--ink);font:inherit;font-size:12px;padding:7px 13px;cursor:pointer}#collapse-all:disabled{opacity:.4;cursor:default}
details.project{display:block;padding:0;border-top-width:1px}.project-summary{display:flex;align-items:center;gap:12px;padding:20px 24px}.project-summary h2{flex:1;margin:0;font-size:22px}.project-meta{display:flex;gap:12px;align-items:center}.update-count{font-size:12px;color:var(--muted)}.project-content{padding:0 24px 24px}.project-description{font-size:15px;color:var(--muted);margin:0 0 19px}
.review-section{border:1px solid var(--line);border-radius:10px;margin-top:10px}.review-section>summary,.meeting-decisions>summary{display:flex;align-items:center;gap:14px;padding:16px 18px;font-weight:500}.section-label{flex:1}.section-hint{font-size:12px;color:var(--muted);margin-left:auto;font-weight:400}.section-body{padding:3px 20px 23px;max-width:76ch}.section-body ul,.section-body ol{padding-left:21px;margin:0}.section-body li{font-size:17px;line-height:1.65}.section-body li+li{margin-top:10px}.section-body .issues{list-style:none;padding:0}.section-body .issues li{display:flex;align-items:baseline;gap:9px}.focus-group+.focus-group{margin-top:25px}.focus-group h4{font-size:14px;font-weight:600;margin:0 0 11px;color:var(--ink)}.focus-group li{color:var(--ink)}.discussion{border-top:1px solid var(--line);padding-top:21px}.meeting-decisions{border:1px solid var(--line);border-radius:12px;margin-top:24px}.meeting-decisions>summary>span:first-child{flex:1}
@media(max-width:650px){.project-summary{padding:18px 17px;gap:10px}.project-summary h2{font-size:20px}.project-meta .update-count{display:none}.project-meta{gap:0}.project-content{padding:0 16px 18px}.review-section>summary{padding:16px 14px;gap:10px}.review-section .section-hint{display:none}.section-body{padding:3px 16px 20px}.section-body li{font-size:16.5px}.review-toolbar p{font-size:12px}.review-toolbar{gap:10px}}
@media(prefers-reduced-motion:reduce){.chevron{transition:none}}
@media print{.review-toolbar{display:none}details.project{break-inside:avoid}.project-meta{display:none}}

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


CHEVRON = '<svg class="chevron" viewBox="0 0 20 20" aria-hidden="true"><path d="m7 4 6 6-6 6"/></svg>'


def disclosure_section(label, content, key, hint=""):
    meta = f'<span class="section-hint">{esc(hint)}</span>' if hint else ""
    return f'<details class="review-section" data-section="{esc(key)}"><summary><span class="section-label">{esc(label)}</span>{meta}{CHEVRON}</summary><div class="section-body">{content}</div></details>'


def project_html(project, index):
    labels = {"blocker": "Blocker", "slowdown": "Slowdown", "check": "To confirm", "none": "Continuing"}
    updates = len(items(project["progress"]))
    update_label = f"{updates} update" + ("s" if updates != 1 else "")
    tone = next((kind for kind in ("blocker", "slowdown", "check") if any(x["kind"] == kind for x in project["issues"])), "none")
    status = f'<span class="tag {tone}">{esc(labels[tone])}</span>'
    note = f'<p class="progress-note">{esc(project["progress_note"])}</p>' if project.get("progress_note") else ""
    progress = disclosure_section("Progress this week", list_html(project["progress"]) + note, "progress", update_label)
    issue_rows = "".join(f'<li><span class="tag {esc(x["kind"])}">{esc(labels[x["kind"]])}</span><span>{esc(x["text"])}</span></li>' for x in project["issues"])
    blockers = disclosure_section("Blockers", f'<ul class="issues">{issue_rows}</ul>', "blockers", "Blockers and slowdowns")
    continuing = f'<div class="focus-group"><h4>Can continue now</h4>{list_html(project["continuing"])}</div>' if project.get("continuing") else ""
    discussion = f'<div class="focus-group discussion"><h4>Discuss together</h4>{list_html(project["discuss"])}</div>' if project.get("discuss") else ""
    focus_content = f'<div class="focus-group"><h4>Priorities to agree</h4>{list_html(project["next_week"])}</div>{continuing}{discussion}'
    focus = disclosure_section("Focus", focus_content, "focus", "Priorities and decisions")
    description = f'<p class="project-description">{esc(project["description"])}</p>' if project.get("description") else ""
    return f'<details class="project" data-project="{esc(project["id"])}"><summary class="project-summary"><span class="number">{index:02d}</span><h2>{esc(project["name"])}</h2><span class="project-meta"><span class="update-count">{esc(update_label)}</span>{status}</span>{CHEVRON}</summary><div class="project-content">{description}{progress}{blockers}{focus}</div></details>'


def render_html(data, brand_css=""):
    cards = "".join(project_html(p,i) for i,p in enumerate(data["projects"],1))
    secondary = "".join(project_html(secondary_project(p,i),i) for i,p in enumerate(data["other_projects"],len(data["projects"])+1))
    others = f'<section class="others"><h2>Other projects</h2><div class="other-grid">{secondary}</div></section>' if secondary else ""
    decisions = '<details class="meeting-decisions"><summary><span>Decisions for Monday</span><span class="section-hint">'+str(len(data["decisions"]))+' decisions</span>'+CHEVRON+'</summary><div class="section-body"><ol>'+"".join(f'<li>{esc(x)}</li>' for x in data["decisions"])+'</ol></div></details>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data["title"])}</title><style>{CSS}\n{brand_css}</style></head><body>
<header><div><div class="eyebrow">Weekly project review</div><h1>{esc(data["title"])}</h1><p class="meta">{esc(data["period"])}</p></div><div class="header-right"><span class="draft">Draft for discussion</span><p class="meeting">{esc(data["meeting"])}</p><p class="meta">{esc(data["prepared"])}</p></div></header>
<main><div class="review-toolbar"><p>Open a project, then choose a section.</p><button id="collapse-all" type="button">Collapse all</button></div><section aria-label="Main projects" class="cards">{cards}</section>{others}{decisions}<footer class="foot"><p>{esc(data.get("note","Proposed work and dates are for discussion."))}</p><p>Blocker: work stops.<br>Slowdown: work continues, but could move faster.</p></footer></main>
<script>
const collapseAll=document.getElementById('collapse-all');
function updateCollapseButton(){{collapseAll.disabled=!document.querySelector('details[open]')}}
document.querySelectorAll('details').forEach(item=>item.addEventListener('toggle',updateCollapseButton));
collapseAll.addEventListener('click',()=>{{document.querySelectorAll('details[open]').forEach(item=>item.open=false);updateCollapseButton()}});
updateCollapseButton();
let beforePrintOpen=[];
window.addEventListener('beforeprint',()=>{{beforePrintOpen=Array.from(document.querySelectorAll('details[open]'));document.querySelectorAll('details').forEach(item=>item.open=true)}});
window.addEventListener('afterprint',()=>{{document.querySelectorAll('details').forEach(item=>item.open=beforePrintOpen.includes(item));updateCollapseButton()}});
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
            right=section(x3,y,"Focus (proposed)",items(p["next_week"]),colw)
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
