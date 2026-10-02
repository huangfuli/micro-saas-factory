import json
import os
from pathlib import Path
from schemas.build import CodeBundle
from schemas.product import ProductPackage


ALLOWED_PREFIXES = ("src/", "docs/")


def safe_target(root: Path, relative: str) -> Path:
    clean = relative.replace("\\", "/").lstrip("/")
    if ".." in clean.split("/"):
        raise ValueError(f"Unsafe generated path: {relative}")
    if not clean.startswith(ALLOWED_PREFIXES):
        raise ValueError(f"Generated path is outside allowed prefixes: {relative}")
    target = (root / clean).resolve()
    if root.resolve() not in target.parents:
        raise ValueError(f"Generated path escapes workspace: {relative}")
    return target


class OpenAICodegenProvider:
    """Optional product-specific code generation restricted to src/ and docs/."""

    def __init__(self):
        self.model = os.getenv(
            "OPENAI_CODE_MODEL",
            os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
        )

    def generate(self, package: ProductPackage) -> CodeBundle:
        if not os.getenv("OPENAI_API_KEY"):
            return CodeBundle(
                summary="OPENAI_API_KEY not configured; deterministic scaffold only.",
                files=[],
                verification_commands=["npm run lint", "npm run build"],
            )

        from openai import OpenAI

        prompt = f"""
You are Builder Agent v0.1 inside a MicroSaaS product factory.
Improve an existing Next.js App Router TypeScript scaffold for this product package:

{json.dumps(package.model_dump(mode="json"), ensure_ascii=False)}

Generate ONLY product-specific files under src/ or docs/.
Do not generate package.json, lockfiles, secrets, environment values, CI files, shell scripts, or infrastructure.
Use only React/Next.js built-ins already present in the scaffold; do not assume uninstalled npm packages.
Focus on T003 core workflow UX, domain types, API route behavior, and useful mock/local behavior that can compile before external integrations exist.
Every file must be complete and buildable.
"""
        client = OpenAI()
        response = client.responses.create(
            model=self.model,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "code_bundle",
                    "strict": True,
                    "schema": CodeBundle.model_json_schema(),
                }
            },
            store=False,
        )
        return CodeBundle.model_validate_json(response.output_text)

    def apply(self, root: Path, bundle: CodeBundle) -> list[str]:
        written = []
        for generated in bundle.files:
            target = safe_target(root, generated.path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(generated.content, encoding="utf-8")
            written.append(generated.path)
        return written
