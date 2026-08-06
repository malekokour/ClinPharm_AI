#!/usr/bin/env python3
"""Check a briefing package for the elements a regulatory meeting request is normally expected to contain.

Emits mechanical findings only. Both sides of every conflict are preserved with
their locators; this script never decides which is correct.

Author: Malek Okour
Dependencies: Python standard library only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from findings import Finding, Report

REQUIRED = [
    ("meeting objective", r"objectiv|purpose of (?:the )?meeting"),
    ("numbered questions", r"question\s*\d|\bq\d+\b"),
    ("company position per question", r"position|proposal|we propose"),
    ("supporting data reference", r"see\s+|section\s+\d|table\s+\d|appendix"),
    ("development status", r"development status|programme status|program status"),
    ("regulatory history", r"previous (?:meeting|interaction)|regulatory history"),
]


def run(ns) -> Report:
    text = read(ns.package).lower()
    report = Report(tool="align_questions")
    report.count("required elements", len(REQUIRED))

    present = 0
    for name, pattern in REQUIRED:
        if re.search(pattern, text):
            present += 1
        else:
            report.add(Finding(
                rule="required-element-absent",
                severity="Major",
                item=name,
                observed="not found",
                expected="an explicit statement addressing this item",
                locator="whole document",
                detail="Absence is reported as absence. A missing element is not assumed "
                       "to be covered elsewhere or intentionally omitted.",
            ))
    report.count("elements present", present)

    if present == 0:
        report.cannot_assess(
            "coverage assessment",
            "none of the expected elements were found, which usually means the wrong "
            "document was supplied",
            "the document this checker targets",
        )
    return report


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--package", required=True, help="document text")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    ns = parser.parse_args()
    report = run(ns)
    print(report.render(as_json=ns.json))
    return 1 if any(f.severity == "Critical" for f in report.findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
