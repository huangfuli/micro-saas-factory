# MicroSaaS Agent Factory

AI-native product factory that turns public demand signals into validated, build-ready MicroSaaS product packages.

## Pipeline

`Sources -> Scout -> Semantic Clusters -> Gate -> Analyst -> Product Manager -> Builder Queue -> Builder -> QA -> Launch`

## Scout v0.3

Scout mines live public demand from Hacker News and GitHub Issues, extracts pain language, removes duplicate signals, groups related jobs-to-be-done, and scores commercial intent plus evidence quality.

A candidate needs at least two distinct evidence items before it can PASS.

## Analyst Agent v0.1

Analyst converts top PASS opportunities into commercial theses:

- target user / JTBD
- commercial intent, urgency, frequency and budget
- competitors and pricing when live research is enabled
- MVP candidates
- acquisition channels
- risks
- BUILD / VALIDATE / WATCH / REJECT

Live competitor/pricing facts use Responses API web search only when `--web-research` is enabled.

## Product Manager Agent v0.1

Product Manager automatically converts only BUILD/VALIDATE theses into a product directory under `products/<slug>/`.

Each product gets:

- `product.json` — complete structured product package
- `PRD.md` — one-page MVP PRD
- `LANDING_PAGE.md` — validation/launch copy
- `VALIDATION.md` — measurable waitlist/preorder experiments
- `TECH_SPEC.md` — build architecture and interfaces
- `TASKS.md` — Builder-ready task breakdown
- `builder_manifest.json` — machine-readable Builder contract

### Development gate

`BUILD -> READY_FOR_BUILD -> data/build_queue.jsonl`

`VALIDATE -> BLOCKED_FOR_VALIDATION -> validation package only`

This prevents the coding agent from automatically building a weak thesis before market validation.

## Run

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# 1. Scout only
python main.py

# 2. Scout + Analyst
python main.py --analyze

# 3. Live competitor/pricing research
python main.py --web-research

# 4. End-to-end: opportunity -> product package
python main.py --productize

# 5. End-to-end with live market research + AI product design
python main.py --web-research --productize --pm-ai
```

Without `OPENAI_API_KEY`, Scout, Analyst fallback, and Product Manager fallback still work. AI stages use schema-constrained outputs when enabled.

## Current architecture

```
sources/
  hackernews.py
  github_issues.py

agents/
  signal_miner.py
  commercial_intent.py
  deduplicator.py
  semantic_clusterer.py
  opportunity_builder.py
  scout.py
  analyst.py
  product_manager.py

schemas/
  signal.py
  cluster.py
  opportunity.py
  analysis.py
  product.py

reports/
  json_report.py
  analysis_report.py
  product_package.py

builder/
  queue.py

scoring/
orchestrator/
tests/
products/
```

## Operating principles

- No evidence, no PASS.
- Two evidence items minimum before Analyst.
- Cheap deterministic stages run before paid AI research.
- VALIDATE does not automatically enter coding.
- BUILD is converted into a machine-readable Builder queue entry.
- Every coding task includes explicit acceptance criteria.
- Market claims must remain traceable to source evidence.

## Next milestone

Builder Agent v0.1 will consume `data/build_queue.jsonl`, create an isolated product repository/branch, implement tasks T001-T006, run tests, and produce a launch candidate rather than merely generating code snippets.
