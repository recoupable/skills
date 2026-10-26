#!/bin/zsh
# Build + render hybrid shorts one at a time (retries), then a 0.3 s fade-out on the last word and a two-pass
# loudness pass to -14 LUFS.
#   scripts/podcast/shorts/render.sh <project> s1:<slug> s2:<slug> ...     -> <project>/exports/shorts/<slug>.mp4
#   RECUT=1 ...      re-cut the media first (after a cut-list change)
#   STOP_AT=0830 ... never START a render at/after 08:30 local (live recordings need the CPU)
# Renders run ~3-5x realtime on an Intel laptop; run ONE at a time (parallel load makes the headless-Chrome
# launch check time out; the retry covers a one-off). A background job can be killed mid-queue: re-run the
# missing ones. Snapshot each short's beats before rendering (see references/podcast-shorts.md).
HERE=${0:A:h}; PROJ=${1:A}; shift
mkdir -p $PROJ/exports/shorts
for pair in "$@"; do
  sid=${pair%%:*}; slug=${pair#*:}; raw=$PROJ/exports/shorts/$sid-raw.mp4; log=$PROJ/exports/shorts/render-$sid.log
  if [[ -n "$STOP_AT" && $(date +%H%M) -ge $STOP_AT ]]; then echo "STOP_AT $STOP_AT reached before $sid; stopping"; exit 0; fi
  python3 $HERE/build_hy.py $PROJ $sid $([[ -n "$RECUT" ]] && echo --recut) > $PROJ/exports/shorts/build-$sid.log 2>&1 || { echo "$sid build failed (exports/shorts/build-$sid.log)"; continue; }
  for try in 1 2 3; do
    (cd $PROJ/comp/shorts/$sid && npx --yes hyperframes render -o $raw > $log 2>&1)
    grep -q "Render complete" $log && break; echo "$sid try $try failed: $(grep -iE 'failed|error' $log | head -1)"
  done
  grep -q "Render complete" $log || continue
  # the last word fades out over 0.3 s ending 0.1 s before the clip end (the rendered audio stops ~0.07 s early),
  # so there is no hard stop; the end card is silent
  clip=$(grep -o 'id="mix"[^>]*data-duration="[0-9.]*"' $PROJ/comp/shorts/$sid/index.html | grep -o '[0-9.]*"$' | tr -d '"')
  fade=; [[ -n "$clip" ]] && fade="afade=t=out:st=$(( clip - 0.4 )):d=0.3,"
  J=$(ffmpeg -hide_banner -i $raw -af ${fade}loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -v error -y -i $raw -c:v copy -af "${fade}loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" \
    -ar 48000 -c:a aac -b:a 192k -movflags +faststart $PROJ/exports/shorts/$slug.mp4
  echo "$sid ok: exports/shorts/$slug.mp4 $(ffmpeg -hide_banner -i $PROJ/exports/shorts/$slug.mp4 -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | tail -1 | tr -s ' ')"
done
