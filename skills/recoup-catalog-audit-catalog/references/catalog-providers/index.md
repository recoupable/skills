# Catalog provider operation profiles

Checked 2026-10-22. Read only the family needed for the current operation.
`references/catalog-providers/operations.json` is the machine-readable registry;
`references/catalog-providers/sources.json` records official URLs and check results.
These are preparation profiles and sourced procedures. They do not implement an
authenticated provider adapter or prove the current account can submit/read back.

| Family | Read | Important distinction |
|---|---|---|
| The MLC | `references/catalog-providers/mlc.md` | Public search, Member Hub claims and Songwriter Hub matching have different roles |
| ASCAP, BMI, SESAC, GMR | `references/catalog-providers/us-pros.md` | Work creation, updates, affiliations and share conventions remain provider-specific |
| SoundExchange, PPL, SENA | `references/catalog-providers/recording-societies.md` | Owner, performer and producer-payment roles are separate |
| PRS/MCPS, SOCAN/CMRRA, SACEM, GEMA, APRA AMCOS | `references/catalog-providers/international.md` | Rights, local share basis and existing mandates determine the route |
| Kobalt, Songtrust | `references/catalog-providers/administrators.md` | Admin intake, downstream acceptance and accounting are independent |
| U.S. Copyright Office | `references/catalog-providers/copyright.md` | Registration, supplementary registration and recordation are distinct |
| Distributor, Spotify, YouTube, TikTok, Meta | `references/catalog-providers/delivery-and-ugc.md` | Delivered correction, UGC enrollment and migration have separate evidence |
| CWR, DDEX and identifiers | `references/catalog-providers/standards-and-identifiers.md` | Standards/identifiers do not establish transport eligibility |

## Using a profile

1. Select exact provider + operation + subject + role + right + territory + period.
   Choose the applicable profile ID, not a provider-wide supported flag.
2. Compare its dated source coverage with current official/account instructions.
   `verified_route_only`, inaccessible or dynamic sources do not establish full
   field validation. Unresearched issuer/provider entries are evidence packets only.
3. Resolve `required_inputs` from authentic case evidence. Inspect current schema,
   account membership/partner capability, mandate, share convention and known prior
   attempts. Record missing prerequisites without inventing values.
4. Prepare the exact fields/assets/documents, before/after diff, disclosure, fees and
   requested action. An existing authorization applies only to matching actual scope.
5. Discover a usable, authorized transport in this environment. The registry does
   not supply endpoints or account credentials. Prefer verified connector/API routes;
   otherwise use eligible portal/import/support assistance or a prepared handoff.
6. Preserve receipt, raw provider state, item decisions and independent readback.
   Current case records hold private evidence; this public registry never does.

## Extending coverage

Add an exact operation and official evidence, not a list of provider logos. A new
adapter needs actual input/output schemas, receiver versions, authentication/role
checks, scope, errors, duplicate/timeout recovery and readback tests. Documented
procedure, fixture-tested preparation, authenticated execution and authorized live
readback are separate coverage levels. This registry's `not_implemented` and
`not_verified` fields must not be promoted merely because a reference was written.

`references/catalog-providers/conformance-cases.json` supplies synthetic decisions
to evaluate in addition to each stage's cases. A schema check or deterministic
preflight test does not substitute for a cold-agent walkthrough or live acceptance.
