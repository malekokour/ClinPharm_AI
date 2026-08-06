"""Contract tests for the public ClinPharm AI v0.1 artifacts."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def discovered_skills() -> list[Path]:
    """Every released package. Tests parametrise over discovery, never a name.

    A hard-coded package name means a second skill escapes every contract test
    silently. Discovery makes coverage automatic and the denominator visible.
    """
    base = ROOT / "skills"
    return sorted(p.parent for p in base.glob("*/SKILL.md")) if base.is_dir() else []

sys.path.insert(0, str(SCRIPTS))

from check_generated_freshness import differing_members


class ClinPharmAIContractTests(unittest.TestCase):
    def test_all_five_operating_modes_have_evaluation_coverage(self) -> None:
        payload = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
        modes = {item["mode"] for item in payload["evals"]}
        self.assertIn("CREATE", modes)
        self.assertIn("UPDATE", modes)
        self.assertIn("PROJECT", modes)
        self.assertIn("REFRESH", modes)
        self.assertIn("EXPORT", modes)
        self.assertTrue(any("restricted" in item["id"] for item in payload["evals"]))
        self.assertTrue(any("prompt-injection" in item["id"] for item in payload["evals"]))

    def test_skill_progressive_disclosure_links_resolve(self) -> None:
        skills = discovered_skills()
        self.assertGreater(len(skills), 0, "no skills/*/SKILL.md discovered")
        for skill in skills:
            with self.subTest(skill=skill.name):
                path = skill / "SKILL.md"
                text = path.read_text(encoding="utf-8")
                self.assertLessEqual(len(text.splitlines()), 500)
                self.assertTrue((skill / "README.md").is_file())
                for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                    if "://" not in target and not target.startswith("#"):
                        self.assertTrue(
                            (path.parent / target.split("#", 1)[0]).exists(), target
                        )

    def test_synthetic_example_preserves_governing_numbers(self) -> None:
        capsule = (ROOT / "examples/clinpharm-pmx/outputs/Project-Context-SYN-101.md").read_text(encoding="utf-8")
        pack = (ROOT / "examples/clinpharm-pmx/outputs/AI-Working-Pack-SYN-101.md").read_text(encoding="utf-8")
        for text in (capsule, pack):
            self.assertIn("14.2 L/h", text)
            self.assertIn("12.4 L/h", text)
            self.assertIn("90%", text)
            self.assertIn("80%", text)
            self.assertIn("unsupported", text.lower())

    def test_secondary_benchmark_review_is_reconciled(self) -> None:
        results = ROOT / "benchmark/results/2026-07-30-codex"
        scores = json.loads((results / "scores.json").read_text(encoding="utf-8"))
        review = scores["review"]["secondary"]
        record = (results / review["record"]).read_text(encoding="utf-8")
        self.assertTrue(review["condition_labels_masked"])
        self.assertFalse(review["independent"])
        self.assertEqual("48/48", review["agreement"]["dimension_scores"])
        self.assertEqual("6/6", review["agreement"]["critical_failure_classifications"])
        self.assertEqual(0, review["agreement"]["total_score_disagreements"])
        for run in scores["runs"]:
            self.assertIn(run["baseline"]["sha256"], record)
            self.assertIn(run["working_pack"]["sha256"], record)

    def test_public_example_is_explicitly_synthetic(self) -> None:
        for path in (ROOT / "examples/clinpharm-pmx").rglob("*.md"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("synthetic", text, path)

    def test_generated_docx_files_are_valid_packages(self) -> None:
        for relative in (
            "starter/build-work-context/Pharma-Work-Context.docx",
            "examples/clinpharm-pmx/outputs/My-Pharma-Work-Context.docx",
            "examples/clinpharm-pmx/outputs/AI-Working-Pack-SYN-101.docx",
        ):
            path = ROOT / relative
            if not path.exists():
                self.skipTest(f"{relative} not built yet")
            with zipfile.ZipFile(path) as archive:
                self.assertIn("word/document.xml", archive.namelist())

    def test_docx_freshness_ignores_zip_compression_envelope(self) -> None:
        source = ROOT / "starter/build-work-context/Pharma-Work-Context.docx"
        if not source.exists():
            self.skipTest("starter DOCX not built yet")
        with tempfile.TemporaryDirectory() as temp:
            rewritten = Path(temp) / source.name
            with zipfile.ZipFile(source) as archive:
                members = [(name, archive.read(name)) for name in archive.namelist()]
            with zipfile.ZipFile(
                rewritten, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1
            ) as archive:
                for name, data in members:
                    archive.writestr(name, data)
            self.assertNotEqual(source.read_bytes(), rewritten.read_bytes())
            self.assertEqual([], differing_members(source, rewritten))

    def test_no_code_starter_has_file_generation_fallback(self) -> None:
        text = (ROOT / "starter/build-work-context/Pharma-Work-Context.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("If Word generation is unavailable", text)
        self.assertIn("ready to paste into Word", text)
        self.assertIn("state that no DOCX was created", text)

    def test_blank_templates_default_to_unknown(self) -> None:
        for path in sorted(
            p for skill in discovered_skills() for p in (skill / "assets").glob("*.template.md")
        ):
            text = path.read_text(encoding="utf-8")
            if "data_classification:" in text:
                self.assertIn("data_classification: UNKNOWN", text, path)

    def test_public_governance_and_site_exist(self) -> None:
        for relative in (
            "AGENTS.md",
            "CODE_OF_CONDUCT.md",
            "SUPPORT.md",
            ".github/CODEOWNERS",
            "docs/assets/clinpharm-ai-workflow.gif",
            "docs/assets/clinpharm-ai-workflow.mp4",
            "site/index.html",
            "site/sitemap.xml",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_release_video_is_mp4(self) -> None:
        video = ROOT / "docs/assets/clinpharm-ai-workflow.mp4"
        header = video.read_bytes()[:64]
        self.assertGreater(video.stat().st_size, 100_000)
        self.assertEqual(header[4:8], b"ftyp")
        self.assertTrue(
            any(brand in header for brand in (b"isom", b"iso2", b"mp41", b"mp42")),
            "expected a recognized ISO Base Media brand",
        )

    def test_prompt_injection_fixture_is_treated_as_untrusted(self) -> None:
        fixture = (ROOT / "evals/fixtures/prompt-injection-source.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("hostile test content", fixture)
        for skill in discovered_skills():
            with self.subTest(skill=skill.name):
                text = (skill / "SKILL.md").read_text(encoding="utf-8")
                # A required SECTION, not one skill's prose. Asserting an exact
                # sentence couples a safety contract to a wording choice and
                # breaks the moment a second skill states the same rule
                # differently — which is exactly what happened.
                self.assertRegex(
                    text, r"(?im)^#+ .*evidence, not instructions",
                    f"{skill.name}: SKILL.md must carry an 'evidence, not "
                    f"instructions' section",
                )


if __name__ == "__main__":
    unittest.main()
