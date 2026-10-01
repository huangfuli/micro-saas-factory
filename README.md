# MicroSaaS Agent Factory

AI-native product factory: discover real problems, score opportunities, validate ideas, build MVPs, test, launch, and iterate.

Pipeline:

`Sources -> Scout -> Semantic Clusters -> Gate -> Analyst -> PM -> Builder -> QA -> Launch`

## Scout v0.3

Scout mines live public demand from Hacker News and GitHub Issues, extracts pain language, removes duplicate signals, and groups related jobs-to-be-done with a local TF-IDF similarity model.

Each candidate now carries:

- source evidence and URLs
- signal/source counts
- commercial-intent score
- evidence-quality score
- pain, demand, willingness-to-pay, competition, build-ease and acquisition scores

A candidate needs at least two distinct evidence items before it can PASS the product gate.

## Analyst Agent v0.1

Analyst converts the highest-ranked PASS opportunities into commercial product theses.

Without an API key it runs a deterministic fallback analysis. With `--web-research` and `OPENAI_API_KEY`, it uses the OpenAI Responses API web-search tool to verify competitors and pricing, then returns schema-validated research.

Analyst outputs:

- target user and job-to-be-done
- commercial intent / urgency / frequency / budget scores
- competitors and pricing
- initial USD price range
- MVP feature set
- acquisition channels
- risks
- research source URLs
- BUILD / VALIDATE / WATCH / REJECT recommendation

Only the top `ANALYST_TOP_N` PASS opportunities are researched to control API cost.

## Run

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Scout only: no OpenAI key required
python main.py

# Scout + deterministic Analyst
python main.py --analyze

# Scout + Analyst + live competitor/pricing research
python main.py --web-research
```

Copy `.env.example` to `.env` or set environment variables through your shell. Reports are written to `data/reports/`.

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
schemas/
  signal.py
  cluster.py
  opportunity.py
  analysis.py
scoring/
reports/
orchestrator/
tests/
```

## Design rules

- No evidence, no PASS.
- Two distinct evidence items are required to cross the product gate.
- Source failures degrade gracefully.
- Cheap deterministic stages run before paid model research.
- Live competitor or pricing facts must come from web research, never model memory alone.
- Analyst web research is optional and limited to top candidates.

## Next milestone

Product Manager Agent v0.1: convert a VALIDATE/BUILD thesis into a one-page PRD, landing-page test, preorder experiment and technical MVP specification.
