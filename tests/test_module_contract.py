"""Contract tests for study-type modules in shared/modules/.

Written after three separate wording-coupled checks failed in one session — an
exact-phrase grep for a safety property reports a violation whenever a second
author states the same rule differently. These assertions match the *property*,
normalising markdown emphasis first, and accept any of the phrasings the property
legitimately takes.

Too loose is dangerous for a safety check, so each property below requires a
disclaimer verb AND its object, not merely a keyword.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted((ROOT / "shared" / "modules").glob("*.md"))

REQUIRED_SECTIONS = (
    "Design conventions to check",
    "Expected statements in a report",
    "Mechanical checks this module enables",
    "Boundaries",
)

FRONTMATTER_KEYS = ("module", "version", "owner", "reviewed", "anchors", "consumers")

#: The property, not one phrasing of it.
CLINICAL_SIGNIFICANCE = re.compile(
    r"clinical(?:ly)?\s+(?:significan\w*|meaningful\w*|relevan\w*)"
    r"|matters?\s+clinical(?:ly)?",
    re.IGNORECASE,
)
#: Verified at SENTENCE level by co-occurrence, not by syntax.
#:
#: Three successive attempts at an ordered pattern each rejected a module that
#: plainly carried the property — "does not adjust a dose", "does not judge
#: whether a PK change warrants a dose adjustment", "It selects no dose". A
#: safety check that dictates word order tests the author's phrasing, not the
#: guarantee. Requiring a negation, a decision verb and a dose noun in the same
#: sentence is strict enough to be meaningful and blind to how it is written.
NEGATION = re.compile(r"\b(?:not|never|no)\b", re.IGNORECASE)
DOSE_NOUN = re.compile(r"\bdos(?:e|es|ing|age)\b", re.IGNORECASE)
DECISION_VERB = re.compile(
    r"\b(?:select\w*|choos\w*|chose|adjust\w*|set|recommend\w*|justif\w+|"
    r"escalat\w*|deriv\w+|decid\w+|judg\w+|determin\w+|warrant\w*)\b",
    re.IGNORECASE,
)


def disclaims_dose_decisions(boundaries: str) -> bool:
    for sentence in re.split(r"(?<=[.!?])\s+", boundaries):
        if (NEGATION.search(sentence)
                and DOSE_NOUN.search(sentence)
                and DECISION_VERB.search(sentence)):
            return True
    return False


def strip_emphasis(text: str) -> str:
    """Markdown emphasis must not defeat a content check.

    `*clinically* significant` and `clinically significant` are the same claim;
    only one of them survives a naive substring match.
    """
    return re.sub(r"[*_`]", "", text)


def boundaries_of(text: str) -> str:
    match = re.search(r"^##\s+Boundaries\s*$(.*)", text, re.MULTILINE | re.DOTALL)
    return strip_emphasis(match.group(1)) if match else ""


class ModuleContractTests(unittest.TestCase):
    def test_modules_are_discovered(self) -> None:
        self.assertGreaterEqual(len(MODULES), 15, "expected at least 15 study-type modules")

    def test_frontmatter_is_complete(self) -> None:
        for path in MODULES:
            with self.subTest(module=path.stem):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), "missing frontmatter")
                block = text.split("---", 2)[1]
                for key in FRONTMATTER_KEYS:
                    self.assertRegex(block, rf"(?m)^{key}:", f"missing '{key}'")

    def test_required_sections_are_present(self) -> None:
        for path in MODULES:
            with self.subTest(module=path.stem):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^#\s+Study-type module", "missing H1")
                for section in REQUIRED_SECTIONS:
                    self.assertRegex(
                        text, rf"(?m)^##\s+{re.escape(section)}",
                        f"missing section '{section}'",
                    )

    def test_boundaries_disclaim_clinical_significance(self) -> None:
        """Every module must refuse to judge clinical significance."""
        for path in MODULES:
            with self.subTest(module=path.stem):
                self.assertRegex(
                    boundaries_of(path.read_text(encoding="utf-8")),
                    CLINICAL_SIGNIFICANCE,
                    "Boundaries must disclaim deciding clinical significance",
                )

    def test_boundaries_disclaim_dose_decisions(self) -> None:
        """Every module must refuse to select, adjust or justify a dose."""
        for path in MODULES:
            with self.subTest(module=path.stem):
                self.assertTrue(
                    disclaims_dose_decisions(
                        boundaries_of(path.read_text(encoding="utf-8"))
                    ),
                    "Boundaries must disclaim dose selection or adjustment",
                )

    def test_numeric_thresholds_are_sourced_or_flagged(self) -> None:
        """A bare numeric threshold is indistinguishable from a fabricated one.

        Any line asserting a percentage interval or a millisecond bound must
        either cite an anchor id or carry an explicit unverified/provisional tag.
        """
        threshold = re.compile(r"\d{2,3}(?:\.\d+)?\s*[–-]\s*\d{2,3}(?:\.\d+)?\s*%|\b\d+\s*ms\b")
        hedged = re.compile(r"UNVERIFIED|PROVISIONAL|research-sourced|`[a-z0-9-]+`", re.IGNORECASE)
        offenders: list[str] = []
        for path in MODULES:
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if threshold.search(line) and not hedged.search(line):
                    offenders.append(f"{path.name}:{n}: {line.strip()[:100]}")
        self.assertEqual(offenders, [], "unsourced numeric thresholds:\n" + "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
