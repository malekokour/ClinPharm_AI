#!/usr/bin/env python3
"""Run every portable local quality gate for ClinPharm AI.

Author: ClinPharm AI contributors
Date: 2026-07-30
Dependencies: Python standard library plus project dependencies
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> None:
    print(f"\n== {label} ==", flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> int:
    python = sys.executable
    run("Repository contract", [python, "scripts/validate_repo.py"])
    run("Benchmark digests", [python, "scripts/verify_benchmark_digests.py"])
    run("Markdown/DOCX parity", [python, "scripts/check_docx_parity.py"])
    run("Generated artifact freshness", [python, "scripts/check_generated_freshness.py"])
    run("Contract tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"])
    run("Public-release privacy scan", [python, "scripts/privacy_scan.py"])
    run(
        "Python compilation",
        [
            python,
            "-m",
            "compileall",
            "-q",
            "scripts",
            "tests",
        ],
    )
    print("\nPASS: all ClinPharm AI quality gates completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
