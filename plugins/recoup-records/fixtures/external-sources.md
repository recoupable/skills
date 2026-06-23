# External fixture sources

The golden fixtures in this directory are synthetic. They are shaped from public
schemas, official templates, and vendor documentation, but they do not copy
private royalty statements or confidential catalog data.

## Source map

| Fixture | Public basis | Source type | Notes |
| --- | --- | --- | --- |
| `golden/ascap-performance` | ASCAP royalty/payment and cue-sheet documentation | Official docs/templates | Tests performance royalty fields such as use type, credits, bonus type, licensee, and publisher share. |
| `golden/bmi-performance` | BMI radio royalty and public performance royalty documentation | Official docs | Tests BMI-style bonus category and publisher net normalization. |
| `golden/mlc-mechanical` | The MLC Royalty Detail and Work Summary statement layout examples | Official layout examples | Tests mechanical publishing income, DSP, usage period, and publisher net. |
| `golden/distributor-master` | Common distributor/DSP royalty export patterns | Industry-style synthetic | Tests master streaming gross, fee, net, platform, territory, and ISRC mapping. |
| `golden/youtube-content-id` | YouTube Reporting API system-managed financial report field docs | Official schema docs | Tests Content ID/UGC revenue, YouTube platform mapping, asset metadata, and net revenue. |
| `golden/curve-income` | Curve template and income import documentation | Vendor docs | Tests source-provided rights type, income type, source work ID, royalty source, and net payable fields. |

### PDF golden fixtures (`extract-pdf-statement.py`)

Each `golden/<society>-pdf/` directory holds a committed text-based `*.pdf`
statement and the `expected-royalty-ledger.csv` it must extract to. They are
synthetic, shaped from each society's public statement layout, and exercise the
per-society templates (column indices, currency, and period source). Regenerate
the PDFs with `golden/generate-pdf-fixtures.py` (needs reportlab); the test reads
the committed PDFs with pdfplumber only.

| Fixture | Society | Period source | Currency |
| --- | --- | --- | --- |
| `golden/ascap-pdf` | ASCAP (US) | filename quarter | USD (net + gross + share) |
| `golden/hfa-pdf` | HFA (US) | in-row year | USD (mechanical) |
| `golden/soundexchange-pdf` | SoundExchange (US) | filename year | USD (ISRC, neighboring) |
| `golden/prs-pdf` | PRS (GB) | filename year | GBP |
| `golden/sacem-pdf` | SACEM (FR) | filename quarter | EUR |
| `golden/sadaic-pdf` | SADAIC (AR) | filename year | ARS |
| `golden/jasrac-pdf` | JASRAC (JP) | filename year | JPY |
| `golden/apra-pdf` | APRA (AU) | filename year | AUD |
| `golden/socan-pdf` | SOCAN (CA) | filename year | CAD |

## Useful public sources

- ASCAP royalties and cue sheets:
  `https://www.ascap.com/help/royalties-and-payment`
- BMI U.S. radio royalties:
  `https://www.bmi.com/creators/royalty/us_radio_royalties`
- The MLC statement layouts:
  `https://help.themlc.com/en/support/what-do-the-different-statement-layouts-mean`
- The MLC data programs:
  `https://www.themlc.com/data-programs-all`
- YouTube system-managed report fields:
  `https://developers.google.com/youtube/reporting/v1/reports/system_managed/fields`
- YouTube financial reports:
  `https://developers.google.com/youtube/reporting/v1/reports/system_managed/ads`
- DDEX sample resources:
  `https://kb.ddex.net/reference-material/standards-specifications/`
- DDEX RDR-R samples:
  `https://kb.ddex.net/implementing-each-standard/recording-data-and-rights-standards-(rdr)/recording-data-and-rights-revenue-reporting-(rdr-r)/rdr-r-samples`
- CWR examples:
  `https://matijakolaric.com/articles/formats/cwr/minimal-cwr`
- Curve template docs:
  `https://help.curveroyaltysystems.com/article/118-how-to-create-a-template`

## Fixture policy

Use public schemas to create small synthetic rows. Add real customer/export
fixtures only when:

1. The owner permits use in tests.
2. Personal, payment, and confidential data is removed.
3. The fixture is small enough to review.
4. The expected normalized output is committed beside the input.
