#!/usr/bin/env python3
"""Verify that canonical Markdown content survives DOCX generation.

Author: ClinPharm AI contributors
Date: 2026-07-29
Dependencies: Python standard library
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PAIRS = (
    (
        ROOT / "starter/build-work-context/Pharma-Work-Context.md",
        ROOT / "starter/build-work-context/Pharma-Work-Context.docx",
    ),
    (
        ROOT / "examples/clinpharm-pmx/outputs/My-Pharma-Work-Context.md",
        ROOT / "examples/clinpharm-pmx/outputs/My-Pharma-Work-Context.docx",
    ),
    (
        ROOT / "examples/clinpharm-pmx/outputs/AI-Working-Pack-SYN-101.md",
        ROOT / "examples/clinpharm-pmx/outputs/AI-Working-Pack-SYN-101.docx",
    ),
)


def markdown_body(text: str) -> str:
    """Remove presentation-only Markdown syntax while retaining content."""
    if text.startswith("---\n"):
        _, _, text = text.partition("\n---\n")
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s*#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", text, flags=re.MULTILINE)
    text = text.replace("```markdown", "").replace("```", "")
    return text.translate(str.maketrans("", "", "`*~|"))


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    return " ".join(
        node.text or "" for node in root.iter(f"{{{WORD_NS}}}t")
    )


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[._/%<>-][A-Za-z0-9]+)*", text.casefold())


def missing_ordered_tokens(source: list[str], generated: list[str]) -> list[str]:
    cursor = 0
    missing: list[str] = []
    for token in source:
        while cursor < len(generated) and generated[cursor] != token:
            cursor += 1
        if cursor == len(generated):
            missing.append(token)
            if len(missing) == 8:
                break
        else:
            cursor += 1
    return missing


def main() -> int:
    failures: list[str] = []
    for source, generated in PAIRS:
        if not source.is_file() or not generated.is_file():
            failures.append(f"missing pair: {source.name} / {generated.name}")
            continue
        missing = missing_ordered_tokens(
            tokens(markdown_body(source.read_text(encoding="utf-8"))),
            tokens(docx_text(generated)),
        )
        if missing:
            failures.append(
                f"{generated.relative_to(ROOT)} lost or reordered tokens: "
                + ", ".join(missing)
            )
        else:
            print(f"PASS: {source.relative_to(ROOT)} -> {generated.relative_to(ROOT)}")
    if failures:
        print(f"FAILED: {len(failures)} Markdown/DOCX parity error(s)")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"PASS: Markdown/DOCX content parity verified for {len(PAIRS)} pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
