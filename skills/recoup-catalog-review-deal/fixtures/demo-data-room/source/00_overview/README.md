# Demo data room — synthetic catalog

This is the synthetic catalog bundled with the recoup-catalog-review-deal
skill to demonstrate end-to-end behavior. Every file in this folder
is fake — invented song titles, invented writers, invented PROs.

## What it represents

A small mixed-rights catalog (publishing + masters) with five
recordings, brought to market by a small artist-owned company called
**Lane Music Holdings LLC**. The flagship track is "Bright Lights"
(2018) — it carries about a third of the catalog's revenue, which
should trip the concentration threshold defined in `assumptions.yaml`.

The data room deliberately includes the kinds of issues that real
seller files contain so the plugin can surface them as findings:

- A PRO bonus quarter on the top track (ASCAP Q3 2024 audio-feature
  premium) that should be normalized out of run-rate NPS.
- An uncleared sample on "Slow Lightning" with no clearance document
  in the legal folder.
- A missing split sheet for "Long Way Home" — only writer names on
  the seller's track list.
- Top-1 catalog concentration around 35%, well over the 25% materiality
  threshold in `assumptions.yaml`.
- An incomplete recording-agreement file (signature page never
  attached) for the masters.

If you opened this README via recoup-catalog-review-deal demo mode, the plugin already
copied this folder into `deals/demo-catalog/source/`. From there it
ran recoup-catalog-review-deal review mode end-to-end and the agent authored
`deals/demo-catalog/DASHBOARD.html` via recoup-catalog-review-deal dashboard mode.
Open that file in a browser for the executive read.

## File index

```
01_track_list/track-list.csv
02_compositions/composition-list.csv
03_royalty_statements/ascap/ascap-statements-2024.csv
03_royalty_statements/distributor/distributor-2024.csv
03_royalty_statements/mlc/mlc-2024.csv
03_royalty_statements/soundexchange/soundexchange-2024.csv
03_royalty_statements/youtube/youtube-cid-2024.csv
04_rights_documents/agreements/recording-agreement-2018.txt
04_rights_documents/agreements/publishing-admin-agreement-2019.txt
04_rights_documents/split_sheets/bright-lights-split.txt
```

Notably **absent** (so the missing-files tracker has things to flag):

- Producer agreement for any recording.
- Sample clearance for "Slow Lightning".
- Split sheet for "Long Way Home" or "Dust on the Pages".
- Recoupment ledger from the 2018 recording agreement.
- UCC/lien search on Lane Music Holdings LLC.
