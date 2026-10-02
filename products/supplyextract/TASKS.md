## T001 — Review-ready product shell

Generate the SupplyExtract product, pricing, privacy, terms, refund and contact pages.

Acceptance:
- All merchant-review pages render
- Landing copy describes only implemented MVP functionality
- No invented users, customers, accuracy or savings claims appear

## T002 — PDF extraction API

Implement PDF validation, optional license validation and schema-constrained OpenAI extraction.

Acceptance:
- Only application/pdf is accepted
- Files over 10 MB are rejected
- Uncertain values can remain null
- Response includes editable header fields and line items

## T003 — Review and export UI

Implement upload, editable review table and CSV/JSON download.

Acceptance:
- User can edit all extracted fields
- CSV includes one row per line item
- JSON contains reviewed values
- UI reminds users to verify extracted data

## T004 — Lemon Squeezy entitlement

Validate paid license keys against the configured Lemon Squeezy subscription variant.

Acceptance:
- Invalid license is rejected when paid mode is enabled
- License metadata variant must match configured variant
- No Lemon Squeezy secret is exposed to the browser

## T005 — Privacy and retention verification

Verify app code does not persist uploaded PDF bytes and public privacy text accurately describes OpenAI processing.

Acceptance:
- No application code writes uploaded PDF bytes to disk or database
- Privacy page discloses third-party AI processing
- No claim is made that upstream processors have zero retention

## T006 — QA and launch preflight

Run lint/build plus merchant-review compliance checks.

Acceptance:
- npm run lint passes
- npm run build passes
- Merchant-review source preflight passes
- Core public routes and /api/health are ready for smoke testing
