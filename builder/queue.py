import json
from pathlib import Path
from schemas.product import ProductPackage


class BuilderQueue:
    def __init__(self, path: str = "data/build_queue.jsonl"):
        self.path = Path(path)

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    def _write(self, rows: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)
        self.path.write_text(text, encoding="utf-8")

    def enqueue(self, package: ProductPackage) -> bool:
        if package.readiness != "READY_FOR_BUILD":
            return False

        rows = self._read()
        slug = package.builder_manifest.product_slug
        if any(x.get("product_slug") == slug for x in rows):
            return False

        rows.append({
            "product_slug": slug,
            "status": "QUEUED",
            "build_goal": package.builder_manifest.build_goal,
            "manifest_path": f"products/{slug}/builder_manifest.json",
        })
        self._write(rows)
        return True

    def claim_next(self) -> dict | None:
        rows = self._read()
        for row in rows:
            if row.get("status") in {"QUEUED", "SCAFFOLDED", "FAILED"}:
                return row
        return None

    def update_status(self, slug: str, status: str, error: str | None = None) -> None:
        rows = self._read()
        found = False
        for row in rows:
            if row.get("product_slug") == slug:
                row["status"] = status
                if error:
                    row["error"] = error
                else:
                    row.pop("error", None)
                found = True
                break
        if not found:
            raise KeyError(f"Build queue item not found: {slug}")
        self._write(rows)
