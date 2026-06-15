#!/usr/bin/env python3
"""Build a branded executive baseline PDF from estimate.json (output of estimate.py).
Usage: python3 build_report.py --estimate out/estimate.json --out out
Requires: matplotlib, reportlab.  -> out/<asset>-baseline-report.pdf"""
import argparse, json, os, re, datetime as dt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ap = argparse.ArgumentParser(); ap.add_argument("--estimate", required=True); ap.add_argument("--out", default=".")
A = ap.parse_args(); R = json.load(open(A.estimate)); OUT = A.out; os.makedirs(OUT, exist_ok=True)
slug = re.sub(r"[^A-Za-z0-9]+", "-", R["asset"]).strip("-") or "asset"

INK="#0F172A"; ACCENT="#7C3AED"; ACCENT2="#06B6D4"; MUTED="#64748B"; LIGHT="#F1F5F9"; GREEN="#16A34A"; GRID="#E2E8F0"
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.edgecolor":MUTED,"axes.labelcolor":INK,
    "text.color":INK,"xtick.color":MUTED,"ytick.color":MUTED,"axes.linewidth":0.8,"figure.dpi":200})
mil = lambda x,_: f"{x:,.0f}M"
def Mb(x): return f"{x/1e9:.2f}B" if x>=1e9 else f"{x/1e6:.0f}M"
def Dm(x): return f"${x/1e6:.2f}M" if x<1e9 else f"${x/1e9:.2f}B"

traj = R.get("trajectory", {}) or {}
yks = sorted(int(y) for y in traj)
charts = []

if len(yks) >= 2:
    cum = [traj[str(y)]["cumulative"]/1e6 for y in yks]
    fig,ax=plt.subplots(figsize=(6.6,2.9)); ax.fill_between([str(y) for y in yks],cum,color=ACCENT,alpha=0.12)
    ax.plot([str(y) for y in yks],cum,color=ACCENT,lw=2.6,marker="o",ms=6,mfc="white",mec=ACCENT,mew=2)
    for x,v in zip(yks,cum): ax.annotate(Mb(v*1e6),(str(x),v),textcoords="offset points",xytext=(0,9),ha="center",fontsize=9,fontweight="bold")
    ax.yaxis.set_major_formatter(FuncFormatter(mil)); ax.set_ylim(0,max(cum)*1.18)
    ax.set_title("Cumulative Spotify streams",loc="left",fontsize=12,fontweight="bold",pad=10)
    ax.grid(axis="y",color=GRID); [ax.spines[s].set_visible(False) for s in("top","right")]
    fig.tight_layout(); p=f"{OUT}/_c_cum.png"; fig.savefig(p,bbox_inches="tight"); plt.close(); charts.append(("Cumulative streams",p))
    # annual + YoY
    anns=[(y,traj[str(y)].get("annual")) for y in yks if traj[str(y)].get("annual") is not None]
    if anns:
        labs=[f"{y-1}–{str(y)[2:]}" for y,_ in anns]; vals=[v/1e6 for _,v in anns]
        fig,ax=plt.subplots(figsize=(6.6,2.9)); bars=ax.bar(labs,vals,color=ACCENT,width=0.6)
        for i,(b,v) in enumerate(zip(bars,vals)):
            ax.annotate(f"{v:.0f}M",(b.get_x()+b.get_width()/2,v),textcoords="offset points",xytext=(0,5),ha="center",fontsize=9,fontweight="bold")
            if i>0:
                g=100*vals[i]/vals[i-1]-100
                ax.annotate(f"{g:+.0f}%",(b.get_x()+b.get_width()/2,v/2),ha="center",fontsize=10,fontweight="bold",color="white")
        ax.yaxis.set_major_formatter(FuncFormatter(mil)); ax.set_ylim(0,max(vals)*1.2)
        ax.set_title("Annual streams & YoY change",loc="left",fontsize=12,fontweight="bold",pad=10)
        ax.grid(axis="y",color=GRID); [ax.spines[s].set_visible(False) for s in("top","right")]
        fig.tight_layout(); p=f"{OUT}/_c_ann.png"; fig.savefig(p,bbox_inches="tight"); plt.close(); charts.append(("Annual streams",p))

# concentration
tr=R["tracks"][:8]; rest=R["tracks"][8:]; total=R["streams"]["spotify_ttm"] or 1
names=[t["title"][:26] for t in tr]; vals=[t["spotify_ttm"]/1e6 for t in tr]
if rest: names.append(f"Other ({len(rest)} tracks)"); vals.append(sum(t['spotify_ttm'] for t in rest)/1e6)
fig,ax=plt.subplots(figsize=(6.6,3.4)); cols=[ACCENT]+[ACCENT2]*(len(vals)-2)+[GRID] if len(vals)>1 else [ACCENT]
ax.barh(range(len(names)),vals,color=cols[:len(names)]); ax.set_yticks(range(len(names))); ax.set_yticklabels(names,fontsize=9); ax.invert_yaxis()
for i,v in enumerate(vals): ax.annotate(f"{v:.0f}M ({100*v*1e6/total:.0f}%)",(v,i),textcoords="offset points",xytext=(6,0),va="center",fontsize=8.3)
ax.xaxis.set_major_formatter(FuncFormatter(mil)); ax.set_xlim(0,max(vals)*1.25)
ax.set_title("Trailing-12-month streams by track — concentration",loc="left",fontsize=12,fontweight="bold",pad=10)
ax.grid(axis="x",color=GRID); [ax.spines[s].set_visible(False) for s in("top","right","left")]
fig.tight_layout(); p=f"{OUT}/_c_conc.png"; fig.savefig(p,bbox_inches="tight"); plt.close(); charts.append(("Concentration",p))

# value range
v=R["value"]; lbl=["Conservative","Central","Upside"]; vv=[v["low"]/1e6,v["central"]/1e6,v["high"]/1e6]
fig,ax=plt.subplots(figsize=(6.6,2.9)); bars=ax.bar(lbl,vv,color=[MUTED,ACCENT,ACCENT2],width=0.55)
for b,x in zip(bars,vv): ax.annotate(f"${x:.0f}M",(b.get_x()+b.get_width()/2,x),textcoords="offset points",xytext=(0,6),ha="center",fontsize=12,fontweight="bold")
ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"${x:.0f}M")); ax.set_ylim(0,max(vv)*1.18)
ax.set_title("Estimated asset value (directional model)",loc="left",fontsize=12,fontweight="bold",pad=10)
ax.grid(axis="y",color=GRID); [ax.spines[s].set_visible(False) for s in("top","right")]
fig.tight_layout(); p=f"{OUT}/_c_val.png"; fig.savefig(p,bbox_inches="tight"); plt.close(); charts.append(("Value",p))

# ---- PDF ----
from reportlab.lib.pagesizes import letter; from reportlab.lib.units import inch; from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
INKc=colors.HexColor(INK); ACc=colors.HexColor(ACCENT); MUc=colors.HexColor(MUTED); LTc=colors.HexColor(LIGHT); GRc=colors.HexColor(GRID)
ss=getSampleStyleSheet()
def S(n,**k): b=k.pop("parent",ss["Normal"]); return ParagraphStyle(n,parent=b,**k)
h1=S("h1",fontName="Helvetica-Bold",fontSize=17,textColor=INKc,leading=20); h2=S("h2",fontName="Helvetica-Bold",fontSize=12.5,textColor=ACc,spaceBefore=13,spaceAfter=6)
body=S("b",fontSize=10,textColor=INKc,leading=15,spaceAfter=6); small=S("s",fontSize=8.2,textColor=MUc,leading=11)
bullet=S("bl",fontSize=10,textColor=INKc,leading=15,leftIndent=10,spaceAfter=3)
def kpi(num,lab,bg=LTc,nc=INKc,lc=MUc):
    t=Table([[Paragraph(num,S('n',fontName="Helvetica-Bold",fontSize=16,textColor=nc))],[Paragraph(lab,S('l',fontSize=7.4,textColor=lc))]],colWidths=[1.62*inch])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(0,0),9),("BOTTOMPADDING",(0,0),(0,0),1),("TOPPADDING",(0,1),(0,1),0),("BOTTOMPADDING",(0,1),(-1,-1),9),("ROUNDEDCORNERS",[5,5,5,5])])); return t

cfg=R["assumptions"]; conc=R["concentration"]
story=[]
hdr=Table([[Paragraph('<font color="#7C3AED"><b>recoup</b></font>',S('lg',fontName="Helvetica-Bold",fontSize=15)),
            Paragraph('PORTFOLIO BASELINE REPORT',S('hr',fontSize=8.5,textColor=MUc,alignment=2))]],colWidths=[3.4*inch,3.6*inch])
hdr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
story+=[hdr,Spacer(1,4),HRFlowable(width="100%",thickness=2,color=ACc,spaceAfter=12),
    Paragraph(f"{R['asset']}" + (f" — {R['owner']}" if R['owner'] else ""),h1),
    Paragraph(f"Asset performance &amp; valuation baseline · As of {R['as_of']}",S('sub',fontSize=10.5,textColor=MUc,spaceAfter=10)),
    Paragraph("Measured baseline built from independent streaming and public data — no owner-supplied files. The reference "
        "point against which the impact of Recoup’s work on this asset is measured over time.",body)]
k=Table([[kpi(Mb(R['streams']['spotify_all_time']),"All-time Spotify streams"),
          kpi(Mb(R['streams']['spotify_ttm']),"Streams, trailing 12 mo."),
          kpi("~"+Dm(R['annual_nls']['central']),"Annual Net Label Share*"),
          kpi("~"+Dm(R['value']['central']),"Est. asset value*",bg=ACc,nc=colors.white,lc=colors.HexColor("#E9D5FF"))]],colWidths=[1.72*inch]*4)
k.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
story+=[Spacer(1,8),k,Spacer(1,2),Paragraph("*Directional model — streams measured live; revenue/value from public per-stream "
    "rates and labeled assumptions (see Methodology). Estimates, not reported royalties.",small)]
if R.get("distributors"):
    story+=[Spacer(1,4),Paragraph(f"<b>Owner:</b> {R['owner'] or 'n/a'}  ·  <b>Distributor(s):</b> {', '.join(R['distributors'])}  ·  <b>Recordings:</b> {R['n_tracks']}",small)]

for title,pth in charts:
    h = 3.4 if title=="Concentration" else 2.9
    story+=[Paragraph(title,h2) if title in ("Concentration",) else Spacer(1,6), Image(pth,width=6.6*inch,height=h*inch)]
    if title=="Concentration":
        story+=[Paragraph(f"The catalog is concentrated: top track <b>“{conc['top_track']}” is {conc['top_track_share']*100:.0f}%</b> of "
            f"trailing-12-month streams; the top three are {conc['top3_share']*100:.0f}%. Single-track dependency is typically "
            "underwritten at a discount and is one of the drivers of the multiple.",small)]

g=R['annual_gross']['central']; nls=R['annual_nls']['central']; df=cfg['distribution_fee']; roy=cfg['artist_producer_royalty']; m=cfg['multiple']['central']
flow=[["Annual gross receipts (all platforms, est.)",Dm(g)],
      [f"less distribution fee (~{df*100:.0f}%)","−"+Dm(g*df)],
      [f"less artist + producer royalties (~{roy*100:.0f}%)","−"+Dm(g*(1-df)*roy)],
      ["= Annual Net Label Share (NLS)",Dm(nls)],
      [f"× market multiple ({cfg['multiple']['low']}–{cfg['multiple']['high']}×, central {m}×)",f"× {m}"],
      ["= Estimated asset value (central)","~"+Dm(R['value']['central'])]]
ft=Table([[Paragraph(x,S('fa',fontSize=9.5)),Paragraph(y,S('fb',fontSize=9.5,fontName="Helvetica-Bold",alignment=2))] for x,y in flow],colWidths=[4.2*inch,1.6*inch])
ft.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LINEBELOW",(0,0),(-1,-1),0.4,GRc),("BACKGROUND",(0,3),(-1,3),LTc),("BACKGROUND",(0,5),(-1,5),colors.HexColor("#EDE9FE")),
    ("FONTNAME",(0,3),(-1,3),"Helvetica-Bold"),("LINEABOVE",(0,3),(-1,3),0.8,MUc),("LINEABOVE",(0,5),(-1,5),0.8,ACc)]))
story+=[Paragraph("Revenue &amp; valuation (directional model)",h2),
    Paragraph("Catalog value = annual Net Label Share (NLS) × a market multiple. NLS is what the label keeps after distribution "
        "and artist/producer royalties:",body),ft]
story+=[Paragraph("Methodology &amp; assumptions",h2),
    Paragraph("<b>Data.</b> Streams measured live via the Recoup Research API (Songstats), per-track current &amp; historic stats by "
    f"ISRC; ownership from public metadata. <b>Rates.</b> Public 2025 per-stream rates (Spotify ${cfg['rates']['spotify']}, "
    f"YouTube ${cfg['rates']['youtube']}, SoundCloud ${cfg['rates']['soundcloud']}); Apple/Amazon/Deezer/Tidal not exposed and "
    "approximated as a labeled gross-up; TikTok/Instagram excluded. <b>Deductions.</b> Distribution ~"
    f"{df*100:.0f}%, artist+producer ~{roy*100:.0f}%; NLS {cfg['nls_band']['low']*100:.0f}–{cfg['nls_band']['high']*100:.0f}% of gross. "
    f"<b>Multiple.</b> {cfg['multiple']['low']}–{cfg['multiple']['high']}× NLS. <b>Scope.</b> Master-side only; publishing separate. "
    "<b>Verification.</b> Every default is replaceable by a real royalty statement, which collapses the range.",small)]

def footer(c,d):
    c.saveState(); c.setStrokeColor(GRc); c.setLineWidth(0.6); c.line(0.8*inch,0.62*inch,7.7*inch,0.62*inch)
    c.setFont("Helvetica",7.5); c.setFillColor(MUc)
    c.drawString(0.8*inch,0.46*inch,f"Recoup · Confidential · Baseline as of {R['as_of']}")
    c.drawRightString(7.7*inch,0.46*inch,f"Page {c.getPageNumber()}"); c.restoreState()
pdf=f"{OUT}/{slug}-baseline-report.pdf"
SimpleDocTemplate(pdf,pagesize=letter,topMargin=0.7*inch,bottomMargin=0.8*inch,leftMargin=0.8*inch,rightMargin=0.8*inch,
    title=f"{R['asset']} Baseline Report",author="Recoup").build(story,onFirstPage=footer,onLaterPages=footer)
print("PDF:",pdf)
