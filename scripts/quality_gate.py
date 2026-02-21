"""Run the release quality gate checks in sequence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_step(command: list[str]) -> None:
    print(f"\n==> {' '.join(command)}")
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> int:
    """Execute compile, tests, and smoke checks for release readiness."""
    steps = [
        [sys.executable, "-m", "compileall", "app", "scripts"],
        [sys.executable, "-m", "pytest", "-q"],
        [sys.executable, "scripts/smoke_check.py"],
    ]

    try:
        for command in steps:
            _run_step(command)
    except subprocess.CalledProcessError as error:
        print(f"\nQuality gate failed: {' '.join(error.cmd)} (exit code {error.returncode})")
        return error.returncode

    print("\nQuality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
