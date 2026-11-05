"""Turn a word-timestamp transcript into timed lyric lines, tagged with the measured section.

usage: lines_from_transcript.py <transcript.json> <measurement.json> <lyrics.lines.json>

transcript.json is the POST /api/content/transcribe response ({"segments": [{start, end, text}]}
with word-level chunks); measurement.json is the POST /api/songs/moments response. A line breaks
on a pause longer than 0.7 s, on sentence punctuation, or at 14 words. Stdlib only.
"""
import json
import sys


def wants_help(nargs):
    """Print the module docstring and exit when asked, or when arguments are missing."""
    asked = len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help")
    if asked or len(sys.argv) - 1 < nargs:
        print(__doc__.strip())
        sys.exit(0 if asked else 2)


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main():
    wants_help(3)
    tx, meas = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
    words = [s for s in tx.get("segments", []) if s.get("text", "").strip()]
    lines, cur = [], []

    def flush():
        if cur:
            lines.append({"start": round(cur[0]["start"], 2), "end": round(cur[-1]["end"], 2),
                          "text": " ".join(w["text"].strip() for w in cur)})
            cur.clear()

    for i, w in enumerate(words):
        if cur and (w["start"] - cur[-1]["end"] > 0.7 or len(cur) >= 14):
            flush()
        cur.append(w)
        if w["text"].strip().endswith((".", "?", "!")):
            flush()
    flush()

    sections = meas.get("sections", [])
    for ln in lines:
        mid = (ln["start"] + ln["end"]) / 2
        sec = next((s for s in sections if s["start"] <= mid < s["end"]), None)
        ln["section"] = sec["label"] if sec else None
        ln["mmss"] = mmss(ln["start"])

    # Repeated lines (the hook) and the first time each appears.
    seen = {}
    for ln in lines:
        key = ln["text"].lower()
        seen.setdefault(key, []).append(ln["mmss"])
    repeats = sorted(((k, v) for k, v in seen.items() if len(v) > 1), key=lambda kv: -len(kv[1]))[:5]

    out = {"lines": lines, "line_count": len(lines), "repeated_lines": [{"text": k, "at": v} for k, v in repeats],
           "word_count": len(words),
           "source": "word timestamps from the transcription route; lines split on pauses"}
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    print(len(words), "words;", len(lines), "lines;", "repeats:", [(r["text"][:40], len(r["at"])) for r in out["repeated_lines"]])
    for ln in lines[:8]:
        print(ln["mmss"], ln["section"], ln["text"][:80])


if __name__ == "__main__":
    main()
