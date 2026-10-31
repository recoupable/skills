# Typed intake and row controls

The helper in `scripts/import_catalog.py` runs locally. It produces a review packet,
not an import receipt. Run it from this skill's directory and give absolute paths
for source/output files in the user's private workspace:

```bash
python3 scripts/import_catalog.py --source /private/work/repertoire.csv --mapping /private/work/map.json --out /private/work/intake.json
python3 scripts/import_catalog.py --source /private/work/repertoire.xlsx --sheet Works --mapping /private/work/map.json --previous /private/work/prior-intake.json --out /private/work/revision.json
```

Copy `templates/import-map.json`, remove unmapped entity/edge sections and map exact
column names. Values are column names. For provider IDs, map `provider_id`,
`provider_namespace` and `account_scope` to explicit source columns. A combined
namespace is not used to infer an account: missing or blank namespace/account scope
holds the observation as a row-scoped candidate, even if another identifier is present.
Supply an explicit reviewed mapping/source revision to resolve that hold. No guessed
column mapping, default share, title-only match or implicit rights authority is applied.
CSV input uses UTF-8 (optional BOM). XLSX needs openpyxl; multiple sheets require an
explicit selection, and each selected sheet is a separate source slice. Keep original
files immutable. Other delimiters/encodings need a separately recorded conversion;
retain the source and conversion evidence. Spreadsheet date cells expose their stored
value/format, but cannot prove precision already lost in the original application.

Entities have candidate identifiers and source observations; even matching identifiers
remain candidates pending review. A row without IDs is a usable unresolved record.
ISRC/ISWC and provider IDs are separate namespaces. Same title does not join two works.
Do not collapse aliases into people or contributors into artist accounts. A conflicting
observation holds all affected rows; retain all variants until a sourced decision.
Observations sharing entity kind, provider namespace, account scope and provider ID
are checked together even when different ISWCs produce separate candidate IDs.
Conflicting nonempty mapped entity values (including ISWC or writers) hold every row
in that scoped group with the conflicting field names. Missing values do not establish
a contradiction or fill another observation. Distinct provider/account scopes remain
separate; no title matching or cross-account identity inference is performed. Raw
observations, source locators and parented interest edges remain unchanged.

The helper deliberately holds numeric identifier cells whose original leading zeros
may already be lost. It does not invent zeros or interpret formula results.

Keep recording/work links many-to-many and proposed until evidence supports them.
Each release/edition has its own disc/track membership even when the recording is shared.
An interest observation retains kind, basis, scale, right, territory, dates, parent,
mandate and evidence. Missing semantics remain held. Collection, administered,
writer, owned, statement percentage and producer participation are different kinds.
Repeated child/parent observations are not independent owned interests or additive sums.
Unknown/negative/over-100 values need the applicable provider semantics and source review,
not clamping or balancing shares. The helper holds nonnumeric/nonfinite values,
nonpositive scales and values outside zero through the supplied scale. It preserves
raw values and does not assume every provider uses a 100-point scale. This range
check does not establish ownership or sum/convert shares. A supplied nonempty scale
is validated even when the interest value is blank; missing values or scales are
not filled in by this check.

Every post-header row, including blanks and malformed widths, receives a disposition.
Local output uses proposed/held/rejected; an exact rerun marks unchanged proposed rows.
Held rows remain held on reruns. `imported` is reserved for a supported hosted write
with readback and field-level results. File bytes + sheet + mapping fingerprint define
an import version; a revised file points to its prior import without rewriting it.
Same input replay is stable. No-identifier candidates stay scoped to source rows and
need explicit reviewed matching across revisions. Keep the prior packet in the case.

Before hosted save, map these records to the discovered exact API/MCP schema and list
unsupported fields. Save only authorized supported records; retain per-row operation
receipts and readback. An ISRC association endpoint cannot store every rights/party/edge
field. Report partial support and keep unresolved data privately; never claim the whole
catalog is hosted because the local row control balances.
