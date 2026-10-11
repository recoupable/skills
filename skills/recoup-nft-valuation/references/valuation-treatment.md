# Valuation treatment — what carries a multiple and what does not

The streaming model prices a **recurring royalty stream**: per-stream rate → net share →
annualised → multiple. It works because streaming income is predictable, decaying slowly,
and largely independent of asset-market cycles.

NFT income breaks all three assumptions. This page is how to include it honestly.

## The three lines

### 1. Primary sales — realized, non-recurring, cycle-dependent

An artist sold ten works in 2021 for $150K. That money arrived once. It is not an
annualised stream, and there is no basis for assuming it recurs — the market that
produced it was a cycle that has not repeated at the same amplitude.

**Treatment:** report as *realized onchain earnings, historical*, with the years they
landed in. **Do not apply the streaming multiple.** A 13× on $150K of one-time sales
invents $1.95M of value that does not exist.

Where it legitimately affects value: it evidences **demonstrated willingness to pay** —
handled in line 3.

### 2. Secondary royalties — annuity-like, low multiple

A cut of every resale, paid automatically. This *is* recurring, so it can carry a
multiple — but a much lower one than streaming, for two reasons:

- **Decay.** Resale volume for a given collection typically falls sharply after the
  initial cycle.
- **Enforcement risk.** Royalties on most marketplaces became optional from ~2023.
  A stream that depends on voluntary payment is not worth a streaming-grade multiple.

**Treatment:** annualise the trailing period, then apply a **conservative multiple well
below the streaming band**, and state the multiple and why. If the trailing 12 months are
near zero, say so and carry it at ~zero rather than reviving an old average.

### 3. Collector base — a risk adjustment, not a dollar figure

This is the line most likely to be undervalued, and it must never be expressed as cash.

Two artists with identical stream counts are not equivalent if one has 40 people who each
paid four figures for their work and the other has none. The first has demonstrated
direct-to-fan monetisation at high price points; the second has only platform-mediated,
sub-cent-per-play income.

**Treatment:** express as a **risk/band adjustment and a qualitative finding**, not a
dollar line. Useful measures:

- distinct collectors, and how many bought more than once;
- median and top settlement price (willingness to pay at the high end);
- recency — is anyone still buying, or did it stop in 2022?;
- concentration — one whale is a different risk profile than forty collectors.

A live, repeat-buying collector base is a reason to sit at the **top of the streaming
valuation band** rather than the middle. It is not a reason to add a number.

## The output contract

Never collapse these into a single headline figure. The honest presentation is:

```
STREAMING CATALOG (estimated)   $X – $Y, central $Z
REALIZED ONCHAIN EARNINGS       $N  (historical, non-recurring — no multiple applied)
SECONDARY ROYALTY VALUE         $R  (trailing 12mo annualised × conservative multiple)
COLLECTOR BASE                  K collectors · J repeat · top settlement $T
```

If someone insists on one number, the defensible construction is
`streaming valuation + secondary royalty value`, with realized primary sales reported
alongside as historical earnings and the collector base cited as the reason for where in
the band it sits. Say exactly that when you present it.

## Why this matters commercially

A streaming-only valuation of a web3-native artist is not merely incomplete — it is
**wrong in a way the artist can immediately detect**, because they know what they earned.
Being visibly wrong about an artist's own income destroys more trust than declining to
value them at all.
