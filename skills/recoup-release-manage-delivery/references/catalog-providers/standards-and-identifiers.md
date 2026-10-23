# Exchange standards and identifier readiness

Checked 2026-10-22. A valid file, eligible sender, successful transport, receiver
syntax acknowledgment and accepted rights record are independent conditions.

## CWR

CISAC's CWR supports work-registration data and status communication between
publishers and societies. Select the receiver's actual version/profile, sender
eligibility and transport, then validate against those specifications and parse
item acknowledgments. This profile does not ship a CWR serializer, schema validator
or sender integration. [CISAC formats](https://www.cisac.org/formats).

## DDEX

Select the actual exchange purpose. RDR notification communicates recording,
contributor and rights data; RDR revenue and choreography address different parts
of exchange. Pin receiver/version/profile and implementation/transport requirements
before preparing a standards-valid package. [RDR](https://ddex.net/standards/recording-data-and-rights/).

ERN carries release/resource metadata and availability terms from record companies
or distributors to DSPs. Pin the receiver's version/profile and onboarding; a locally
prepared message does not prove delivery or acceptance. No ERN serializer/transport
is implemented here. [ERN purpose](https://kb.ddex.net/implementing-each-standard/electronic-release-notification-message-suite-%28ern%29/).

The published Catalogue Transfer standard addresses a relinquishing record company,
acquiring record company and DSP, and expressly excludes transfers involving
distributors in its current scope. Do not use the name to infer universal distributor
migration support. Subsequent delivery metadata has its own receiver/process; this
profile implements no ERN/CT transport. [CT scope](https://ddex.net/standards/catalogue-transfers/).

## ISRC and other identifiers

Inspect existing assignment and actual recording identity before requesting an
ISRC. Use the appropriate eligible registrant/agency route. The same recording
keeps its assigned ISRC through ownership changes; do not reuse an identifier for
a different recording or invent an issuer prefix. Record actual requested/assigned
evidence. [IFPI guidance](https://isrc.ifpi.org/faqs).

ISWC, IPI, ISNI and UPC/EAN readiness entries preserve typed identity and missing
evidence, but this pass did not verify their issuing schemas/transports. Research
the actual eligible issuer and rules for the requested operation before validating
or filing. An administration or distributor change alone is not a universal reason
to issue a new identifier. Pending identifiers remain pending where the actual
recipient permits them; never manufacture a syntactically plausible value.
