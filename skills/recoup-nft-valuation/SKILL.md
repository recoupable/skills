---
name: recoup-nft-valuation
description: Measure an artist's onchain NFT earnings from public chain data and fold them into a catalog valuation without inflating it. Use for "what did this artist earn from NFTs", "value an NFT artist's catalog", "include NFT sales in the valuation", "measure Zora/Foundation/Sound sales", or any catalog valuation where the artist sold music NFTs. Streaming-only valuations understate web3-native artists — often by an order of magnitude.
---

# Recoup — NFT Valuation

Value an artist whose income came substantially from selling NFTs. A streaming-only
valuation reads their catalog as small because it measures the wrong revenue: for an
OG onchain artist, primary sales can dwarf a decade of streaming royalties.

This skill produces **two numbers side by side** — a streaming catalog estimate and a
measured onchain earnings figure — and deliberately refuses to merge them into one.
Merging them is the central mistake this skill exists to prevent.

> **Origin:** written after an artist told us our valuation of her catalog was wrong
> because it counted only Spotify and ignored the NFT sales that were the bulk of her
> career income. She was right. Worked example: `references/worked-example.md`.

## The hard gate — addresses come from the artist, never from a guess

**Do not derive a single published number from an address the artist has not confirmed.**
ENS names, handles that match, and addresses in press articles are *candidates*. A
wallet that looks like theirs is exactly the fabricated-number failure a real-numbers
brand cannot survive.

Ask the artist for:

1. Every wallet they minted or received sale proceeds on (there are usually several — a
   2021 hot wallet, a later one, a hardware wallet).
2. Any **0xSplits** or multisig contract they routed drops through. Proceeds land there,
   not in their wallet, and an address-only scan misses all of it.
3. Which platforms they sold on — Zora, Foundation, Catalog, Sound, Manifold, Async —
   each is a different contract set to index.
4. Which chains — Ethereum mainnet, Base, Zora Network, Optimism.

Confirm by checking that a claimed address actually appears as creator/recipient on a
work they publicly claim. If the artist is unreachable, stop and report the blocker.
An unverified measurement is worth less than no measurement.

## Step 1 — Enumerate the revenue surfaces

NFT income is not one number. Four surfaces, each measured differently and each
carrying a different valuation weight. Contract addresses, event shapes and the era map
are in `references/zora-contracts.md`.

| # | Surface | What it is | Valuation weight |
|---|---|---|---|
| 1 | **Primary sales** | The artist sold a work. One-time cash. | Realized, non-recurring |
| 2 | **Protocol rewards** | Creator's share of per-mint protocol fees | Realized, non-recurring |
| 3 | **Secondary royalties** | A cut of every resale, paid automatically | Annuity-like |
| 4 | **Collector base** | Who bought, how much, how often, still holding? | Risk signal, not cash |

Surface 4 is not revenue and must never be added to a dollar total. It is often the
most predictive output of the whole exercise — see Step 4.

## Step 2 — Index it

**Prefer a public Dune query over a private script.** Roughly equal work, and the number
becomes independently re-runnable by the artist, a skeptic, or a buyer. For a brand that
claims real numbers, a number anyone can re-run outranks a number we assert.

Index inbound value to the confirmed addresses and split contracts, filtered by
counterparty contract, across every platform and chain the artist named.

**Three traps that will silently corrupt the total:**

- **Native ETH is invisible to a log-only scan.** ⚠️ *The one that has actually bitten
  us — it understated a real artist by 2.8×.* ERC-20 transfers emit a `Transfer` event;
  **plain ETH transfers emit no log at all.** An indexer built on `eth_getLogs` sees
  every DAI and WETH leg of a sale and silently drops every native-ETH leg. It does not
  error, it does not warn — it just returns a smaller number.

  This is not an edge case on Zora V1. A sale is split into a **creator share** and an
  **owner share**, and on a first sale of their own work **the artist is both, so they
  receive both legs.** Auction settlements route the owner share through the Auction
  House, which **unwraps WETH to native ETH** before forwarding it — so the larger leg,
  typically 70–80% of the sale, is exactly the one a log scan cannot see. Mechanism and
  worked arithmetic: `references/zora-contracts.md` → *The two-leg payment*.
- **ERC-20 settlement.** Early NFT sales often settled in **DAI, WETH or USDC**, not
  ETH. An ETH-only indexer returns a confidently wrong number and misses the artist's
  earliest (often largest) sales. Note this is the *mirror* of the trap above: token-only
  and ETH-only scans each miss half of a V1 auction. **You need both.**
- **Rewards double-counting.** Protocol rewards are *deposited* to an escrow contract
  and later *withdrawn*. Deposits are the earnings; withdrawals are cash movement.
  Counting both doubles the figure.

### The reconciliation gate — a sale total is not final until it closes twice

**Never publish a per-sale figure assembled from token-transfer logs alone.** Close every
sale by a second, independent method that cannot share the first one's blind spot:

1. **Balance delta.** `eth_getBalance` on the artist's address at `block-1` and `block`.
   Add back gas (`gasUsed × effectiveGasPrice`) when the artist sent the transaction
   themselves. This catches native legs by construction.
2. **The settlement event.** Read the marketplace's own end-of-sale event — for a reserve
   auction, `AuctionEnded` carries the final `amount` plus `tokenOwner`, `curator` and
   `curatorFee`, which also tells you whether the proceeds were actually all theirs.
3. **Sum of legs vs. bid in.** The value entering the marketplace contract must equal the
   legs leaving it. **If your legs do not sum to the winning bid, you are missing a leg** —
   that residual is the fastest tell that something settled natively.

A row that fails to reconcile is a **blocker, not a footnote**. Chase it before it enters
a total.

**Verify the split, do not assume it.** Creator share is set per token at mint and varies
in practice (20%, 25% and 30% all appear in a single artist's catalog). Read it per sale.

Also reconcile against any public claim the artist has made about their own sales. A
measured number that lands near their stated figure is a strong story; one that lands
far from it is a finding to investigate before publishing, not to quietly ship.

## Step 3 — Price every settlement at its own block timestamp

A 2021 sale converted at today's token price is a fabricated number, in whichever
direction it flatters. For each settlement: block timestamp → token/USD at that
timestamp → USD-at-settlement.

Report **native amounts** (ETH/DAI/USDC) *and* **USD-at-settlement**. If a
"what it would be worth today" figure is wanted, it is a separate, explicitly labelled
conversion — never the headline.

## Step 4 — Fold it into the valuation without inflating it

The streaming model prices **recurring royalties**: per-stream rate → net → multiple.
NFT income does not have that shape. Applying the streaming multiple to it invents a
valuation.

- **Primary sales are realized, non-recurring, cycle-dependent cash.** Applying a 10–16×
  multiple to them would invent a valuation. They belong on a separate line: *realized
  onchain earnings, historical*.
- **Secondary royalties are annuity-like** and can carry a multiple — but a much lower
  one, given decay and the collapse of royalty enforcement across marketplaces.
- **The real signal is the collector base.** An artist with a demonstrated set of people
  who paid four figures for their work has a different risk profile than one with the
  same stream count and no buyers. That is arguably more predictive of future earnings
  than play count.

Full treatment, including how to band the secondary-royalty multiple and how to express
collector base as a risk adjustment rather than a dollar figure:
`references/valuation-treatment.md`.

## Step 5 — Report

Output shape:

```
STREAMING CATALOG (estimated)     $X – $Y, central $Z    ← measured streams, estimated $
REALIZED ONCHAIN EARNINGS         $N USD-at-settlement   ← measured, historical, non-recurring
  primary sales                   $A across M works
  protocol rewards                $B
  secondary royalties             $C  (annuity-like — the only line carrying a multiple)
COLLECTOR BASE                    K distinct collectors, top holder P works   ← risk signal
```

Always disclose, in the artifact itself:

- which figures are **measured** vs **estimated**;
- the **as-of date** and the **contracts indexed**, so it is auditable;
- what is **excluded** — offchain payouts, chains not indexed, platforms not covered,
  gas and marketplace fees, and whether figures are gross or net.

## Guardrails

- **Unconfirmed address = no publication.** No exceptions, including for a candidate
  that looks obviously right.
- **A total built only from token-transfer logs is unverified.** Native ETH emits no log.
  Reconcile every sale by balance delta or settlement event before it enters a figure.
- **Legs must sum to the bid.** An unexplained residual between what entered the
  marketplace and what you attributed is a missing leg, not a rounding error.
- **An artist disputing a number is evidence, not an objection.** They know what landed in
  their wallet. When their recollection and our measurement disagree, re-audit from chain
  before defending the figure — in the case this skill was corrected from, the artist was
  right and we were reading 30% of the sale.
- **Never merge onchain earnings into the streaming valuation as one number.**
- **Never apply a streaming multiple to primary sales.**
- **Price at settlement**, never at today's token price.
- **The artist's own estimate is not a measurement** — cite it as their claim, and label
  our number as the measured one.
- **Their story is theirs.** When the work is about a specific artist, the numbers are
  ours to verify and theirs to narrate. Coordinate before publishing.

## References

- `references/zora-contracts.md` — contract addresses, era map, event shapes, verification status
- `references/valuation-treatment.md` — the model: what carries a multiple and what does not
- `references/worked-example.md` — the case this skill was written from
