# SupplyExtract Technical Specification

## Runtime
Next.js App Router on Vercel.

## Extraction
POST /api/extract receives one application/pdf file, validates size and entitlement, and sends the PDF transiently to the OpenAI Responses API using input_file plus a strict JSON schema.

Required runtime env:
- OPENAI_API_KEY
- OPENAI_EXTRACTION_MODEL
- ALLOW_UNLICENSED_EXTRACTION

## Entitlement
Paid mode validates a Lemon Squeezy license key against the official License API and rejects a valid key if its variant_id does not match LEMON_SQUEEZY_VARIANT_ID.

## Storage
Run #001 adds no product database and no application-level persistent PDF storage.

## Output
Editable client review plus CSV/JSON export.

## Privacy
The application privacy page must state that document content is sent to OpenAI to perform extraction and that third-party processing is governed by the provider's applicable terms/policies. Do not claim that no upstream retention occurs.
