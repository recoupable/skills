#!/usr/bin/env python3
"""Per-line VO generator (ElevenLabs), the house template. Copy into <project>/video/ next to a lines.json.

  lines.json: {"voice_id": "...", "model_id": "eleven_v3", "stability": 0.3, "similarity_boost": 0.75,
               "lines": [{"id": "01", "text": "..."}, {"id": "02", "text": "...", "approved": "assets/voice/01.wav"}]}
  python3 gen-voice.py            # every line
  python3 gen-voice.py 02 07      # only those ids; every other line is kept from audio_meta.json

Each line: raw pcm_24000 take in assets/voice/raw/<id>.wav, then measured linear gain + true-peak limiter
to -16 LUFS in assets/voice/<id>.wav (voice.md), word timings from the alignment into audio_meta.json,
then one REVIEW file of every line in order with 0.6s gaps for the owner to hear before compositing.
A line with "approved" copies that file instead of generating (an owner-approved take never changes);
its word timings come from <approved>.scribe.json if present.
"""
import base64, json, os, shutil, subprocess, sys, time, wave, urllib.request
KEY = os.environ.get("ELEVENLABS_API_KEY") or [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser(os.environ.get("ELEVENLABS_ENV", ".env"))) if l.startswith("ELEVENLABS_API_KEY=")][0]
CFG = json.load(open("lines.json")); RATE = 24000; TARGET = -16.0
ONLY = set(sys.argv[1:]); os.makedirs("assets/voice/raw", exist_ok=True)
OLD = {v["id"]: v for v in json.load(open("audio_meta.json"))["voices"]} if os.path.exists("audio_meta.json") else {}
def lufs(p):
    m = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in m.splitlines() if " I:" in l][-1].split()[1]), float([l for l in m.splitlines() if "Peak:" in l][-1].split()[1])
def words_of(al):
    out, cur, w0, pe = [], "", None, 0
    for c, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.strip() == "":
            if cur: out.append({"text": cur, "start": round(w0, 3), "end": round(pe, 3)}); cur = ""
            continue
        if not cur: w0 = s
        cur += c; pe = e
    if cur: out.append({"text": cur, "start": round(w0, 3), "end": round(pe, 3)})
    return out
def normalise(raw, out):
    I, P = lufs(raw); gain = TARGET - I
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"volume={gain:+.1f}dB,aresample=96000,alimiter=limit=0.84:attack=1:release=80:level=disabled,aresample={RATE}", out], check=True)
    I2, P2 = lufs(out); return I, gain, I2, P2
voices = []
for ln in CFG["lines"]:
    lid, text = ln["id"], ln["text"]
    if ONLY and lid not in ONLY and lid in OLD: voices.append(OLD[lid]); continue
    out = f"assets/voice/{lid}.wav"
    if ln.get("approved"):
        shutil.copy(ln["approved"], out)
        with wave.open(out) as w: dur = w.getnframes() / w.getframerate()
        sc = ln["approved"].rsplit(".", 1)[0] + ".scribe.json"
        words = [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in json.load(open(sc)).get("words", []) if w.get("type", "word") == "word"] if os.path.exists(sc) else None
        voices.append({"id": lid, "path": out, "text": text, "duration_s": round(dur, 3), "words": words, "note": "approved take, copied"}); print(f"{lid}: approved take {dur:.2f}s"); continue
    for attempt in range(4):
        try:
            rq = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{CFG['voice_id']}/with-timestamps?output_format=pcm_24000",
                data=json.dumps({"text": text, "model_id": CFG.get("model_id", "eleven_v3"), "voice_settings": {"stability": CFG.get("stability", 0.3), "similarity_boost": CFG.get("similarity_boost", 0.75)}}).encode(),
                headers={"xi-api-key": KEY, "Content-Type": "application/json"})
            body = json.load(urllib.request.urlopen(rq, timeout=180)); break
        except Exception as e:
            if attempt == 3: raise
            print(f"  retry {lid} ({e})"); time.sleep(4 + 4 * attempt)
    pcm = base64.b64decode(body["audio_base64"]); raw = f"assets/voice/raw/{lid}.wav"
    with wave.open(raw, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm)
    I, gain, I2, P2 = normalise(raw, out); dur = len(pcm) / 2 / RATE
    voices.append({"id": lid, "path": out, "text": text, "duration_s": round(dur, 3), "words": words_of(body["alignment"]), "raw_lufs": I, "gain_db": round(gain, 1), "lufs": I2, "peak_dbtp": P2})
    print(f"{lid}: {dur:5.2f}s  raw {I} -> {I2} LUFS / {P2} dBTP")
json.dump({"tts_provider": "elevenlabs", "voice_id": CFG["voice_id"], "model": CFG.get("model_id", "eleven_v3"), "voices": voices}, open("audio_meta.json", "w"), indent=1)
ins = []; n = len(voices)
for v in voices: ins += ["-i", v["path"]]
filt = "".join(f"[{i}:a]apad=pad_dur=0.6[a{i}];" for i in range(n)) + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", filt, "-map", "[o]", "assets/voice/REVIEW-all-lines.wav"], check=True)
print(f"review file: assets/voice/REVIEW-all-lines.wav, total VO {sum(v['duration_s'] for v in voices):.1f}s")
