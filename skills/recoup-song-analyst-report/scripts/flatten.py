"""Flatten a report JSON into plain text: a readable text version and input for text critics.

usage: flatten.py <report.json> <report.txt>

Stdlib only.
"""
import json
import sys


def wants_help(nargs):
    """Print the module docstring and exit when asked, or when arguments are missing."""
    asked = len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help")
    if asked or len(sys.argv) - 1 < nargs:
        print(__doc__.strip())
        sys.exit(0 if asked else 2)


def main():
    wants_help(2)
    r = json.load(open(sys.argv[1]))
    out = []
    h = lambda t: out.append("\n## " + t)  # noqa: E731
    p = lambda t: out.append(str(t))  # noqa: E731

    h("Identity"); p(json.dumps(r["identity"]))
    v = r["verdict"]
    h("Verdict"); p(v["headline"]); p(v["subhead"])
    for b in v["bullets"]:
        p(f"- [{b['kind']}] {b['text']}")
    if v.get("emotional_position"):
        p("Emotional position: " + json.dumps(v["emotional_position"]))
    for s in v["review"]:
        p(f"### {s['heading']} (deep dive: {s.get('deep_dive', '')})")
        [p(x) for x in s["paragraphs"]]
    f = r["first_impression"]
    h("First impression")
    for k in ("opening_read", "sonic_landscape", "production_quality"):
        p("### " + k); p(f[k])
    p("### standout moments")
    for m in f["standout_moments"]:
        cuts = m.get("cuts") or {"15": m.get("cut_15", "")}
        p(f"- {m['time']} {m.get('lyric', '')} | {m['what']} | {m['why']} | cuts {json.dumps(cuts)} | use {m.get('use', '')}")
    for k in ("emotional_texture", "weaknesses", "lyrics_and_narrative", "artist_context", "quality_calibration"):
        if f.get(k):
            p("### " + k); p(f[k])
    h("Dimension cards")
    for k, c in r["dimensions"].items():
        p("### " + k); p(c["summary"])
        [p(f"- [{b['kind']}] {b['text']}") for b in c["bullets"]]
    s = r["sonic_identity"]
    h("Sonic identity"); p(s["headline"]); p(s["subhead"]); p("moods " + json.dumps(s["moods"])); p(s["fingerprint_note"])
    [p(f"- ISSUE {x['title']} {x.get('time', '')}: {x['problem']} FIX: {x['fix']}") for x in s["issues"]]
    c = r["production_craft"]
    h("Production craft"); p(c["headline"]); p(c["subhead"])
    [p(f"- {b['band']}: {b['annotation']} — {b['note']}") for b in c["bands"]]
    [p(x) for x in c["approach"]]
    for m in c["mix"]:
        p("### " + m["heading"]); [p(x) for x in m["paragraphs"]]
    [p("- technique: " + t) for t in c.get("techniques", [])]
    [p(f"- ISSUE {x['title']} {x.get('time', '')}: {x['problem']} FIX: {x['fix']}") for x in c["issues"]]
    s = r["songwriting"]
    h("Songwriting"); [p(s[k]) for k in ("headline", "craft", "narrative_arc", "theme")]
    [p(f"- {k['time']} “{k['line']}” — {k['why']}") for k in s["key_lines"]]
    s = r["structure"]
    h("Structure"); [p(s[k]) for k in ("headline", "form", "dynamics", "creative_dna")]
    m = r["market"]
    h("Market"); p(m["positioning"]); p(json.dumps(m["audience"])); p("playlists " + json.dumps(m["playlist_fits"])); p("influence " + json.dumps(m["influence_map"]))
    [p(f"- artist {a['name']} ({a.get('era', '')}): {a['why']}") for a in m["comparable_artists"]]
    [p(f"- song {a['title']} · {a['artist']}: {a['why']}") for a in m.get("comparable_songs", [])]
    [p(f"- brand {a['category']}: {a['angle']} ({a['cut']})") for a in m.get("brand_categories", [])]
    s = r["sync"]
    h("Sync"); p(s["headline"]); p(s["pitch"]); [p("- sell: " + x) for x in s["sell"]]
    [p(f"- scene {x['name']} [{x.get('medium', '')}] @ {x['time']} cuts {json.dumps(x.get('cuts', {}))}: {x['why']}") for x in s["scene_archetypes"]]
    [p(f"- edit {x['type']} {x['time']} {x['name']}: {x['note']}") for x in s["edit_points"]]
    for o in s["observations"]:
        p("### " + o["heading"]); [p(x) for x in o["paragraphs"]]
    [p(f"- ISSUE {x['title']} {x.get('time', '')}: {x['problem']} FIX: {x['fix']}") for x in s["issues"]]
    g = r["growth"]
    h("Growth"); p(g["headline"]); [p(f"- {o['what']}: {o['why']}") for o in g["opportunities"]]
    h("Score"); p(json.dumps(r["score"]))
    h("Technical notes"); [p("- " + n) for n in r["technical"]["notes"]]
    text = "\n".join(out)
    open(sys.argv[2], "w").write(text)
    print(len(text.split()), "words")


if __name__ == "__main__":
    main()
