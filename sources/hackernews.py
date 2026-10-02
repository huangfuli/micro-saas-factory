from datetime import datetime, timezone
from html import unescape
from re import sub
from schemas.signal import DemandSignal
from sources.base import SignalSource
from sources.http import get_json


class HackerNewsSource(SignalSource):
    name = "hackernews"
    base = "https://hacker-news.firebaseio.com/v0"

    def fetch(self, limit: int = 50) -> list[DemandSignal]:
        ids = get_json(f"{self.base}/askstories.json") or []
        signals = []
        for item_id in ids[:limit]:
            item = get_json(f"{self.base}/item/{item_id}.json") or {}
            if not item or item.get("deleted") or item.get("dead"):
                continue
            title = unescape(item.get("title", ""))
            text = sub(r"<[^>]+>", " ", unescape(item.get("text", "")))
            signals.append(DemandSignal(
                source=self.name,
                external_id=str(item_id),
                title=title,
                text=" ".join(text.split()),
                url=f"https://news.ycombinator.com/item?id={item_id}",
                author=item.get("by"),
                created_at=datetime.fromtimestamp(item["time"], tz=timezone.utc) if item.get("time") else None,
                engagement=int(item.get("score", 0)) + int(item.get("descendants", 0)),
            ))
        return signals
