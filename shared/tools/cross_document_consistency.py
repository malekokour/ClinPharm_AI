#!/usr/bin/env python3
"""T05 — cross-document numeric consistency checker.

Two modes, one engine:

* ``document`` — reconcile within one document and against its declared source
  outputs. Used by ``review-csr-pk-consistency``.
* ``programme`` — maintain a register of values across a document thread and
  diff each document against a version baseline. Used by
  ``reconcile-cross-document-facts``.

The engine exists **only here**. No skill re-implements it; that single-source
rule is what stops two skills drifting apart on the same reconciliation.

Every output is a mechanical finding. The engine never decides which of two
conflicting values is correct — it preserves both with their locators.

Author: ClinPharm AI contributors
Date: 2026-08-05
Dependencies: Python standard library only
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

#: A number is only a *value* when it is not part of an identifier and not a
#: document reference. Both exclusions were added after the fixture produced
#: nonsense comparisons:
#:   * the ``0`` inside ``AUC0–τ`` was extracted as a value of zero;
#:   * ``14.2`` from "Table 14.2.1" was compared against real quantities.
#: The lookbehind rejects a digit glued to a letter or digit; the reference
#: filter drops anything introduced by a section or table marker.
NUMBER = re.compile(
    r"(?<![A-Za-z0-9.])"
    r"(?P<value>-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?)"
    r"(?![0-9]*\.[0-9]+\.)"
    r"\s*(?P<unit>ng·h/mL|ng\*h/mL|ng\.h/mL|µg·h/mL|ng/mL|µg/mL|ug/mL|mg/L|"
    r"pg/mL|L/h/kg|mL/min/kg|mL/min|mL/h|L/h|L/kg|mL|L|h|%)?"
)

#: Text immediately before a number that marks it as a document reference.
REFERENCE_PREFIX = re.compile(
    r"(?:§|section|table|figure|appendix|cohort|amendment|part|v)\s*$", re.IGNORECASE
)


#: Parameter labels recognised in surrounding text, longest first so that
#: "auc0-inf" is not swallowed by "auc". Matching on a *parameter* rather than on
#: raw surrounding text is what lets a prose sentence reconcile against a table
#: row — the two never share context, but they do share a parameter name.
PARAMETER_LABELS = [
    ("auc0-inf", ("auc0-inf", "auc0−inf", "auc(0-inf)", "aucinf", "auc0-∞")),
    ("auc0-tau", ("auc0-τ", "auc0-tau", "auctau", "auc0–τ", "auc0-τ,ss")),
    ("auc0-t", ("auc0-t", "auc(0-t)", "auc0–t")),
    ("auc", ("auc",)),
    ("cmax", ("cmax", "c max", "peak concentration")),
    ("cmin", ("cmin", "ctrough", "trough concentration")),
    ("tmax", ("tmax", "time to peak")),
    ("thalf", ("t½", "t1/2", "half-life", "half life", "terminal half")),
    ("clearance", ("cl/f", "cl f", "apparent clearance", "clearance")),
    ("volume", ("vz/f", "vss", "vd", "volume of distribution")),
    ("accumulation", ("accumulation ratio", "accumulation")),
    ("gmr", ("gmr", "geometric mean ratio", "ratio")),
    ("dose", ("dose", "mg once daily")),
    ("slope", ("slope",)),
]


def parameter_label(context: str) -> str | None:
    """Identify which PK parameter a number belongs to from nearby text.

    Scored by (end position, alias length): the nearest label to the number
    wins, and among labels ending at the same point the **longest** wins.

    That tie-break is load-bearing. Scoring by start position alone made
    "ratio" beat "accumulation ratio" inside the same phrase, so food-effect
    geometric mean ratios reconciled against an accumulation ratio and produced
    three false positives. Caught by running the fixture, not by review.
    """
    lowered = context.lower()
    best: tuple[int, int, str] | None = None
    for canonical, aliases in PARAMETER_LABELS:
        for alias in aliases:
            pos = lowered.rfind(alias)
            if pos == -1:
                continue
            score = (pos + len(alias), len(alias))
            if best is None or score > (best[0], best[1]):
                best = (score[0], score[1], canonical)
    return best[2] if best else None


@dataclass(frozen=True)
class Value:
    """One extracted number with everything needed to find it again."""

    raw: str
    number: Decimal
    unit: str | None
    document: str
    version: str
    locator: str
    context: str
    parameter: str | None = None

    def key(self) -> str:
        """Reconciliation key: the parameter, not the surrounding prose.

        Keying on raw context was a defect — a synopsis sentence and a table row
        describing the same quantity share no surrounding text, so nothing ever
        compared. Caught by running the engine against the synthetic fixture,
        which produced 27 extracted values and 1 comparison.
        """
        return f"{self.parameter or self.context}|{self.unit or ''}"


@dataclass
class Discrepancy:
    rule: str
    severity: str
    left: Value
    right: Value
    detail: str
    kind: str = "mechanical"

    def as_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "kind": self.kind,
            "statement_as_written": self.left.raw,
            "statement_locator": f"{self.left.document} v{self.left.version} {self.left.locator}",
            "expected_value_or_content": self.right.raw,
            "expected_locator": f"{self.right.document} v{self.right.version} {self.right.locator}",
            "detail": self.detail,
            "disposition": "open",
        }


@dataclass
class Register:
    """The consistency register. Both sides of every conflict survive."""

    values: list[Value] = field(default_factory=list)
    discrepancies: list[Discrepancy] = field(default_factory=list)
    compared: int = 0

    def add(self, value: Value) -> None:
        self.values.append(value)

    def summary(self) -> dict[str, object]:
        return {
            "values_extracted": len(self.values),
            "comparisons": self.compared,
            "discrepancies": len(self.discrepancies),
            "by_severity": {
                s: sum(1 for d in self.discrepancies if d.severity == s)
                for s in ("Critical", "Major", "Minor")
            },
        }


def extract(text: str, document: str, version: str, locator: str,
            context_window: int = 140) -> list[Value]:
    """Pull numbers with enough surrounding text to identify what they are.

    The window must reach the parameter label. At 48 characters it did not: in
    prose such as "Mean AUC0-tau at steady state in the 200 mg cohort was 412
    ng*h/mL" the label sits roughly 50 characters before its value, so the
    number was extracted unattributed and never reconciled. Measured recall of
    the script path was 0.50 until this was widened; the miss was invisible
    without the fixture.
    """
    out: list[Value] = []
    for m in NUMBER.finditer(text):
        raw = m.group(0).strip()
        try:
            number = Decimal(m.group("value").replace(",", ""))
        except InvalidOperation:
            continue
        start = max(0, m.start() - context_window)
        preceding = text[start:m.start()]
        if REFERENCE_PREFIX.search(preceding):
            continue  # a section, table or version reference, not a quantity
        context = re.sub(r"\s+", " ", preceding).strip().lower()[-context_window:]
        label = parameter_label(context)
        if label is None:
            continue  # an unattributable number cannot be reconciled against anything
        out.append(
            Value(raw=raw, number=number, unit=m.group("unit"),
                  document=document, version=version, locator=locator,
                  context=context, parameter=label)
        )
    return out


def within_tolerance(a: Decimal, b: Decimal, relative: Decimal = Decimal("0.005")) -> bool:
    """Default 0.5% absorbs legitimate rounding between a table and its prose.

    The tolerance actually applied should come from the study's own analysis
    plan when one is supplied — checking a document against generic expectations
    rather than its own pre-specified rules is how false positives are made.
    """
    if a == b:
        return True
    scale = max(abs(a), abs(b))
    return scale != 0 and abs(a - b) / scale <= relative


def reconcile(register: Register, left: list[Value], right: list[Value],
              severity: str = "Critical",
              relative_tolerance: Decimal = Decimal("0.005")) -> None:
    """Compare two value sets by context+unit key. Preserve every conflict."""
    index: dict[str, list[Value]] = {}
    for v in right:
        index.setdefault(v.key(), []).append(v)
    for lv in left:
        for rv in index.get(lv.key(), []):
            register.compared += 1
            if within_tolerance(lv.number, rv.number, relative_tolerance):
                continue
            register.discrepancies.append(
                Discrepancy(
                    rule="numeric-mismatch",
                    severity=severity,
                    left=lv,
                    right=rv,
                    detail=(
                        f"Values differ beyond the applied tolerance "
                        f"({relative_tolerance:%}). Both statements are recorded "
                        f"with their locators; which value is correct is a "
                        f"scientific judgment reserved for a qualified reviewer."
                    ),
                )
            )


def check_version_baseline(values: list[Value], baseline: dict[str, str],
                           register: Register) -> None:
    """Flag values inherited from a superseded document version.

    Reconciliation against a superseded output is the most damaging
    false-positive class in a review workflow: it produces confident findings
    that are entirely artefacts of stale inputs.
    """
    for v in values:
        register.compared += 1
        authoritative = baseline.get(v.document)
        if authoritative is not None and v.version != authoritative:
            register.discrepancies.append(
                Discrepancy(
                    rule="stale-version",
                    severity="Major",
                    left=v,
                    right=Value(raw=f"v{authoritative}", number=v.number, unit=v.unit,
                                document=v.document, version=authoritative,
                                locator="version baseline", context=v.context),
                    detail=(
                        f"Value taken from {v.document} v{v.version} while the "
                        f"declared authoritative version is v{authoritative}."
                    ),
                )
            )
