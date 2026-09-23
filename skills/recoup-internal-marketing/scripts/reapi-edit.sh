#!/usr/bin/env bash
# Character-swap edit on reAPI Seedance 2.5 (see references/character-swap-edit.md).
#
# Usage: reapi-edit.sh <take_dir> <source_trimmed.mp4> <img1> [img2 ... img30]
#   <take_dir> must contain prompt.txt. Images go in the order the prompt names them (@Image1..).
#   Needs REAPI_API_KEY in the environment (source the project .env). Requires curl, jq, ffmpeg.
#   Set SOURCE_URL to reuse an already-hosted source clip instead of uploading it again.
#   RESOLUTION defaults to 1080p (use 720p for a cheap test).
set -euo pipefail

take=$1; src=$2; shift 2
: "${REAPI_API_KEY:?source the project .env first}"
[ -f "$take/prompt.txt" ] || { echo "missing $take/prompt.txt" >&2; exit 1; }
cd "$take"

# fal's CDN is unreachable from ByteDance's fetcher; litterbox (24h) is not.
host() { curl -sf -F reqtype=fileupload -F time=24h -F "fileToUpload=@$1" \
  https://litterbox.catbox.moe/resources/internals/api.php; }

for img in "$@"; do host "$img"; echo; done | grep . | jq -R . | jq -s . > image_urls.json
SOURCE_URL=${SOURCE_URL:-$(host "$src")}
echo "$SOURCE_URL" > source_url.txt

jq -n --rawfile prompt prompt.txt --arg source "$SOURCE_URL" \
  --slurpfile images image_urls.json --arg res "${RESOLUTION:-1080p}" '{
    model: "doubao-seedance-2.5-face", prompt: $prompt,
    image_urls: $images[0], video_urls: [$source],
    omni_reference_task_type: "edit", duration: -1, size: "adaptive",
    resolution: $res, bitrate_mode: "default", generate_audio: false,
    output_format: "mp4", watermark: false }' > request.json

# One POST only: a second POST is a second paid render.
curl --fail-with-body -sS https://reapi.ai/api/v1/videos/generations \
  -H "Authorization: Bearer $REAPI_API_KEY" -H 'Content-Type: application/json' \
  --data-binary @request.json -o submission.json || { cat submission.json >&2; exit 1; }
TASK_ID=$(jq -er .id submission.json)
echo "task $TASK_ID"

while true; do
  curl --fail-with-body -sS "https://reapi.ai/api/v1/tasks/$TASK_ID" \
    -H "Authorization: Bearer $REAPI_API_KEY" -o task.json
  case $(jq -er .status task.json) in
    completed) break ;;
    failed) jq .error task.json >&2; exit 1 ;;
    processing) sleep 10 ;;
    *) echo "unexpected status" >&2; exit 1 ;;
  esac
done

curl --fail -L -sS "$(jq -er '.output.video_urls[0]' task.json)" -o generated.mp4

# Original audio back on, 1440x1080 H.264 for X.
ffmpeg -v error -y -i generated.mp4 -i "$src" -map 0:v:0 -map 1:a:0 \
  -vf 'scale=1440:1080:flags=lanczos,setsar=1' -c:v libx264 -preset slow -crf 16 \
  -profile:v high -level:v 4.1 -pix_fmt yuv420p -maxrate 20M -bufsize 40M -g 48 \
  -c:a copy -movflags +faststart final_1080p.mp4
ffmpeg -v error -i final_1080p.mp4 -f null -

# QC sheet: source | output at the same timestamps.
mkdir -p qc
for t in 1 6 12 18 24 28; do
  ffmpeg -v error -y -ss "$t" -i "$src" -frames:v 1 -vf scale=-1:360 "qc/s$t.png"
  ffmpeg -v error -y -ss "$t" -i generated.mp4 -frames:v 1 -vf scale=-1:360 "qc/g$t.png"
  ffmpeg -v error -y -i "qc/s$t.png" -i "qc/g$t.png" -filter_complex hstack "qc/r$t.png"
done
ffmpeg -v error -y $(for t in 1 6 12 18 24 28; do printf -- '-i qc/r%s.png ' "$t"; done) \
  -filter_complex vstack=6 qc/compare.png
echo "done: $take/final_1080p.mp4 · QC $take/qc/compare.png"
