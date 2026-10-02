import os
import re
from pathlib import Path

from builder.runtime import CommandError, Runtime


URL_RE = re.compile(r"https://[a-zA-Z0-9.-]+\.vercel\.app")


class VercelDeployer:
    def __init__(self):
        self.runtime = Runtime()

    def deploy(
        self,
        release_dir: Path,
        production: bool = True,
        environment: dict[str, str] | None = None,
    ) -> str:
        token = os.getenv("VERCEL_TOKEN", "").strip()
        if not token:
            raise RuntimeError("VERCEL_TOKEN is required for non-interactive deployment.")
        if not self.runtime.which("npx"):
            raise RuntimeError("npx not found. Install Node.js 20.9+.")

        # First preview deployment links/creates the Vercel project non-interactively.
        preview_output = self.runtime.run(
            ["npx", "vercel@latest", "deploy", "--yes", "--token", token],
            release_dir,
            timeout=1800,
            sensitive_values=[token],
        )
        preview_urls = URL_RE.findall(preview_output)
        if not preview_urls:
            raise RuntimeError("Vercel preview deployment did not return a URL.")

        for key, value in (environment or {}).items():
            if value:
                self._upsert_env(
                    release_dir,
                    key,
                    value,
                    token,
                    target="production",
                )

        if not production:
            return preview_urls[-1]

        prod_output = self.runtime.run(
            [
                "npx",
                "vercel@latest",
                "deploy",
                "--prod",
                "--yes",
                "--token",
                token,
            ],
            release_dir,
            timeout=1800,
            sensitive_values=[token],
        )
        urls = URL_RE.findall(prod_output)
        if not urls:
            raise RuntimeError("Vercel production deployment finished without a URL.")
        return urls[-1]

    def _upsert_env(
        self,
        release_dir: Path,
        key: str,
        value: str,
        token: str,
        target: str,
    ) -> None:
        visibility = "secret" if self._is_secret(key) else "config"
        base = [
            "npx",
            "vercel@latest",
            "env",
        ]
        add = base + [
            "add",
            key,
            target,
            "--value",
            value,
            "--visibility",
            visibility,
            "--yes",
            "--token",
            token,
        ]
        try:
            self.runtime.run(
                add,
                release_dir,
                timeout=300,
                sensitive_values=[token, value],
            )
            return
        except CommandError:
            update = base + [
                "update",
                key,
                target,
                "--value",
                value,
                "--visibility",
                visibility,
                "--yes",
                "--token",
                token,
            ]
            self.runtime.run(
                update,
                release_dir,
                timeout=300,
                sensitive_values=[token, value],
            )

    @staticmethod
    def _is_secret(key: str) -> bool:
        upper = key.upper()
        return any(x in upper for x in ("SECRET", "TOKEN", "KEY", "PASSWORD"))
