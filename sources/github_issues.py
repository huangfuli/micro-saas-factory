import os
from datetime import datetime
from urllib.parse import quote
from schemas.signal import DemandSignal
from sources.base import SignalSource
from sources.http import get_json


class GitHubIssuesSource(SignalSource):
    name = "github_issues"
    endpoint = "https://api.github.com/search/issues"

    def __init__(self, queries: list[str] | None = None):
        self.queries = queries or [
            '"feature request" is:issue is:open',
            '"would be nice" is:issue is:open',
            '"wish there was" is:issue is:open',
        ]

    def fetch(self, limit: int = 30) -> list[DemandSignal]:
        if os.getenv("SCOUT_GITHUB_ENABLED", "1") != "1":
            return []
        per_query = max(1, min(20, limit // len(self.queries)))
        results = []
        for query in self.queries:
            data = get_json(f"{self.endpoint}?q={quote(query)}&sort=updated&order=desc&per_page={per_query}") or {}
            for item in data.get("items", []):
                results.append(DemandSignal(
                    source=self.name,
                    external_id=str(item["id"]),
                    title=item.get("title", ""),
                    text=(item.get("body") or "")[:4000],
                    url=item["html_url"],
                    author=(item.get("user") or {}).get("login"),
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")) if item.get("created_at") else None,
                    engagement=int(item.get("comments", 0)),
                ))
        return results[:limit]
