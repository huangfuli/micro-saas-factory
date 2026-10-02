import argparse
from pathlib import Path

from builder.queue import BuilderQueue
from schemas.product import ProductPackage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    args = parser.parse_args()

    path = Path("products") / args.slug / "product.json"
    if not path.exists():
        raise SystemExit(f"Product package not found: {path}")

    package = ProductPackage.model_validate_json(path.read_text(encoding="utf-8"))
    if BuilderQueue().enqueue(package):
        print(f"Queued: {args.slug}")
    else:
        print(f"Not queued (already present or not READY_FOR_BUILD): {args.slug}")


if __name__ == "__main__":
    main()
