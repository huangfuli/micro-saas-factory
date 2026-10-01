import os
import re
from pathlib import Path
from builder.runtime import Runtime


URL_RE = re.compile(r"https://[a-zA-Z0-9.-]+\.vercel\.app")


class VercelDeployer:
    def __init__(self):
        self.runtime = Runtime()

    def deploy(self, release_dir: Path, production: bool = True) -> str:
        token = os.getenv("VERCEL_TOKEN", "").strip()
        if not token:
            raise RuntimeError("VERCEL_TOKEN is required for non-interactive deployment.")
        if not self.runtime.which("npx"):
            raise RuntimeError("npx not found. Install Node.js 20.9+.")

        command = [
            "npx", "vercel@latest", "deploy", "--yes",
            "--token", token,
        ]
        if production:
            command.append("--prod")

        output = self.runtime.run(
            command,
            release_dir,
            timeout=1800,
            sensitive_values=[token],
        )
        urls = URL_RE.findall(output)
        if not urls:
            raise RuntimeError("Vercel deployment finished without a deployment URL.")
        return urls[-1]
