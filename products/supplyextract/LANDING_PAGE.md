# SupplyExtract

## Headline
Stop retyping supplier PDFs into spreadsheets.

## Subheadline
Upload a supplier invoice or purchase order, review the extracted header and line items, then export clean CSV or JSON.

## What it currently does
- accepts a single PDF
- extracts common invoice / purchase-order header fields
- extracts line items such as SKU, description, quantity, unit price and line total
- lets the user edit the result before export
- exports CSV and JSON

## Accuracy
SupplyExtract uses AI extraction. Results can be incomplete or incorrect, especially on poor scans or unusual layouts. Users must review extracted values before relying on them.
