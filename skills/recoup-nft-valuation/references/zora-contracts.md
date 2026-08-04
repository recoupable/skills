# Zora contracts, eras, and what to index

Zora is three different protocols wearing one name. An artist active since 2021 has
earnings spread across all three, and each pays out differently. Indexing only the
current one is the most common way to under-count an OG artist.

**Verification discipline:** every address below is marked with how it was verified.
Re-verify anything marked `UNVERIFIED` on a block explorer before you index against it —
a wrong contract address produces a confident, wrong number.

## The era map

| Era | Protocol | How the artist got paid |
|---|---|---|
| 2020–2021 | **Zora V1** — shared Media/Market contracts | Bids/asks and auctions, settled in **any ERC-20** (DAI and WETH were common). `bidShares` paid the creator a cut of every resale automatically. |
| 2022– | **ERC721Drop** (from ZoraNFTCreator) | Editions with a mint price; proceeds to the drop's `fundsRecipient`, less a **5% primary-sale fee reserved by the Zora DAO**. |
| 2023– | **ERC1155 + Protocol Rewards** | Free and paid mints; the per-mint protocol fee is split across creator and developer roles and escrowed. |

## Addresses (Ethereum mainnet)

| Contract | Address | Verification |
|---|---|---|
| Zora V1 Media (shared ERC-721, "Zora / ZORA") | `0xabEFBc9fD2F806065b4f3C237d4b59D9A97Bcac7` | VERIFIED — Etherscan token page, 2026-07-30 |
| Zora V1 Market | `0xE5BFAB544ecA83849c53464F85B7164375Bdaac1` | VERIFIED — Etherscan address page, 2026-07-30 |
| ProtocolRewards (escrow singleton, v1.1) | `0x7777777F279eba3d3Ad8F4E708545291A6fDBA8B` | VERIFIED — ourzora/protocol-rewards + Zora docs, 2026-07-30. Deterministically deployed at the **same address on every network**. |
| Zora Auction House (reserve auctions) | `0xE468cE99444174Bd3bBBEd09209577d25D1Ad673` | VERIFIED — decoded `AuctionEnded` on 15 settlements from a real artist's catalog, 2026-08-04. Many 2021 sales settled here rather than through Market. **Pays the owner share as native ETH — see below.** |
| ZoraNFTCreator (ERC721Drop factory) | — | UNVERIFIED — resolve per chain; drops are clones, so enumerate via the factory's creation event. |
| ZoraCreator1155Factory | — | UNVERIFIED — resolve per chain. |

Drops and 1155 collections are **clones**: each has its own address. Enumerate them from
the factory's creation events for the artist's address, rather than hunting collection by
collection.

## The two-leg payment — how a V1 sale actually pays the artist

**This is the single most expensive thing to get wrong on V1.** It understated a real
artist's catalog by **2.8×** before it was caught — by the artist, not by us.

Zora V1 does not pay a sale to one recipient. `bidShares` splits every settlement three
ways — `prevOwner`, `creator`, `owner` — summing to 100%. On a **first sale of the
artist's own work, the artist is both creator and owner**, so **two separate payments are
theirs** and a scan that finds one has found a fraction.

How each leg moves depends on the venue, and that is what makes it dangerous:

| Venue | Creator leg | Owner leg | Visible in `eth_getLogs`? |
|---|---|---|---|
| **Direct bid/ask** (Market) | ERC-20 to artist | ERC-20 to artist | ✅ both legs |
| **Reserve auction** (Auction House) | ERC-20 to artist | **unwrapped WETH → native ETH** to artist | ❌ **owner leg invisible** |

The Auction House calls `withdraw()` on WETH and forwards native ETH with a plain value
call. Native transfers emit **no event**, so a log-only indexer records only the creator
leg — typically **20–30% of the sale** — and reports it as the whole thing, without error.

### Worked arithmetic (real settlement, artist anonymized)

```
13.420690 WETH   winning bid            AuctionHouse -> Market
 4.026207 WETH   creator share (30%)    Market -> artist        <- the only leg a log scan sees
 9.394483 ETH    owner  share (70%)     AuctionHouse -> artist   (native, no log)
──────────────
13.420690        total actually received by the artist
```

Independently confirmed by balance delta: the artist's ETH balance moved **+9.355567**
across that block — the 9.394483 owner share less 0.038916 gas, since they sent the
settlement transaction themselves.

**Reading only the logged leg reported $15,544. The sale was $51,813.**

### Rules that follow

- **Read the creator share per token.** It is set at mint and varies — 20%, 25% and 30%
  all appeared within one artist's 27 works. Never assume a constant and never
  back-compute the total by dividing by an assumed share.
- **`AuctionEnded` is the receipt.** It carries the final `amount`, plus `tokenOwner`,
  `curator` and `curatorFee`. Confirm `tokenOwner` is the artist — if it is not, the owner
  leg went to a reseller and is **not** the artist's revenue. A non-zero `curatorFee` is a
  third party's cut and must come out.
- **Check that legs sum to the bid.** Any residual is a leg you have not found yet.
- **This pattern is not unique to Zora.** Any marketplace that unwraps WETH before paying
  a seller has the same blind spot. Treat "settled in native ETH" as the default
  assumption to disprove, not an exception to discover.

## Fee constants

- **ERC721Drop:** 5% of the primary sale amount reserved by the Zora DAO. Gross-vs-net
  matters — say which you are reporting.
- **Protocol Rewards mint fee:** 0.000777 ETH per mint, split across creator and
  developer roles (creator, create-referral, mint-referral, first-minter, Zora).
  On free mints this fee split *is* the creator's entire revenue for that mint.

## What to pull per surface

1. **Primary sales, V1** — settlements on Market/Auction House where the artist is the
   creator/token owner. Capture the **settlement token**, not just an ETH amount — **and
   both `bidShares` legs.** On an auction the owner leg arrives as **native ETH with no
   log**; see *The two-leg payment* above. Reconcile each sale by balance delta or
   `AuctionEnded` before recording it.
2. **Primary sales, Drops/1155** — value transferred to `fundsRecipient` (which may be a
   0xSplits contract, not a wallet).
3. **Protocol rewards** — reward **deposits** crediting the artist's address in the
   escrow singleton. Deposits are earnings; `withdraw` calls are cash movement. Counting
   both double-counts.
4. **Secondary royalties** — V1 `bidShares` creator cut on resales, plus EIP-2981 payouts
   routed by marketplaces on later contracts. Note that royalty *enforcement* collapsed
   across marketplaces from ~2023, so this stream commonly decays for reasons unrelated
   to the artist's demand.

## Chains

Zora activity spans **Ethereum mainnet, Zora Network, Base, and Optimism**. The rewards
escrow is at the same address on all of them. Ask the artist which chains they used, and
state in the report which ones were indexed.

## Tooling

- **Dune (preferred).** Publish the query so the number is independently re-runnable.
  Dune added `erc721_multichain` / `erc1155_multichain` views covering standard events
  across ~65 EVM chains (June 2026), plus decoded Zora tables and NFT-trade spells.
  Confirm current table names in Dune's data catalog before writing the query — table
  names drift.
- **Direct RPC / explorer APIs** — `eth_getLogs` for the specific events, or an asset-
  transfer API for inbound value filtered by counterparty. Fine for a one-off, but the
  result is only as auditable as the script you hand over.
- **Marketplace APIs** — useful for secondary sale history per collection; treat as
  corroboration, not as the source of truth for money received.

## Sources

- Zora ERC721Drop docs — https://docs.zora.co/contracts/ERC721Drop
- Protocol Rewards — https://github.com/ourzora/protocol-rewards
- Dune decoded tables — https://docs.dune.com/data-catalog/evm/zora/decoded/overview
