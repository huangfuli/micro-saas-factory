# MicroSaaS Agent Factory

AI-native product factory: discover real problems, score opportunities, validate ideas, build MVPs, test, launch, and iterate.

Pipeline: `Scout -> Score -> Gate -> Rank -> Analyst -> PM -> Builder -> QA -> Launch`

## Scout v0.2

Scout now discovers public demand signals instead of returning hard-coded ideas.

Current pipeline:

`Hacker News + GitHub Issues -> DemandSignal -> pain-pattern mining -> dedupe -> opportunity grouping -> weighted scoring -> PASS/REJECT -> Top 20 JSON report`

Every opportunity retains source evidence and URLs so later agents can audit why it exists.

### Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Reports are written to `data/reports/`.

### Design rules

- No evidence, no PASS.
- Source failures degrade gracefully instead of stopping the whole factory.
- v0.2 uses deterministic extraction/scoring before adding LLM enrichment, making the discovery layer testable and auditable.
- GitHub search is intentionally bounded; disable it with `SCOUT_GITHUB_ENABLED=0` if needed.

## Next milestone

Scout v0.3 will add semantic clustering, stronger commercial-intent extraction, competitor/pricing research and an Analyst Agent that turns evidence clusters into product hypotheses.
