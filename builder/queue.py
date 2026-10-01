import json
from pathlib import Path
from schemas.product import ProductPackage


class BuilderQueue:
    def __init__(self, path: str = "data/build_queue.jsonl"):
        self.path = Path(path)

    def enqueue(self, package: ProductPackage) -> bool:
        if package.readiness != "READY_FOR_BUILD":
            return False

        self.path.parent.mkdir(parents=True, exist_ok=True)
        existing = set()
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    existing.add(json.loads(line)["product_slug"])
                except (KeyError, json.JSONDecodeError):
                    continue

        slug = package.builder_manifest.product_slug
        if slug in existing:
            return False

        record = {
            "product_slug": slug,
            "status": "QUEUED",
            "build_goal": package.builder_manifest.build_goal,
            "manifest_path": f"products/{slug}/builder_manifest.json",
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
