"""The canonical definition of this repository's public surface.

Single source of record. ``validate_repo.py`` and ``privacy_scan.py`` both import
from here; neither keeps its own copy.

Why this module exists
----------------------
Both scripts previously defined ``PUBLIC_ROOTS`` and ``PUBLIC_ROOT_FILES``
independently, and on 2026-08-05 they drifted: ``.gitleaks.toml`` was added to
the validator's allowlist but not the scanner's. The validator enumerated 213
files, the privacy scanner 212, and the file the two disagreed about was
therefore never privacy-scanned at all.

Both scripts still passed. A duplicated boundary does not announce that it has
drifted — it just protects slightly different things, and the gap is exactly the
size of whatever was added to one copy and not the other.

Enumeration policy (PS-D018)
----------------------------
The public surface is enumerated by **allowlist**, never by a recursive
filesystem walk filtered through a denylist. A denylist fails silently on
anything nobody thought to list; on 2026-08-04 that defect made the public
tooling read the private ``_ADMIN/`` control plane. For a repository whose
premise is a privacy boundary, the enumeration source *is* the boundary.

Author: ClinPharm AI contributors
Date: 2026-08-05
Dependencies: Python standard library only — these gates must run from a clean
checkout with nothing installed.
"""

from __future__ import annotations

from pathlib import Path

#: Directories that constitute the public product. Anything outside this set is
#: not part of the public surface and is never read, whether or not it exists.
PUBLIC_ROOTS: frozenset[str] = frozenset(
    {
        ".github",
        ".githooks",
        "benchmark",
        "catalog",
        "collections",
        "docs",
        "evals",
        "examples",
        "scripts",
        "shared",
        "site",
        "skills",
        "starter",
        "tests",
    }
)

#: Files permitted at the repository root.
PUBLIC_ROOT_FILES: frozenset[str] = frozenset(
    {
        ".editorconfig",
        ".gitattributes",
        ".gitignore",
        ".gitleaks.toml",
        "AGENTS.md",
        "CHANGELOG.md",
        "CITATION.cff",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "SUPPORT.md",
        "pyproject.toml",
        "requirements.lock",
    }
)


def allowlist_walk(root: Path, ignored_parts: set[str] | None = None) -> list[Path]:
    """Enumerate the public surface under ``root`` by allowlist.

    ``ignored_parts`` drops paths containing any of the given path components
    (``__pycache__`` and similar). It is a second filter on an already-bounded
    set, never the mechanism that defines the surface.
    """
    skip = ignored_parts or {"__pycache__"}
    found: list[Path] = []
    for name in sorted(PUBLIC_ROOT_FILES):
        candidate = root / name
        if candidate.is_file():
            found.append(candidate)
    for name in sorted(PUBLIC_ROOTS):
        base = root / name
        if not base.is_dir():
            continue
        found.extend(
            path
            for path in sorted(base.rglob("*"))
            if path.is_file() and not any(part in skip for part in path.parts)
        )
    return sorted(found)
