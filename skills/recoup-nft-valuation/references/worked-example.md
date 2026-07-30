# Worked example — the case this skill was written from

## The correction

We valued a consented roster artist's catalog from Spotify data alone and reported a
band with a central estimate around **$15.6K**, computed from **3.85M measured lifetime
plays** across 62 tracks.

Her feedback: the valuation was wrong, because the **bulk of her career income came from
NFT sales, not streaming** — and we had counted none of it.

She was right, and the error is systematic rather than a one-off. Any artist who sold
music NFTs will read a streaming-only valuation as a claim that their career is worth a
fraction of what they actually earned. For an OG onchain artist the gap can be an order
of magnitude.

## What the public record says

She has stated publicly that she sold **upwards of $200,000** of NFTs on Zora, including
**$100,000+ in 2021 alone**, beginning with a February 2021 mint of a 2017 song bought by
a Zora co-founder for **$1,000 in DAI**.

Two things follow:

1. **Her figure is an estimate, not a measurement.** It is the artist's own recollection.
   Cite it as her claim; our job is to produce the audited number next to it.
2. **The first sale settled in DAI.** An ETH-only indexer would have missed the sale that
   started her onchain career. This is why `SKILL.md` Step 2 insists on ERC-20 coverage.

## The benchmark this gives you

A public claim is a gift: it is a reconciliation target. Once the measured number exists:

- **lands near her figure** → strong, publishable story — an artist's own estimate,
  confirmed onchain;
- **lands well below** → investigate before publishing. Likely causes: wallets or
  0xSplits contracts not yet supplied, platforms beyond Zora, or a chain not indexed;
- **lands well above** → also investigate. Likely causes: double-counted rewards
  (deposits *and* withdrawals), gross-vs-net confusion, or resale volume misattributed as
  creator revenue.

Never publish a number that contradicts the artist's own account without resolving the
gap with them first.

## Status of this example

The measurement has **not been run**. It is blocked on the artist confirming her wallet
and split addresses — the hard gate in `SKILL.md`. Candidate addresses were identified
from public ENS records but are deliberately **not recorded here**: they are unverified,
this repository is public, and an unconfirmed address must not become a number.

## The transferable lessons

- **Ask the artist how they earned before choosing a valuation method.** The question
  "did you sell NFTs?" belongs in onboarding, not in a post-mortem.
- **A valuation an artist knows is wrong costs more than no valuation.** They will not
  tell you it is wrong; they will simply stop trusting the tool.
- **Public claims are reconciliation targets**, not substitutes for measurement.
