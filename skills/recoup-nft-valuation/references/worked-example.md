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

## Status of this example — measured, then corrected 2.8× by the artist

The measurement has since been run against a confirmed wallet, and **the first result was
wrong.** The sequence is the whole lesson:

1. We measured her Zora V1 catalog by indexing ERC-20 `Transfer` logs and reported
   **$83,438** across 27 works.
2. That landed **well below her stated ~$200K** — which the reconciliation guidance above
   says to *investigate before publishing*. We logged the gap as "open", then built a
   marketing piece on the number anyway. **Recording a gap is not investigating it.**
3. We sent her the figure with three per-piece numbers. She replied that the largest was
   **$50k, not our $15,544**, and that she had also sold on other platforms.
4. Re-auditing from chain proved her right. Every **reserve-auction** sale had paid her a
   second leg as **native ETH**, which emits no log — so we had been reading the creator
   share only, typically 30% of each sale. **12 direct bid/ask sales were correct; all 15
   auction sales were understated.**
5. Corrected total: **$234,735** — 2.8× the first figure, and still a floor, since it
   covers one protocol on one chain.

Mechanism, arithmetic and the reconciliation gate that would have caught it:
`references/zora-contracts.md` → *The two-leg payment*, and `SKILL.md` Step 2.

Addresses, transaction hashes and the artist's identity are deliberately **not recorded
here.** This repository is public, these are a real person's earnings, and the figures are
still under discussion with her. The auditable per-transaction ledger lives with the
account team.

## The transferable lessons

- **Ask the artist how they earned before choosing a valuation method.** The question
  "did you sell NFTs?" belongs in onboarding, not in a post-mortem.
- **A valuation an artist knows is wrong costs more than no valuation.** They will not
  tell you it is wrong; they will simply stop trusting the tool.
- **Public claims are reconciliation targets**, not substitutes for measurement.
- **An unresolved gap is a blocker, not a disclosure.** Labelling a figure "a floor" does
  not license publishing it. If the artist's own account and our measurement disagree by a
  multiple, the measurement is the thing on trial.
- **The artist is a verification source, not an obstacle.** She caught a systematic
  indexing bug that our own review, lint and frame-QC did not. Send the numbers to the
  artist *before* they reach an audience — and treat "that's wrong" as a bug report.
- **Two independent methods, or it is not measured.** A total that has only ever been
  computed one way carries that method's blind spots with full confidence.
