# Production Run #001 — SupplyExtract

## Decision

BUILD

SupplyExtract is a narrow SaaS for extracting supplier invoice and purchase-order PDF headers and line items into reviewable structured data, then CSV/JSON.

The first release deliberately avoids bank statements, automatic accounting posting, inbox ingestion, and claims of perfect accuracy.

## Evidence

The run is grounded in public workflow pain around repetitive PDF-to-spreadsheet entry, including a small-business logistics example describing approximately 50 supplier invoices per week and manual entry of SKU, quantity and price into Excel.

Competitor research confirms an existing paid market for document parsing, but Run #001 is positioned as a narrower review-before-export workflow rather than an enterprise automation platform.

See evidence.json for source URLs and the exact summaries used by the factory.

## Build boundary

MVP:
- one PDF per extraction
- maximum 10 MB
- common supplier invoice / PO header fields
- line items
- editable review
- CSV and JSON export
- Lemon Squeezy subscription license validation
- no application-level persistent PDF archive

The product must tell users to review AI-extracted values before relying on them.

## Billing

The product package does not hard-code a public selling price. Launch must verify the active Lemon Squeezy Price and inject the displayed plan price into the public site.

## Candidate domain

supplyextract.com was shown as available in the Vercel domain search during Run #001. No domain purchase has been made.

## Run locally

1. Enqueue the committed product:
   python scripts/enqueue_product.py supplyextract

2. Build:
   python main.py --build-next --qa --clean-build

3. Configure runtime secrets and real public business information.

4. Create the real Lemon Squeezy Test Mode subscription product/variant and enable the desired subscription/licensing configuration.

5. Run the Launch merchant-review flow.

Do not set MERCHANT_REVIEW_ATTESTED=1 until a human verifies that the deployed business description, capabilities, pricing, legal information and refund policy are accurate.
