# SupplyExtract — MVP PRD

## Product
Turn supplier invoice and purchase-order PDFs into reviewable line-item CSV and JSON.

## User
Small logistics, manufacturing, trades, procurement and operations teams that currently re-key supplier documents into spreadsheets.

## Core job
Upload one supplier PDF, extract common header and line-item fields, review/correct them, then export structured data.

## In scope
- Upload one PDF up to 10 MB
- Extract document type, vendor, document number, date, currency and totals
- Extract line items including SKU, description, quantity, unit, unit price and line total
- Show extracted data in an editable review screen before export
- Download reviewed data as CSV or JSON
- Validate a Lemon Squeezy subscription license key for paid access
- Allow a deliberately limited unlicensed demo only when explicitly enabled by environment configuration
- Process documents without adding application-level persistent document storage in the MVP

## Out of scope
- Bank-statement extraction
- Automatic accounting or ERP posting
- Automatic invoice approval
- Email inbox ingestion
- Batch processing
- Vendor-specific training
- Guarantees of extraction accuracy
- Long-term document archive

## Acceptance
- PDF MIME type and 10 MB maximum are enforced server-side
- Missing or uncertain fields may be returned as null rather than invented
- The review screen allows editing every extracted header field and line-item field
- CSV output contains one row per line item and repeats document-level identifiers
- JSON output preserves the complete reviewed document structure
- Uploaded PDF bytes are not written to the product database or filesystem by application code
- Paid-mode extraction requires a valid license key for the configured Lemon Squeezy variant
- Public copy states that users should verify extracted data before relying on it

## Safety / truthfulness
- AI extraction is not guaranteed to be correct.
- Users must review output before accounting, procurement or payment decisions.
- The MVP does not advertise bank-statement processing.
- The application does not intentionally persist uploaded PDF bytes.
- Privacy copy must accurately disclose OpenAI processing and must not promise upstream zero retention.
