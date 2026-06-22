#!/usr/bin/env python3
"""Generate an account-status package for a Recoup account.

Resolves an account (by email or account id), pulls its artists, socials,
chats, tasks, sandboxes, credits and subscription, then writes:

  <out-dir>/ACCOUNT.md
  <out-dir>/artists/INDEX.md
  <out-dir>/artists/<slug>-<shortid>/ARTIST.md   (one per artist)
  <out-dir>/<Name>-Account-Status.pdf

Auth: pass --token or set RECOUP_ACCESS_TOKEN. An admin token can read any
account via the account_id override on list endpoints.

Usage:
  python3 generate_account_status.py --email artist@example.com --out-dir ./artist-folder
  python3 generate_account_status.py --account-id <uuid> --out-dir ./artist-folder
"""
import argparse, datetime, json, os, re, sys, urllib.request, urllib.parse

BASE = os.environ.get("RECOUP_API_BASE", "https://api.recoupable.com")  # endpoint paths already include the /api prefix


def api(method, path, token, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + token,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode()), r.status
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode()), e.code
        except Exception:
            return {"_error": str(e)}, e.code
    except Exception as e:
        return {"_error": str(e)}, 0


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").strip().lower()).strip("-")
    return s or "untitled"


def fmt_ts(v):
    if not v:
        return "—"
    try:
        if isinstance(v, (int, float)):
            return datetime.datetime.utcfromtimestamp(v / 1000 if v > 1e12 else v).strftime("%Y-%m-%d")
        return str(v)[:10]
    except Exception:
        return str(v)


def platform_of(url):
    if not url:
        return "—"
    m = re.match(r"(?:https?://)?(?:www\.)?([^/]+)", url)
    return m.group(1) if m else url


def to_epoch(v):
    """Best-effort parse of an updatedAt/timestamp value to epoch seconds."""
    if not v:
        return 0
    if isinstance(v, (int, float)):
        return v / 1000 if v > 1e12 else v
    s = str(v).strip().replace("Z", "+00:00")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s[:32] if "." in s else s, fmt).timestamp()
        except Exception:
            continue
    try:
        return datetime.datetime.fromisoformat(s).timestamp()
    except Exception:
        return 0


# Theme buckets used to score/label chats from their auto-generated titles.
# (label, regex, weight) — highest-weight matched theme becomes the row's label.
CHAT_THEMES = [
    ("Strategy & frameworks", r"framework|strateg|playbook|roadmap|\bplan\b|positioning", 5),
    ("Analysis & metrics", r"analysis|audit|competitive|benchmark|metrics|\breport\b|rss", 4),
    ("Brand & growth", r"brand|proposal|growth|viral|selection|audience|outreach", 3),
    ("Research & prep", r"guide|insight|overview|scenario|\bbio\b|interview|question|research|prep", 2),
    ("Content production", r"thumbnail|image|description|caption|episode|content|photo|video|\bep\.", 1),
]


def rank_chats(chats, top_n=10):
    """Score chats by topic signal (from the title) + recency, return the top N.

    Full transcripts are not retrievable with an admin token (per-chat message
    bodies are owner-scoped), so ranking uses the auto-generated title plus how
    recently the chat was active. Each chat gets a `_theme`, `_date`, `_ts`.
    """
    for c in chats:
        c["_ts"] = to_epoch(c.get("updatedAt") or c.get("updated_at") or c.get("timestamp"))
        c["_date"] = fmt_ts(c.get("updatedAt") or c.get("updated_at") or c.get("timestamp"))
    ts_vals = [c["_ts"] for c in chats if c["_ts"]]
    newest, oldest = (max(ts_vals), min(ts_vals)) if ts_vals else (0, 0)
    span = (newest - oldest) or 1
    for c in chats:
        title = (c.get("title") or "").lower()
        score, theme, best_w = 0.0, "General", -1
        for label, pat, w in CHAT_THEMES:
            if re.search(pat, title):
                score += w
                if w > best_w:
                    best_w, theme = w, label
        if c["_ts"]:
            score += 3.0 * (c["_ts"] - oldest) / span  # recency bonus 0..3
        c["_score"], c["_theme"] = score, theme
    return sorted(chats, key=lambda c: (c["_score"], c["_ts"]), reverse=True)[:top_n]


def gather(token, email=None, account_id=None):
    # Resolve account
    if email and not account_id:
        acct, _ = api("POST", "/api/accounts", token, {"email": email})
        data = acct.get("data", acct)
        account_id = data.get("account_id") or data.get("id")
    else:
        data, _ = api("GET", f"/api/accounts/{account_id}", token)
        data = data.get("data", data)
    if not account_id:
        raise SystemExit("Could not resolve account. Check the email/id and token.")

    A = account_id
    name = (data.get("name") or "").strip() or "(unnamed)"
    emails = [e.get("email") for e in (data.get("account_emails") or []) if e.get("email")]
    primary_email = email or (emails[0] if emails else "—")
    wallets = [w.get("address") for w in (data.get("account_wallets") or []) if w.get("address")]

    sub, _ = api("GET", f"/api/accounts/{A}/subscription", token)
    credits, _ = api("GET", f"/api/accounts/{A}/credits", token)
    orgs, _ = api("GET", f"/api/organizations?account_id={A}", token)
    sandboxes, _ = api("GET", f"/api/sandboxes?account_id={A}", token)
    artists_resp, _ = api("GET", f"/api/artists?account_id={A}", token)
    artists = artists_resp.get("artists", []) or []

    enriched = []
    all_chats = []
    total_chats = total_tasks = 0
    for a in artists:
        aid = a.get("account_id") or a.get("id")
        aname = (a.get("name") or "").strip()
        socials = (api("GET", f"/api/artists/{aid}/socials", token)[0].get("socials") or [])
        chats_resp = api("GET", f"/api/chats?artist_account_id={aid}&account_id={A}", token)[0]
        chats = chats_resp.get("chats", chats_resp if isinstance(chats_resp, list) else []) or []
        tasks = (api("GET", f"/api/tasks?artist_account_id={aid}&account_id={A}", token)[0].get("tasks") or [])
        nchat = len(chats) if isinstance(chats, list) else 0
        total_chats += nchat
        total_tasks += len(tasks)
        if isinstance(chats, list):
            for c in chats:
                if isinstance(c, dict):
                    c.setdefault("_artist", aname)
                    all_chats.append(c)
        enriched.append({"id": aid, "name": aname,
                         "socials": socials, "chats": nchat, "tasks": len(tasks)})

    # Rank chats across all artists by topic signal + recency. Transcript bodies
    # are owner-scoped, so this works from each chat's auto-generated title.
    top_chats = rank_chats(all_chats, top_n=10)

    return {
        "account_id": A, "name": name, "email": primary_email, "emails": emails,
        "wallets": wallets,
        "subscription": sub, "credits": credits,
        "orgs": orgs.get("organizations", []) or [],
        "sandboxes": (sandboxes.get("sandboxes") or []) if isinstance(sandboxes, dict) else [],
        "artists": enriched, "total_chats": total_chats, "total_tasks": total_tasks,
        "top_chats": top_chats, "multi_artist": len(artists) > 1,
    }


def write_markdown(ctx, out_dir, today):
    A = ctx["account_id"]
    arts_dir = os.path.join(out_dir, "artists")
    os.makedirs(arts_dir, exist_ok=True)
    creds = ctx["credits"] if isinstance(ctx["credits"], dict) else {}
    sub = ctx["subscription"] if isinstance(ctx["subscription"], dict) else {}
    used = creds.get("used_credits", 0)
    total = creds.get("total_credits", 0)
    is_pro = sub.get("isPro", False)
    n_sandbox = len(ctx["sandboxes"])
    dormant = (ctx["total_chats"] == 0 and ctx["total_tasks"] == 0 and n_sandbox == 0 and (used or 0) == 0)
    verdict = ("**Dormant — minimal or no product engagement.** No chats, tasks, sandbox runs, or credit "
               "usage on record." if dormant else
               "**Active — the account shows real product engagement.**")

    # ACCOUNT.md
    rows = []
    for art in ctx["artists"]:
        disp = art["name"] or "(untitled)"
        folder = f"{slug(art['name'])}-{art['id'].split('-')[0]}"
        rows.append(f"| {disp} | `{folder}` | {len(art['socials'])} | {art['chats']} | {art['tasks']} |")

    # Most relevant chats — top 10 by topic signal + recency (from titles).
    top_chats = ctx.get("top_chats") or []
    if top_chats:
        show_artist = ctx.get("multi_artist")
        head = "| # | Chat | Last active | Theme |" + (" Artist |" if show_artist else "")
        sep = "|---|---|---|---|" + ("---|" if show_artist else "")
        crows = [head, sep]
        for i, c in enumerate(top_chats, 1):
            title = (c.get("title") or "(untitled)").strip().replace("|", "/")
            if len(title) > 70:
                title = title[:69].rstrip() + "…"
            extra = f" {c.get('_artist') or '—'} |" if show_artist else ""
            crows.append(f"| {i} | {title} | {c.get('_date', '—')} | {c.get('_theme', 'General')} |{extra}")
        chats_section = f"""## Most relevant chats (top {len(top_chats)} of {ctx['total_chats']})

Ranked by topic signal and recency from each chat's auto-generated title. The
theme is inferred from the title; full transcripts are not retrievable with an
admin token (see note below).

{chr(10).join(crows)}

"""
    else:
        chats_section = ""

    acct_md = f"""# Account — {ctx['name']}

_Snapshot generated {today} from the Recoup API._

## Identity

| Field | Value |
|---|---|
| Account name | {ctx['name']} |
| Sign-in email | {ctx['email']} |
| Account ID | `{A}` |
| Wallet(s) | {', '.join(ctx['wallets']) or '—'} |

## Plan & usage

| Field | Value |
|---|---|
| Subscription | {sub.get('plan') or sub.get('status') or 'None (free)'} |
| Pro status | {'Yes' if is_pro else 'No'} |
| Credits | {used or 0} used of {total or 0} granted |
| Organizations | {len(ctx['orgs'])} |
| Chats opened | {ctx['total_chats']} |
| Scheduled tasks | {ctx['total_tasks']} |
| Sandboxes | {n_sandbox} |

## Verdict

{verdict}

## Artists ({len(ctx['artists'])} records)

| Artist | Folder | Socials | Chats | Tasks |
|---|---|---|---|---|
{chr(10).join(rows) if rows else '| _none_ | | | | |'}

{chats_section}> Notes:
> - Pre-migration sessions may not surface in current endpoints; cross-check usage signals.
> - Chat summaries are derived from each chat's auto-generated title. An admin token's
>   `account_id` override is honored for list reads (chats, artists, tasks) but per-chat
>   message bodies are owner-scoped and return `Forbidden`/`Chat room not found`. Use an
>   owner-scoped token for the account to produce transcript-level summaries.
"""
    with open(os.path.join(out_dir, "ACCOUNT.md"), "w") as f:
        f.write(acct_md)

    # Per-artist ARTIST.md + index
    idx = ["# Artists index\n", f"_{len(ctx['artists'])} records under account `{A}` ({ctx['name']} / {ctx['email']})._\n",
           "| Artist | Folder | Socials | Chats | Tasks |", "|---|---|---|---|---|"]
    for art in ctx["artists"]:
        disp = art["name"] or "(untitled)"
        folder = f"{slug(art['name'])}-{art['id'].split('-')[0]}"
        fdir = os.path.join(arts_dir, folder)
        os.makedirs(fdir, exist_ok=True)
        if art["socials"]:
            srows = ["| Platform | Handle | Followers | Last updated |", "|---|---|---|---|"]
            for s in art["socials"]:
                foll = s.get("followerCount") or s.get("follower_count") or s.get("followers")
                foll = f"{foll:,}" if isinstance(foll, int) else "—"
                srows.append(f"| {platform_of(s.get('profile_url'))} | {s.get('username') or '—'} | {foll} | {fmt_ts(s.get('updated_at'))} |")
            socials_md = "\n".join(srows)
        else:
            socials_md = "_No socials connected._"
        art_md = f"""# {disp}

**Artist account ID:** `{art['id']}`
**Owning account:** {ctx['name']} · {ctx['email']} (`{A}`)
**Socials connected:** {len(art['socials'])}
**Chats:** {art['chats']} · **Scheduled tasks:** {art['tasks']}

_Snapshot generated {today} from the Recoup API._

## Socials connected

{socials_md}

## Chats

{('_No chats opened._' if art['chats'] == 0 else f"{art['chats']} chat(s) on record.")}

## Scheduled tasks

{('_No scheduled tasks._' if art['tasks'] == 0 else f"{art['tasks']} task(s) on record.")}

## Notes

- _Add context, brand, and next steps here as we build this artist's plan._
"""
        with open(os.path.join(fdir, "ARTIST.md"), "w") as f:
            f.write(art_md)
        idx.append(f"| {disp} | `{folder}` | {len(art['socials'])} | {art['chats']} | {art['tasks']} |")
    with open(os.path.join(arts_dir, "INDEX.md"), "w") as f:
        f.write("\n".join(idx) + "\n")
    return dormant


def build_pdf(ctx, out_dir, today, dormant):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                         TableStyle, HRFlowable, PageBreak)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
    except ImportError:
        print("reportlab not installed — skipping PDF (pip install reportlab --break-system-packages)")
        return None

    NAVY, ACCENT, GREY, LIGHT = (colors.HexColor(c) for c in ("#1a2b4a", "#2f6df0", "#5b6472", "#eef1f6"))
    st = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=st["Title"], textColor=NAVY, fontSize=22, alignment=TA_LEFT, spaceAfter=2)
    SUB = ParagraphStyle("SUB", parent=st["Normal"], textColor=GREY, fontSize=10)
    H2 = ParagraphStyle("H2", parent=st["Heading2"], textColor=NAVY, fontSize=13, spaceBefore=14, spaceAfter=6)
    BODY = ParagraphStyle("BODY", parent=st["Normal"], fontSize=9.5, leading=14)
    CELL = ParagraphStyle("CELL", parent=st["Normal"], fontSize=8.5, leading=11)
    CELLB = ParagraphStyle("CELLB", parent=CELL, fontName="Helvetica-Bold")
    # White bold cell for dark navy header rows. A Paragraph carries its own text
    # color, so a TableStyle TEXTCOLOR alone won't whiten header text — use this.
    CELLBW = ParagraphStyle("CELLBW", parent=CELLB, textColor=colors.white)
    NOTE = ParagraphStyle("NOTE", parent=st["Normal"], fontSize=8, leading=11, textColor=GREY)
    creds = ctx["credits"] if isinstance(ctx["credits"], dict) else {}
    sub = ctx["subscription"] if isinstance(ctx["subscription"], dict) else {}

    story = [Paragraph(f"Account Status &mdash; {ctx['name']}", H1),
             Paragraph(f"Recoup account health snapshot &nbsp;|&nbsp; Prepared {today}", SUB),
             HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=6, spaceAfter=10)]
    ident = [["Account name", ctx["name"], "Sign-in email", ctx["email"]],
             ["Account ID", ctx["account_id"], "Organizations", str(len(ctx["orgs"]))]]
    t = Table([[Paragraph(c, CELLB if i % 2 == 0 else CELL) for i, c in enumerate(r)] for r in ident],
              colWidths=[1.1*inch, 2.2*inch, 1.1*inch, 2.1*inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d4dae6")),
                           ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 7)]))
    story += [t, Spacer(1, 12)]
    vtxt = ("Dormant &mdash; minimal or no product engagement." if dormant else "Active &mdash; real product engagement.")
    v = Table([[Paragraph(f"<b>Verdict: {vtxt}</b>", ParagraphStyle("v", parent=BODY, textColor=colors.white, fontSize=10.5))]],
              colWidths=[6.5*inch])
    v.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("TOPPADDING", (0, 0), (-1, -1), 8),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 10)]))
    story.append(v)

    story.append(Paragraph("Product engagement", H2))
    eng = [["Metric", "Value", "Metric", "Value"],
           ["Chats opened", str(ctx["total_chats"]), "Scheduled tasks", str(ctx["total_tasks"])],
           ["Sandboxes", str(len(ctx["sandboxes"])), "Credits used", f"{creds.get('used_credits', 0)} of {creds.get('total_credits', 0)}"],
           ["Subscription", (sub.get("plan") or sub.get("status") or "None"), "Pro", "Yes" if sub.get("isPro") else "No"]]
    te = Table([[Paragraph(c, CELLBW if ri == 0 else (CELLB if ci % 2 == 0 else CELL)) for ci, c in enumerate(r)] for ri, r in enumerate(eng)],
               colWidths=[1.65*inch, 1.7*inch, 1.65*inch, 1.5*inch])
    te.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d4dae6")),
                            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d4dae6")),
                            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 7)]))
    story.append(te)

    story.append(Paragraph(f"Artists ({len(ctx['artists'])} records)", H2))
    arows = [["Artist", "Socials", "Chats", "Tasks"]]
    for a in ctx["artists"]:
        arows.append([a["name"] or "(untitled)", str(len(a["socials"])), str(a["chats"]), str(a["tasks"])])
    ta = Table([[Paragraph(c, CELLBW if ri == 0 else CELL) for c in r] for ri, r in enumerate(arows)],
               colWidths=[3.0*inch, 1.4*inch, 1.05*inch, 1.05*inch])
    ta.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d4dae6")),
                            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d4dae6")),
                            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 7)]))
    story.append(ta)

    # Most relevant chats — new page, white headers.
    top_chats = ctx.get("top_chats") or []
    if top_chats:
        show_artist = ctx.get("multi_artist")
        story.append(PageBreak())
        story.append(Paragraph(f"Most relevant chats (top {len(top_chats)} of {ctx['total_chats']})", H2))
        story.append(Paragraph(
            "Ranked by topic signal and recency from each chat's auto-generated title. The theme is "
            "inferred from the title; full transcripts are not retrievable with an admin token.", BODY))
        story.append(Spacer(1, 8))
        header = ["#", "Chat", "Last active", "Theme"] + (["Artist"] if show_artist else [])
        crows = [header]
        for i, c in enumerate(top_chats, 1):
            title = (c.get("title") or "(untitled)").strip()
            if len(title) > 78:
                title = title[:77].rstrip() + "…"
            row = [str(i), title, c.get("_date", "—"), c.get("_theme", "General")]
            if show_artist:
                row.append(c.get("_artist") or "—")
            crows.append(row)
        widths = ([0.3*inch, 3.05*inch, 0.95*inch, 1.55*inch, 1.05*inch] if show_artist
                  else [0.3*inch, 3.7*inch, 1.0*inch, 1.9*inch])
        tc = Table([[Paragraph(c, CELLBW if ri == 0 else CELL) for c in r] for ri, r in enumerate(crows)],
                   colWidths=widths, repeatRows=1)
        tc.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d4dae6")),
                                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d4dae6")),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
        story.append(tc)
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Data note: Summaries are derived from each chat's auto-generated title (created from its "
            "opening prompt). The admin token's account_id override is honored for list reads but per-chat "
            "message bodies are owner-scoped and return Forbidden. An owner-scoped token for the account "
            "would allow transcript-level summaries.", NOTE))

    out = os.path.join(out_dir, f"{slug(ctx['name'])}-Account-Status.pdf")
    SimpleDocTemplate(out, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.6*inch,
                      leftMargin=0.75*inch, rightMargin=0.75*inch, title=f"{ctx['name']} - Account Status").build(story)
    return out


def main():
    p = argparse.ArgumentParser(description="Generate a Recoup account-status package.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--email")
    g.add_argument("--account-id")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--token", default=os.environ.get("RECOUP_ACCESS_TOKEN", ""))
    args = p.parse_args()
    if not args.token:
        sys.exit("No token. Pass --token or set RECOUP_ACCESS_TOKEN.")
    today = datetime.date.today().strftime("%B %-d, %Y")
    os.makedirs(args.out_dir, exist_ok=True)
    ctx = gather(args.token, email=args.email, account_id=args.account_id)
    dormant = write_markdown(ctx, args.out_dir, today)
    pdf = build_pdf(ctx, args.out_dir, today, dormant)
    print(f"Account: {ctx['name']} ({ctx['account_id']})")
    print(f"Artists: {len(ctx['artists'])} | chats={ctx['total_chats']} tasks={ctx['total_tasks']}")
    print(f"Wrote ACCOUNT.md, artists/ tree" + (f", and {os.path.basename(pdf)}" if pdf else ""))


if __name__ == "__main__":
    main()
