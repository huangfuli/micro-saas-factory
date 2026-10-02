import json
from datetime import datetime, timezone
from pathlib import Path


def write_report(opportunities, signals, directory: str = "data/reports") -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    filename = path / f"scout-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signal_count": len(signals),
        "opportunity_count": len(opportunities),
        "opportunities": [x.model_dump(mode="json") for x in opportunities],
    }
    filename.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return filename
