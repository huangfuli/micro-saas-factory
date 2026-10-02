# MicroSaaS Agent Factory

AI-native product factory:

`Sources -> Scout -> Gate -> Analyst -> Product Manager -> Builder -> QA -> Merchant Review -> Launch`

## Payment provider

The factory uses **Lemon Squeezy** as its payment and subscription provider.

The billing implementation is intentionally designed around Lemon Squeezy's merchant-review process:

1. Build a real, working SaaS MVP.
2. Publish a complete website with real product information.
3. Show the actual subscription price.
4. Publish Privacy Policy, Terms of Service, Refund Policy and Contact pages.
5. Create the actual SaaS product + monthly subscription variant in Lemon Squeezy **Test Mode**.
6. Verify the website content and Lemon Squeezy product match.
7. Deploy the review-ready site.
8. Submit the Lemon Squeezy store activation/KYC/KYB review.
9. After approval, copy/use the product in Live Mode and replace test API key/store/variant IDs with live values.
10. Re-run Launch; only a verified live-mode variant can move the factory to `LIVE`.

## Truthfulness rule

The product factory must never invent business evidence.

Generated public pages are forbidden from inventing:

- customers or customer logos
- testimonials
- user/customer counts
- revenue or sales numbers
- awards
- partnerships
- guarantees
- product capabilities that are not implemented

Before external launch, a human must verify the site and set:

`MERCHANT_REVIEW_ATTESTED=1`

Only set this after confirming that the business description, product scope, pricing, legal pages and checkout configuration are truthful.

## Review-ready website

Every generated SaaS contains:

- `/` — product description
- `/pricing` — subscription pricing
- `/privacy` — privacy policy
- `/terms` — terms of service
- `/refund-policy` — refund policy
- `/contact` — support/contact information
- `/dashboard` — product workspace
- `/api/health` — health check
- `/api/billing/checkout` — Lemon Squeezy checkout creation
- `/api/billing/webhook` — signed Lemon Squeezy webhook receiver

The Launch compliance gate rejects obvious placeholder content and common unverifiable marketing claims.

## Lemon Squeezy integration

The generated checkout endpoint uses:

- `LEMON_SQUEEZY_API_KEY`
- `LEMON_SQUEEZY_STORE_ID`
- `LEMON_SQUEEZY_VARIANT_ID`

It creates a Lemon Squeezy checkout for the configured Store + Variant and redirects the user to the hosted checkout URL.

The webhook endpoint validates the `X-Signature` HMAC using:

- `LEMON_SQUEEZY_WEBHOOK_SECRET`

Launch registers an idempotent webhook URL for the deployed product and subscribes to core order/subscription events.

## Price verification

The factory does not trust a manually typed website price.

Before deployment, Launch retrieves the configured Lemon Squeezy Variant, Product and current Price object and verifies:

- variant belongs to the configured store
- product is published
- variant is active
- pricing category is subscription
- pricing model is standard
- renewal interval is one month
- price is positive
- Lemon Squeezy product has a substantive description

The website pricing value deployed to Vercel is generated from the verified Lemon Squeezy Price object.

## Test Mode vs Live Mode

If Lemon Squeezy reports the configured Variant as Test Mode, successful deployment is marked:

`BILLING_TEST`

It is **not** marked `LIVE`.

After Lemon Squeezy approves the store, replace the credentials and IDs with the live-mode values and launch again.

Only live-mode billing + passing website compliance + successful smoke tests produce:

`LIVE`

## Builder v0.2

Builder creates a Next.js 16.3 App Router workspace under:

`builds/<product-slug>/`

AI code generation remains restricted to `src/` and `docs/`.

QA runs:

```bash
npm install
npm run lint
npm run build
```

Only QA-passing products become `BUILT`.

## Launch flow

```text
BUILT
  ↓
merchant-review source preflight
  ↓
READY_TO_PUBLISH
  ↓
optional GitHub publish
  ↓
verify Lemon Squeezy product / variant / price
  ↓
human truthfulness attestation
  ↓
Vercel deploy
  ↓
register signed webhook
  ↓
smoke test:
  /
  /pricing
  /privacy
  /terms
  /refund-policy
  /contact
  /api/health
  ↓
BILLING_TEST or LIVE
```

## Configuration

See `.env.example`.

Required for Lemon Squeezy:

```text
LEMON_SQUEEZY_API_KEY
LEMON_SQUEEZY_STORE_ID
LEMON_SQUEEZY_VARIANT_ID
LEMON_SQUEEZY_WEBHOOK_SECRET
```

Required public website facts:

```text
NEXT_PUBLIC_LEGAL_BUSINESS_NAME
NEXT_PUBLIC_SUPPORT_EMAIL
NEXT_PUBLIC_REFUND_POLICY_TEXT
MERCHANT_REVIEW_ATTESTED
```

The displayed plan price is derived from the verified Lemon Squeezy Price object at launch.

## Commands

Build and QA a generated product:

```bash
python main.py --build-next --builder-ai --qa --clean-build
```

Prepare a release without external actions:

```bash
python main.py --launch-next
```

Verify Lemon Squeezy configuration:

```bash
python main.py --launch-next --configure-lemonsqueezy
```

Publish + configure billing + deploy:

```bash
python main.py --launch-next --publish-github --configure-lemonsqueezy --deploy-vercel
```

Before the first merchant review, use Lemon Squeezy Test Mode credentials and product IDs.

After store approval, switch to live-mode credentials/IDs and run the launch command again.

## Guardrails

- VALIDATE opportunities cannot enter Builder.
- non-BUILT products cannot enter Launch.
- missing Pricing/Privacy/Terms/Refund/Contact pages block release.
- placeholder legal/business values block public deployment.
- Lemon Squeezy product configuration is verified before deployment.
- test-mode billing cannot be labeled LIVE.
- local secrets are excluded from release archives.
- command errors redact secret values.
- production smoke checks must pass before LIVE.
- every release writes `.factory/release_manifest.json`.
- every launch writes `.factory/launch_result.json`.

## Next milestone

The next step is **Factory Production Run #001**: use the factory to select one real overseas demand signal, build the first product, deploy the review-ready website with Lemon Squeezy Test Mode, then submit the store for activation.
