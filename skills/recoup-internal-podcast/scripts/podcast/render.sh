#!/bin/zsh
# Re-cut + build + render chapters one at a time, with retries.
#   scripts/podcast/render.sh <project> ch01 ch02 ...            (recut + build + render each)
#   NO_RECUT=1 scripts/podcast/render.sh <project> ch04          (graphics-only change: skip the media cut)
#   STOP_AT=0830 scripts/podcast/render.sh <project> ch05 ch06   (never START a render at/after 08:30 local)
# Renders run ~3-5x realtime on an Intel laptop. Run ONE at a time: parallel CPU load makes the
# headless-Chrome launch check time out (the retry covers a one-off). STOP_AT exists because a
# background timer meant to kill renders before a live recording was itself killed first; check the
# clock here, in the loop, before every render. Outputs land in <project>/exports/<ch>.mp4.
HERE=${0:A:h}; PROJ=${1:A}; shift
mkdir -p $PROJ/exports
for c in "$@"; do
  if [[ -n "$STOP_AT" && $(date +%H%M) -ge $STOP_AT ]]; then echo "STOP_AT $STOP_AT reached before $c; stopping"; exit 0; fi
  python3 $HERE/build.py $PROJ $c $([[ -z "$NO_RECUT" ]] && echo --recut) > $PROJ/exports/build-$c.log 2>&1 || { echo "$c build failed (exports/build-$c.log)"; continue; }
  for try in 1 2 3; do
    (cd $PROJ/comp/chapters/$c && npx --yes hyperframes render -o $PROJ/exports/$c.mp4 > $PROJ/exports/render-$c.log 2>&1)
    if grep -q "Render complete" $PROJ/exports/render-$c.log; then echo "$c ok: $(grep -E 'MB ·' $PROJ/exports/render-$c.log | tr -s ' ')"; break; fi
    echo "$c try $try failed: $(grep -iE 'failed|error' $PROJ/exports/render-$c.log | head -1)"
  done
done
