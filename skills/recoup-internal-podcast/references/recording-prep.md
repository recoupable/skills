# Recording prep: the day before and the hour of

The edit can only use what the recording captured. Most of the time lost in post-production on the first
six episodes (2026-10-01 to 10-14) traced back to the recording: a host camera at 17-24 fps beside a guest at
30, words lost while the host was muted, and a render running on the recording machine. Booking and the guest
brief are the sales guest pipeline; this file is the studio.

## The day before (studio test)

1. **Calendar invite:** the Restream studio link is the location, the scheduler's own video link and
   reschedule text are removed. Never name another video tool in guest emails or replies.
2. **Host camera test:** a 2-minute solo Restream recording on the exact setup planned for tomorrow. Measure
   its frame rate from packet timestamps, not the container header:
   `ffprobe -v error -select_streams v:0 -show_entries packet=pts_time -of csv=p=0 <test.mkv>` and count
   frames per second across the file. About 30 fps passes. Every guest so far recorded at 30 fps through the same
   studio, so a low host rate is the host machine (CPU load, thermal throttling, a 720p built-in camera in dim
   light), not Restream.
3. **If the test is under ~28 fps:** try a phone as the camera (macOS Continuity Camera) on a stand at eye
   level, then repeat the test. Still low on the phone means the CPU is the limit; record anyway and plan the
   edit around it (guest-focus layout, cards over host questions; `references/podcast-episode.md`).

## The hour of

- **Nothing heavy on the recording machine.** No renders, `fix_host_video.py`, enhancer uploads or large
  downloads; CPU load is the likely cause of Restream dropping the host camera. Check for running jobs and
  stop or pause them before the guest joins. A render queue started earlier should use `STOP_AT`.
- Machine plugged in and raised for airflow, one browser tab for the studio plus the note taker, no screen share
  during the take, the host facing the light.
- **Unmute before speaking.** The host track is gated to digital silence while the host is quiet, so a line
  said while muted is gone from every file. If it happens, the host repeats the line on tape so the edit has it.

## Right after

- Download the per-speaker audio zip and both camera files (`references/podcast-episode.md` step 1).
- Same-day CRM close-out and recorder notes are the sales guest pipeline (*Right after the recording*).
- Before cutting, scan the host track for mid-speech dropouts (`silencedetect=n=-85dB` against the host
  transcript words): Restream lost about 7 s of the host mid-sentence once, in both audio and video, and the
  transcriber skipped the words silently.
