# MicroSaaS Agent Factory

AI-native product factory:

`Sources -> Scout -> Gate -> Analyst -> Product Manager -> Builder Queue -> Builder -> QA -> Launch`

## Builder Agent v0.1

Builder consumes the next eligible entry from `data/build_queue.jsonl` and creates an isolated Next.js App Router workspace under `builds/<product-slug>/`.

It performs four controlled stages:

1. Deterministic scaffold: package.json, TypeScript config, landing page, dashboard, health/job API routes, environment template and copied PRD/technical docs.
2. Optional AI codegen: `--builder-ai` may only write inside `src/` and `docs/`; it cannot write secrets, package files, CI, shell scripts or infrastructure.
3. Optional install: `--install` runs npm install.
4. QA gate: `--qa` runs npm install, npm run lint and npm run build. Only successful QA moves the queue item to BUILT.

The generated scaffold targets Next.js 16.3 and requires Node.js 20.9+.

### Commands

```bash
# Discover + analyze + create build-ready product packages
python main.py --web-research --productize --pm-ai

# Create a deterministic product workspace from the next BUILD item
python main.py --build-next

# Add product-specific AI-generated core workflow files
python main.py --build-next --builder-ai --clean-build

# Install dependencies and verify a deployable build
python main.py --build-next --builder-ai --qa --clean-build
```

### Builder state machine

`QUEUED -> BUILDING -> SCAFFOLDED -> BUILT`

Failures become `FAILED` and retain the error. A failed or scaffolded item can be picked up again for repair/rebuild.

### Safety boundaries

- VALIDATE products never enter Builder.
- AI-generated files are restricted to `src/` and `docs/`.
- Secrets are never generated into source files.
- Builder does not modify its own factory repository while generating products.
- Every workspace writes `.factory/build_result.json` for auditability.
- QA must pass before status becomes BUILT.

## Earlier stages

Scout v0.3 mines Hacker News and GitHub Issues, deduplicates signals, performs local semantic clustering and scores commercial intent/evidence quality.

Analyst v0.1 turns strong opportunities into commercial theses and can optionally use live web research for competitors/pricing.

Product Manager v0.1 generates `PRD.md`, `LANDING_PAGE.md`, `VALIDATION.md`, `TECH_SPEC.md`, `TASKS.md`, `product.json` and `builder_manifest.json`.

BUILD products enter `data/build_queue.jsonl`; VALIDATE products remain blocked for market validation.

## Models

The default API model is `gpt-5.6-sol`. Override with `OPENAI_MODEL` or `OPENAI_CODE_MODEL`.

## Next milestone

Builder v0.2 will create a dedicated GitHub repository for each BUILT product, open a PR with generated code, and hand the successful build to Deployment/Launch Agent for Vercel + Stripe + domain configuration.
