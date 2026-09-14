# Podcast guest pipeline

The podcast is the top of the Agency Leads funnel, not a media project. A cold lead is
invited onto a 30 to 60 minute episode about their history in music and how they use AI;
the conversation tells us what to build for them. Started 2026-09-14. The operator's
working folder is `workspace/sales/podcast/` (pipeline README, invite templates, guest
folders, episode copy, cover generator); this file carries only what a cold reader needs
to run it the same way.

## The loop and the Attio mapping

1. 10 invites a day to qualified leads. Invite sent = **New**.
2. Replied, no date = **In Conversation** (flag after 3 days, same rule as any agency lead).
3. Recording booked = **Call Booked**. Record; publish to YouTube, Spotify, Apple and socials
   within 48 h; add the episode to the site's `episodes.json` in the same PR.
4. Day 7 after recording: send three concrete builds drawn from the call notes, one
   sentence each, no price. Sent = **Scoping**.
5. Reply → proposal, $1k to $5k for a 2 to 4 week build, deposit + delivery split, in the
   order `discovery-and-proposals.md` sets. Sent = **Proposal Sent**. Deposit paid = **Won**.
6. Every completed build ends with a testimonial and a post-mortem. After three paid,
   completed, reviewed builds, review the rate.

`lead_source = Podcast`, `project_type = Build`. No new stages, no new list. Invite links
carry `?utm_source=email&utm_medium=invite&utm_campaign=<yyyy-mm>`.

## Episode copy that supports a premium price

Guests and prospects read the episode page before they read anything else we send. Every
title and description is sales copy for a firm that charges six figures for a build:

- **Title shape:** `<the specific claim> w/ <Guest Name>`. Panels end in `(panel)`.
- **Description:** one specific claim in the first sentence, hard nouns over adjectives,
  no hype words, no emoji, no em dashes, guest links kept, then one fixed closing line:
  *"Recoup designs and builds the systems behind conversations like this one: catalog data,
  royalty operations, and AI agents for labels, publishers, funds and management companies.
  recoupable.dev"*
- **Back catalog:** a Web3-era episode is reframed to the business lesson in the title and
  first sentence, not rewritten into something it was not. Six were retitled 2026-09-14;
  the copy is in `workspace/sales/podcast/episodes/retitle-2026-09-14.md`.

## Cover spec (measured from the reference show's thumbnails, 2026-09-14)

The reference thumbnails are 2000×1125 (some 4000×2250). Fractions are of the short side
(H) unless marked W, so the same numbers drive the square Spotify art.

| Element | Spec |
|---|---|
| Canvas | 16:9 for YouTube and site cards; 1:1 for Spotify episode art (min 1400², we ship 2000²) |
| Margin | 10% H on every side (112 px at 1125). Logo, title and guest line all start on the left margin |
| Logo | Show lockup, height 12.5% H (140 px), top-left corner on the margin |
| Title | Left column, max width 47.5% W; font 8.9% H (100 px), medium weight, line pitch 1.27×; 2 to 3 lines; the block sits in the lower half, ending ~28% H above the bottom |
| Guest line | Under the title: name at 4.1% H semibold, org/role at 3.7% H regular, bottom of block 18% H above the bottom edge |
| PFP placement | Right side, from 40% W to the right edge, face centred at ~71% W; head top on the top margin (10% H); shoulders bleed off the bottom edge |
| PFP style | Background-removed cutout of a real photo, full colour, no circle, no frame, no tint, no drop shadow; the sweep shows around the silhouette |
| Colour | Reference uses dark ink on a flat accent; ours is white type on the Recoup Podcast blue sweep (`assets/recoup-podcast-blue-sweep-background.png`, lockup `recoup-podcast-white-transparent.png`) |

Square derivation: same margins and logo; title column 47% W and the title auto-steps
down (8.9 → 5.2% H) until the block clears the lockup row; the cutout is 62% H tall,
centred at 74% W, anchored to the bottom edge. `workspace/sales/podcast/scripts/make-covers.py`
implements both.

## Guest photo sourcing

Use the guest's own published artist image, never a fan photo or a screenshot.

- **Spotify artist image (best, no auth):** `https://open.spotify.com/oembed?url=https://open.spotify.com/artist/<id>`
  returns `thumbnail_url` at 320 px. Swap the image-id prefix `ab67616100005174` for
  `ab6761610000e5eb` to get the 640 px original from the same CDN.
- **Cutout:** `rembg` (bria-rmbg model, ~1 GB first download). It does not install on
  Python 3.13 (numba/llvmlite); use a 3.12 venv, `pip install --no-deps rembg` plus
  `onnxruntime numpy pillow opencv-python-headless scipy pooch jsonschema tqdm scikit-image`,
  and stub the three `pymatting` imports in `rembg/bg.py` (only alpha-matting needs them).
  Check the mask on a flat colour before using it.
- Store `guests/<slug>/headshot-source-<origin>.jpg` and `headshot-cutout.png` in the
  workspace; the cover script picks the cutout up by slug.

## Editing episodes on Spotify for Creators

The dashboard is the only write path (the RSS is read-only and cached for up to an hour, so
verify in the dashboard, not the feed). Learned on the 2026-09-14 run:

- **Login needs the human.** Automated logins hit "We need to make sure that you're a human";
  open a headed `agent-browser` window, let the operator log in and solve it, then drive.
  **Save the auth state immediately** (`agent-browser state save <file>`): a browser relaunch
  drops the session and every edit after that silently lands on the login page.
- Two shows can share one account. Pick the show by its id in the URL
  (`/pod/show/<showId>/episodes`), not by name; an empty duplicate "Recoup Podcast" show
  exists on the same login.
- Episode details page: tick the **HTML** switch (click the checkbox via the DOM, the
  label click does not register), then `fill` the title input and the HTML textarea.
  Paragraphs as `<p>`, links as `<a href>`; the editor strips nothing else we used.
- **Cover upload:** the page has two image `input[type=file]`; the first (`#show-art-upload`)
  is the SHOW cover, the second is the episode cover. Uploading to the first overwrites the
  show art. Give the second an id, upload to it, then click the crop dialog's own Save (the
  last `Save` button in the snapshot), wait ~10 s, then the page-level Save.
- Search on the episodes list is a plain substring; "w/ Kantor" with a trailing space in the
  stored title did not match, "Kantor" did.
