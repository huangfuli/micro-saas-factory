import os
from pathlib import Path
from builder.runtime import Runtime


class GitHubPublisher:
    """Publishes a release workspace with the local gh CLI when available."""

    def __init__(self):
        self.runtime = Runtime()

    def publish(self, release_dir: Path, slug: str) -> str:
        if not self.runtime.which("git"):
            raise RuntimeError("git CLI not found.")
        if not self.runtime.which("gh"):
            raise RuntimeError(
                "gh CLI not found. Create the product repository manually or install GitHub CLI."
            )

        owner = os.getenv("GITHUB_OWNER", "").strip()
        if not owner:
            raise RuntimeError("GITHUB_OWNER is required for automatic repo creation.")

        repo = f"{owner}/{slug}"
        visibility = os.getenv("PRODUCT_REPO_VISIBILITY", "private").lower()
        if visibility not in {"private", "public"}:
            raise ValueError("PRODUCT_REPO_VISIBILITY must be private or public.")

        if not (release_dir / ".git").exists():
            self.runtime.run(["git", "init"], release_dir)
            self.runtime.run(["git", "add", "."], release_dir)
            self.runtime.run(
                ["git", "-c", "user.name=MicroSaaS Factory", "-c",
                 "user.email=factory@users.noreply.github.com",
                 "commit", "-m", "feat: initial generated product"],
                release_dir,
            )

        self.runtime.run(
            [
                "gh", "repo", "create", repo,
                f"--{visibility}",
                "--source=.",
                "--remote=origin",
                "--push",
            ],
            release_dir,
            timeout=300,
        )
        return f"https://github.com/{repo}"
