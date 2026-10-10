---
name: recoup-catalog-import-catalog
description: "Turn a supplied distributor or repertoire CSV/spreadsheet into an organized, traceable catalog of releases, recordings and available composition links, with duplicates and uncertain matches flagged. Use for \"import my catalog\", \"load this distributor spreadsheet\", or \"organize this repertoire export\". Saves through a supported importer when available; does not establish ownership, distribute recordings or value a deal."
---

# Import my catalog

Read `references/music-business-records.md` before starting; it defines supported
file-review and hosted-save routes, source handling and completion checks.

## Result

Give the user a usable catalog and a separate list of rows needing a decision,
without dropping troublesome rows or turning an import into a rights claim.

## Workflow

1. Read the authorized CSV/spreadsheet and its worksheets, encoding, delimiter, header
   and row counts with available file tools. Preserve identifiers as strings, including
   leading zeros. Inspect the actual format; name unsupported or unreadable inputs.
2. Propose column mappings for title/version, artist, ISRC, release title, UPC,
   release date/precision, disc/track position and any supplied composition/writer
   fields. Resolve ambiguous mappings with the user before treating them as facts;
   never interpret distributor revenue shares as songwriter or ownership shares.
3. Separate recordings from release membership and compositions. Repeated ISRCs
   across releases may mean one recording in several products, while conflicting
   metadata under one ISRC requires review. Keep rows lacking IDs as unresolved
   candidates; do not invent identifiers or merge solely by title/artist name.
4. Build an organized catalog plus a review queue. Every row retains file/sheet/row
   and original values; retain excluded/invalid rows and reasons. Reconcile total
   input rows against imported, unchanged, proposed and rejected/held rows without
   counting multi-release membership as new recordings.
5. Compare with existing authorized catalog records if available. Reusing the same
   file/version should not create duplicates; changed versions produce a change list
   and preserve history rather than overwrite accepted identity or rights decisions.
6. Discover an importer that supports this format and workspace before writing.
   Inspect existing catalogs and exact schemas. The basic `insert_catalog_songs`
   operation can associate valid ISRCs with an existing catalog; it is not a general
   spreadsheet importer and cannot save unresolved rows or full composition records.
   Never use it as proof of complete import. Without suitable hosted support, return
   a labeled private catalog worksheet/export and review queue instead.
7. Read back supported hosted writes and reconcile counts. Retain the import/version
   or operation receipt where returned, and identify exactly what was not saved.

## Handoff

Provide catalog location, source/version, row reconciliation, unique recording and
release counts where resolvable, held rows and the specific decisions needed next.
Do not enroll credited people into a roster, infer rights, perform valuation, upload
media or silently skip bad rows. Use the host's available deterministic file tooling;
paid OCR or model extraction is a separate authorized step.

Example: 20 rows with one ISRC appearing on two releases preserve both memberships;
that repeat is not automatically two recordings or a row to delete.
