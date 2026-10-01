import shutil
import subprocess
from pathlib import Path


class CommandError(RuntimeError):
    pass


class Runtime:
    def which(self, command: str) -> str | None:
        return shutil.which(command)

    def run(
        self,
        command: list[str],
        cwd: Path,
        timeout: int = 900,
        sensitive_values: list[str] | None = None,
    ) -> str:
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
            rendered_command = " ".join(command)
            rendered_output = output[-5000:]
            for secret in sensitive_values or []:
                if secret:
                    rendered_command = rendered_command.replace(secret, "***REDACTED***")
                    rendered_output = rendered_output.replace(secret, "***REDACTED***")
            raise CommandError(
                f"Command failed ({process.returncode}): {rendered_command}\n{rendered_output}"
            )
        return output
