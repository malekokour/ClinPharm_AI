#!/usr/bin/env python3
"""Check whether stated in vitro findings trigger a clinical DDI study that the document does not mention.

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

RATIO = re.compile(r"(AUCR|Cmax\s*ratio|AUC\s*ratio)\D{0,20}(\d+(?:\.\d+)?)", re.I)
INHIB = re.compile(r"\b(IC50|Ki)\b\D{0,20}(\d+(?:\.\d+)?)\s*(nM|uM|µM|mM)", re.I)
CLINICAL = re.compile(r"clinical (?:DDI|drug[- ]drug interaction) study|dedicated interaction study", re.I)
ENZYMES = ("CYP3A4", "CYP2D6", "CYP2C9", "CYP2C19", "CYP1A2", "P-gp", "BCRP", "OATP")


def run(ns) -> Report:
    text = read(ns.document)
    report = Report(tool="check_ddi_triggers")

    ratios = [(m.group(1), float(m.group(2))) for m in RATIO.finditer(text)]
    inhib = [(m.group(1), float(m.group(2)), m.group(3)) for m in INHIB.finditer(text)]
    enzymes = [e for e in ENZYMES if e.lower() in text.lower()]
    has_clinical = bool(CLINICAL.search(text))

    report.count("interaction ratios found", len(ratios))
    report.count("inhibition constants found", len(inhib))
    report.count("enzymes or transporters named", len(enzymes))

    if not ratios and not inhib:
        report.cannot_assess(
            "DDI trigger assessment",
            "no interaction ratios or inhibition constants were found",
            "a document reporting AUCR/Cmax ratios or IC50/Ki values",
        )
        return report

    # A ratio at or beyond the conventional no-effect boundary is a mechanical
    # trigger for further evaluation. Whether a study is actually warranted is a
    # regulatory and scientific judgement this tool does not make.
    for label, value in ratios:
        if value >= 1.25 or value <= 0.80:
            sev = "Critical" if (value >= 2.0 or value <= 0.5) else "Major"
            if not has_clinical:
                report.add(Finding(
                    rule="trigger-without-stated-followup",
                    severity=sev,
                    item=f"{label} = {value:g}",
                    observed=f"{label} {value:g}, outside 0.80-1.25",
                    expected="a stated clinical interaction study, or a stated rationale for not doing one",
                    locator="interaction results",
                    detail="The ratio crosses the conventional no-effect boundary and the document "
                           "does not mention a clinical interaction study. Reported as a gap in the "
                           "document, not as a conclusion about the interaction.",
                ))
            else:
                report.add(Finding(
                    rule="trigger-noted",
                    severity="Minor",
                    item=f"{label} = {value:g}",
                    observed=f"{label} {value:g}, outside 0.80-1.25",
                    expected="—",
                    locator="interaction results",
                    detail="A clinical study is mentioned; this row records the trigger for traceability.",
                ))

    if inhib and not enzymes:
        report.add(Finding(
            rule="constant-without-named-target",
            severity="Major",
            item="inhibition constant",
            observed=f"{len(inhib)} value(s) with no named enzyme or transporter",
            expected="each constant attributed to a named CYP or transporter",
            locator="in vitro results",
            detail="An unattributed constant cannot be traced to a mechanism.",
        ))
    return report


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--document", required=True, help="DDI summary or briefing text")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    ns = parser.parse_args()
    report = run(ns)
    print(report.render(as_json=ns.json))
    return 1 if any(f.severity == "Critical" for f in report.findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
