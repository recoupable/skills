"""Deterministic fact check of a composed report against its inputs.

usage: fact_check.py <report.json> <measurement.json> <answers.json> <context.json> [lyrics.lines.json]

Exit 0 when clean; prints every violation and exits 1 otherwise. This is the fact critic for
everything a machine can check; a reader still judges taste. With lyrics.lines.json (timed lines
from lines_from_transcript.py) quotes may also come from the transcript, and a timestamp that
sits inside any lyric line is allowed. When the measurement has no loudness or true peak (a
measurement made before those fields existed), any LUFS or dBTP figure in the report fails,
because nothing measured it. Stdlib only.
"""
import json
import re
import sys

TS = re.compile(r"\b(\d{1,2}):(\d{2})\b")
# Only double quotes count as quotations; single quotes are apostrophes in lyric prose.
QUOTE = re.compile(r"[\"“]([^\"”]{4,120})[\"”]()")


def seconds(m, s):
    return int(m) * 60 + int(s)


def walk_strings(o, path="report"):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_strings(v, f"{path}[{i}]")


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("’", "'"))


def main():
    if len(sys.argv) < 5 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help") else 2)
    report, meas, answers, ctx = (json.load(open(p)) for p in sys.argv[1:5])
    lyrics = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {"lines": []}
    lyric_norm = norm(" ".join(ln["text"] for ln in lyrics["lines"]))
    lyric_spans = [(ln["start"], ln["end"]) for ln in lyrics["lines"]]
    allowed_times = set()
    for s in meas["sections"]:
        allowed_times.update({s["start"], s["end"]})
    for m in meas["moments"]:
        allowed_times.update({m["start"], m["end"]})
        for c in m["cuts"].values():
            allowed_times.update(c)
    for d in meas.get("mute_drops", []):
        allowed_times.update({d["start"], d["end"]})
    for e in meas.get("edit_points", []):
        allowed_times.add(e["time"])
    allowed_times.add(meas["duration_seconds"])
    answer_text = " ".join(str(v) for v in answers.values())
    answer_times = {seconds(a, b) for a, b in TS.findall(answer_text)}
    answer_norm = norm(answer_text)
    ctx_text = norm(json.dumps(ctx))

    problems = []
    for path, text in walk_strings(report):
        for a, b in TS.findall(text):
            t = seconds(a, b)
            if t in answer_times or any(abs(t - x) <= 2 for x in allowed_times):
                continue
            if any(s - 1 <= t <= e + 1 for s, e in lyric_spans):
                continue
            problems.append(f"TIME {a}:{b} at {path} not within 2 s of any measured point, lyric line or model answer")
        for q1, q2 in QUOTE.findall(text):
            q = norm(q1 or q2)
            if len(q.split()) >= 3 and q not in answer_norm and q not in ctx_text and q not in lyric_norm:
                problems.append(f"QUOTE {q1 or q2!r} at {path} not found in answers, context or transcript")

    # Numbers the report must copy from the measurement.
    ident = report.get("identity", {})
    if abs(float(ident.get("tempo_bpm", 0)) - meas["tempo_bpm"]) > 1.5:
        problems.append(f"TEMPO {ident.get('tempo_bpm')} vs measured {meas['tempo_bpm']}")
    if ident.get("duration_mmss") and ident["duration_mmss"] != f"{int(meas['duration_seconds'] // 60)}:{int(meas['duration_seconds'] % 60):02d}":
        problems.append(f"DURATION {ident['duration_mmss']} vs measured {meas['duration_seconds']}")
    blob = json.dumps(report)
    lufs = meas.get("lufs", meas.get("loudness_lufs"))
    for pat, val, label in [(r"-?\d+(?:\.\d+)? ?LUFS", lufs, "LUFS"), (r"[+-]?\d+(?:\.\d+)? ?dBTP", meas.get("true_peak_dbtp"), "true peak")]:
        for hit in re.findall(pat, blob):
            if val is None:
                problems.append(f"{label} {hit} quoted but the measurement has no {label} value")
                continue
            num = float(re.findall(r"[+-]?\d+(?:\.\d+)?", hit)[0])
            if abs(num - val) > 0.15:
                problems.append(f"{label} {hit} vs measured {val}")

    # Names: every capitalised multi-word name in writers/producers/artists fields must be in context.
    for field in ("artists", "writers", "producers", "year", "label"):
        v = ident.get(field)
        if v and norm(str(v)) not in ctx_text:
            problems.append(f"IDENTITY {field}={v!r} not in context")
    for song in report.get("market", {}).get("comparable_songs", []) or []:
        if norm(song.get("title", "")) not in ctx_text:
            problems.append(f"COMPARABLE SONG {song.get('title')!r} not confirmed in context")

    # Score arithmetic.
    sc = report.get("score", {})
    w = {"hook": 20, "production": 20, "songwriting": 15, "structure": 10, "vocal": 10, "sync_utility": 15, "market": 10}
    if sc.get("subscores"):
        total = round(sum(sc["subscores"].get(k, 0) * wt for k, wt in w.items()) / 10)
        if abs(total - int(sc.get("total", -1))) > 1:
            problems.append(f"SCORE total {sc.get('total')} vs rubric {total}")

    # Three bullets, typed.
    for name, card in (report.get("dimensions") or {}).items():
        kinds = [b.get("kind") for b in card.get("bullets", [])]
        if sorted(kinds) != ["neutral", "risk", "strength"]:
            problems.append(f"BULLETS {name}: {kinds}")

    # One fact, one home: measured figures and findings must not recur through the prose.
    # Structural fields (times on moments, key lines, edit points, scenes; identity; score;
    # technical notes) are exempt; everything else is reader prose.
    prose = []
    for path, text in walk_strings(report):
        tail = path.split(".")[-1].split("[")[0]
        if path.startswith(("report.technical", "report.identity", "report.score", "report.sonic_identity.moods")):
            continue
        if tail in ("time", "cut", "cut_15", "6", "15", "30", "lyric", "line", "tag", "band", "kind", "type", "name", "medium", "era", "url", "deep_dive") and "review" not in path:
            continue
        prose.append(text)
    blob = " ".join(prose)
    figures = re.findall(r"[+\-−]?\d+(?:\.\d+)? ?(?:dBTP|dB|LUFS|%|LU)\b", blob)
    counts = {}
    for f in figures:
        counts[f] = counts.get(f, 0) + 1
    for f, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n > 2:
            problems.append(f"REPEAT figure {f!r} appears {n} times in reader prose (max 2)")
    # Findings, not strings: a finding keeps its meaning under any wording, so each group of
    # words that names the same finding is counted together. Home section (3 mentions) + 3
    # elsewhere is the ceiling; past that the report is leaning on one thing. These groups are
    # the findings most songs share; each report adds its own below.
    FINDINGS = {
        "the bad file": r"\bclip(?:s|ped|ping)?\b|\bruns hot\b|\btoo hot\b|\bpeak(?:s|ing)? (?:at|above|over|past)\b|\btrue peak\b|\bdBTP\b|\bbroadcast\b|\blossless\b|\bdeliverable\b|\bdelivery master\b|\bpeak-safe\b|\bthis (?:MP3|file)\b|\bthe (?:MP3|file) (?:is|was|sits|measures|clips|distorts)\b|\bremaster(?:ed|ing)?\b",
        "the stops and gaps": r"\bstop[- ]hits?\b|\bstops?\b(?! short)|\bmutes?\b|\bholes?\b|\bgaps?\b|\bdrop[- ]outs?\b",
        "the dull top end": r"\bair\b|\bveiled\b|\bdull\b|\bdark top\b|\babove 6 ?kHz\b|\bno sparkle\b|\bmuffled\b",
        "the wait before the hook": r"\brunway\b|\bbefore the hook\b|\bwaits? for the chorus\b|\bslow start\b",
        "the long final chorus": r"\bover a minute\b|\bfinal chorus (?:run|block)\b|\bplateaus?\b|\bruns long\b",
        "the near-silence": r"\bnear[- ]silen(?:ce|t)\b|\bsilence\b|\bthe hole\b|\bfalls? away\b|\bdrops? away\b|\bbreakdown\b|\bthe band (?:drops|falls|vanishes|disappears)\b",
        "the public-record placement": r"\bpublic record\b|\bplaced\b|\bplacement\b",
    }
    # The report's own declared findings (schema: technical.findings) are counted the same way,
    # so the rule follows each song. The shared groups above still apply when they match.
    declared = report.get("technical", {}).get("findings") or []
    if len(declared) < 4:
        problems.append("FINDINGS technical.findings must declare at least four repeated findings")
    for f in declared:
        words = [re.escape(w.strip().lower()) for w in f.get("words", []) if w.strip()]
        if words:
            FINDINGS[f"declared: {f.get('id')}"] = r"\b(?:" + "|".join(words) + r")\b"
    for finding, pat in FINDINGS.items():
        n = len(re.findall(pat, blob, re.I))
        if n > 6:
            problems.append(f"REPEAT finding {finding!r} named {n} times in reader prose under any wording (max 6)")
    # Identity fields carry values only; provenance belongs in technical.notes. A title may
    # carry its own parentheses ("Song (Acoustic)"), so it is exempt.
    for k, v in (report.get("identity") or {}).items():
        if isinstance(v, str) and re.search(r"\(|measured|model|metadata|confidence", v, re.I) and k not in ("key_source", "title"):
            problems.append(f"IDENTITY {k}={v!r} carries a parenthetical or provenance word; keep the value plain")
    tcounts = {}
    for a, b in TS.findall(blob):
        tcounts[f"{a}:{b}"] = tcounts.get(f"{a}:{b}", 0) + 1
    for t, n in sorted(tcounts.items(), key=lambda kv: -kv[1]):
        if n > 6:
            problems.append(f"REPEAT timestamp {t} appears {n} times in reader prose (max 6)")
    for jargon in ("valence", "arousal", "side-to-mid", "side to mid", "flagged", "crest factor", "centroid", "confidence", "listening model", "measured edge", "energy scale", "per file metadata"):
        if re.search(r"\b" + re.escape(jargon) + r"\b", blob, re.I):
            problems.append(f"JARGON {jargon!r} in reader prose; keep it in technical.notes or say what it sounds like")

    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s)")
        sys.exit(1)
    print("clean")


if __name__ == "__main__":
    main()
