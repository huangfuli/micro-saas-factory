# MicroSaaS Agent Factory

AI-native product factory:

`Sources -> Scout -> Gate -> Analyst -> Product Manager -> Builder -> QA -> Launch`

## Current closed loop

`real demand -> evidence -> commercial thesis -> PRD -> generated app -> QA -> release package -> GitHub -> Stripe -> Vercel -> smoke test`

The factory does not mark a product LIVE unless the production deployment responds successfully on the configured smoke-test paths.

## Builder v0.2

Builder creates a Next.js 16.3 App Router product workspace under `builds/<slug>/`.

Generated products now include:

- landing page + dashboard
- health and core-job API routes
- hosted Stripe Checkout session route in subscription mode
- `.env.example`
- `.vercelignore`
- PRD / validation / technical / task docs
- Builder audit file

AI Builder remains restricted to `src/` and `docs/`.

## Launch Agent v0.1

Only products whose Builder result is `BUILT` can enter Launch.

Launch performs:

1. Copy the clean workspace to `releases/<slug>/`.
2. Exclude `node_modules`, `.next`, local env files and Vercel metadata.
3. Produce `releases/<slug>-0.1.0.zip`.
4. Optionally publish an independent GitHub repository with local `gh`.
5. Optionally create a Stripe Product + monthly Price.
6. Optionally create/link a Vercel project, configure production environment values, and deploy production.
7. Smoke-test `/` and `/api/health`.
8. Mark the queue item `LIVE` only if all smoke checks pass.

Launch state:

`BUILT -> READY_TO_PUBLISH -> PUBLISHED -> DEPLOYED -> LIVE`

Failures become `LAUNCH_FAILED` and retain the failure reason.

## Commands

First produce and QA a product:

```bash
python main.py --web-research --productize --pm-ai
python main.py --build-next --builder-ai --qa --clean-build
```

Prepare a release without touching external services:

```bash
python main.py --launch-next
```

Publish the release to a new GitHub product repository:

```bash
python main.py --launch-next --publish-github
```

Provision Stripe recurring billing:

```bash
python main.py --launch-next --provision-stripe
```

Deploy to Vercel and smoke-test:

```bash
python main.py --launch-next --deploy-vercel
```

Full external launch in one run:

```bash
python main.py --launch-next --publish-github --provision-stripe --deploy-vercel
```

## External credentials

Automatic GitHub product-repo creation uses the local GitHub CLI. The current ChatGPT GitHub connector can modify existing repositories but does not expose repository creation, so the factory uses `gh repo create` when it is run on your machine.

Required launch configuration is shown in `.env.example`:

- `GITHUB_OWNER`
- `PRODUCT_REPO_VISIBILITY`
- `VERCEL_TOKEN`
- `STRIPE_SECRET_KEY`
- optional `STRIPE_WEBHOOK_SECRET`

Secrets are never written into generated product source. Vercel command failures redact tokens and secret values from factory error logs.

## Stripe path

Launch creates a Stripe Product and recurring monthly Price. The generated Next.js checkout endpoint reads `STRIPE_SECRET_KEY` and `STRIPE_PRICE_ID` only on the server and creates a hosted Checkout Session in subscription mode.

## Vercel path

Launch first creates a preview deployment to link/create the Vercel project, then upserts configured production environment variables, creates the production deployment, and performs HTTP smoke checks.

## GitHub path

If `git`, `gh`, and `GITHUB_OWNER` are available, Launch initializes the release directory, creates the product repository, adds the remote, commits the generated launch candidate, and pushes it.

## Guardrails

- VALIDATE products cannot reach Builder.
- non-BUILT products cannot reach Launch.
- local secrets are excluded from release packages.
- AI codegen cannot edit package files, CI, secrets or infrastructure.
- deployment is not called LIVE until smoke tests succeed.
- every release writes `.factory/release_manifest.json`.
- every launch writes `.factory/launch_result.json`.

## Next milestone

Launch v0.2 adds domain provisioning, Stripe webhook registration, production analytics/monitoring, rollback, and automated post-launch KPI collection so the factory can decide whether to iterate, hold, or retire each MicroSaaS.
