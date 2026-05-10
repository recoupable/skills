# Tooling landscape

This plugin should complement systems of record and data providers, not pretend
to replace them. The strongest position is a diligence and analysis layer that
turns exports, files, and APIs into source-cited deal workpapers.

## Royalty accounting systems

These systems manage contracts, statements, calculations, and reporting.

| Tool | What it solves | What remains manual |
| --- | --- | --- |
| Curve | Label and publisher royalty accounting, statement ingestion, contract terms, CWR, reporting. | Deal-specific diligence, cross-room evidence trails, valuation normalization, IC packaging. |
| RoyaltyShare | Royalty processing for labels, especially Orchard-connected workflows. | Independent buyer diligence across mixed external data rooms. |
| Vistex Counterpoint | Enterprise rights, contracts, repertoire, royalty accounting. | Lightweight deal-room analysis and AI-assisted exception synthesis. |
| Synchtank IRIS | Publisher royalty accounting, CMO imports, catalog analysis. | Buy-side underwriting, rights confidence scoring, memo generation. |

Plugin role: consume exports, validate structures, reconcile with other sources,
and create diligence workpapers. Do not mutate these systems without a separate
approved integration.

## Catalog and asset systems

These systems organize recordings, assets, rights, and pitching workflows.

| Tool | What it solves | What remains manual |
| --- | --- | --- |
| OpenPlay | Catalog metadata, rights, assets, delivery, API source of truth. | Acquisition diligence, valuation bridges, seller-file reconciliation. |
| DISCO | Asset management, pitching, tagging, rights lookup, sync workflows. | Financial diligence and cross-source royalty normalization. |
| DDEX/CWR files | Standardized delivery and publishing registration data. | Human-readable exceptions, confidence scoring, valuation impact. |

Plugin role: reconcile data-room metadata with canonical catalog exports and
flag mismatches that affect collection or transferability.

## Data and usage providers

These tools provide external context and verification signals.

| Tool | What it solves | What remains manual |
| --- | --- | --- |
| Luminate | Consumption, metadata enrichment, market measurement. | Mapping usage signals to seller royalty statements and valuation assumptions. |
| Chartmetric | Artist, playlist, social, radio, and platform analytics. | Royalty tie-outs, NPS/NLS, rights diligence. |
| Music Reports/Songdex | Licensing, ownership, DDEX, cue sheets, royalty reporting. | Deal-room synthesis and buyer-specific underwriting. |
| The MLC | U.S. blanket mechanical licensing, unmatched recordings, DQI, public/bulk data. | Linking MLC issues to catalog valuation and seller cleanup tasks. |
| BMAT, Soundmouse, Audoo | Usage detection, broadcast, cue sheets, public performance monitoring. | Translating detections into diligence exceptions and value impact. |

Plugin role: use provider data as corroborating evidence, not as payable royalty
proof by itself.

## Catalog finance and marketplaces

These companies show the capital workflows the plugin can accelerate.

| Company | Workflow signal |
| --- | --- |
| Royalty Exchange | Marketplace underwriting needs standardized royalty history and buyer-facing materials. |
| Duetti | Independent catalog acquisition needs fast master/publishing diligence and post-close operations. |
| beatBread | Financing workflows need collateral, revenue history, and deal comparison. |
| Lyric Financial | Advances and credit lines depend on royalty verification and risk controls. |
| Citrin Cooperman/Massarsky | Specialist valuation work depends on rigorous income composition, decay, and rights analysis. |
| Catalog funds and securitizations | Lender and ABS workflows require repeatable evidence, reserves, concentration, and valuation support. |

Plugin role: create faster diligence packets, financing packages, and IC memos
from the same normalized evidence base.

## Differentiators for this plugin

To be world-class, the plugin should be:

- **Evidence-first.** Every material conclusion links to source files,
  extracted fields, or labeled assumptions.
- **System-agnostic.** Work from folders, exports, PDFs, CSVs, JSON, and API
  responses instead of assuming one royalty platform.
- **Rights-aware.** Never collapse publishing, masters, neighboring rights,
  recoupment, reserves, and sync into generic revenue.
- **Exception-driven.** Surface missing documents, mismatched identifiers,
  unsupported income, and valuation-sensitive risks quickly.
- **Human-in-the-loop.** Counsel, royalty auditors, and investment teams approve
  conclusions; the plugin does extraction, reconciliation, checks, and drafting.
- **Output-oriented.** Produce buyer memos, seller cleanup reports, financing
  packs, claim worklists, and post-close admin trackers.

## Anti-positioning

Avoid these traps:

- Do not become a royalty accounting system.
- Do not become a licensed data provider.
- Do not replace legal diligence.
- Do not hardcode one provider's schema as the only path.
- Do not treat streaming popularity as royalty evidence.
- Do not generate polished memos without workpapers.
