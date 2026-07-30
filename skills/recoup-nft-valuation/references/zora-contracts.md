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
| Zora Auction House (reserve auctions) | — | UNVERIFIED — look up before use. Many 2021 sales settled here rather than through Market. |
| ZoraNFTCreator (ERC721Drop factory) | — | UNVERIFIED — resolve per chain; drops are clones, so enumerate via the factory's creation event. |
| ZoraCreator1155Factory | — | UNVERIFIED — resolve per chain. |

Drops and 1155 collections are **clones**: each has its own address. Enumerate them from
the factory's creation events for the artist's address, rather than hunting collection by
collection.

## Fee constants

- **ERC721Drop:** 5% of the primary sale amount reserved by the Zora DAO. Gross-vs-net
  matters — say which you are reporting.
- **Protocol Rewards mint fee:** 0.000777 ETH per mint, split across creator and
  developer roles (creator, create-referral, mint-referral, first-minter, Zora).
  On free mints this fee split *is* the creator's entire revenue for that mint.

## What to pull per surface

1. **Primary sales, V1** — settlements on Market/Auction House where the artist is the
   creator/token owner. Capture the **settlement token**, not just an ETH amount.
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
