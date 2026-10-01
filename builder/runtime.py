import shutil
import subprocess
from pathlib import Path


class CommandError(RuntimeError):
    pass


class Runtime:
    def which(self, command: str) -> str | None:
        return shutil.which(command)

    def run(self, command: list[str], cwd: Path, timeout: int = 900) -> str:
        process = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        output = (process.stdout or "") + (process.stderr or "")
        if process.returncode != 0:
            raise CommandError(
                f"Command failed ({process.returncode}): {' '.join(command)}\n{output[-5000:]}"
            )
        return output
