#!/usr/bin/env python3
"""Validate the public ClinPharm AI repository contract.

Discovery-based: every released package under ``skills/*/SKILL.md`` is validated
by the same rules, and the collection catalogs under ``collections/*/collection.json``
are checked against what actually exists on disk.

``catalog/catalog.json`` joins the two axes (artifact kind x domain collection).
It is a derived view, not a second source of truth: every claim it makes is
re-derived from the collections and from disk, and any disagreement fails.

Enumeration policy (PS-D018)
----------------------------
The public surface is enumerated from ``git ls-files`` when a Git checkout is
available, and otherwise from an explicit **allowlist** of public roots. It is
never enumerated by a recursive filesystem walk filtered through a denylist.

A denylist fails silently on anything nobody thought to list. On 2026-08-04 that
defect made this gate read the private ``_ADMIN/`` control plane and fail on a
clean ``main``. For a repository whose premise is a privacy boundary, the
enumeration source *is* the boundary.

Author: ClinPharm AI contributors
Date: 2026-08-04
Dependencies: Python standard library only — this gate must run from a clean
checkout with nothing installed.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_surface as _surface

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

# --- public surface definition -------------------------------------------------

#: The public surface is defined once, in ``public_surface``. Importing rather
#: than restating it is what keeps this gate and the privacy scanner from
#: protecting subtly different sets of files.
PUBLIC_ROOTS = _surface.PUBLIC_ROOTS
PUBLIC_ROOT_FILES = _surface.PUBLIC_ROOT_FILES

#: Required regardless of which skills are released.
EXPECTED = [
    "AGENTS.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    ".github/workflows/quality.yml",
    ".github/workflows/pages.yml",
    ".github/workflows/release.yml",
    "docs/PRIVACY.md",
    "docs/COMPATIBILITY.md",
    "site/index.html",
    "site/sitemap.xml",
]

FORBIDDEN_SUFFIXES = {".csv", ".xpt", ".sas7bdat", ".xlsx", ".env", ".pem", ".key"}
FORBIDDEN_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:sk|ghp|github_pat)_[A-Za-z0-9_-]{20,}\b"),
]
TEXT_SUFFIXES = {".cff", ".json", ".md", ".py", ".toml", ".xml", ".yaml", ".yml"}

#: 'released' means the package exists AND passed its qualification gate.
#: 'built' means the package exists and the gate has NOT been passed — a
#: distinction the vocabulary originally lacked, which forced a choice between
#: overclaiming and a red gate. Only 'released' and 'built' may have a directory;
#: only 'released' is offered to users as ready.
VALID_STATUSES = {"released", "built", "planned", "held", "deferred", "excluded"}

#: Populated during catalog validation so the PASS line can state what is
#: actually released rather than counting every package on disk as released.
STATUS_TALLY: dict[str, int] = {}
DIRECTORY_ALLOWED = {"released", "built"}
SKILL_LINE_LIMIT = 500
MAX_FILE_BYTES = 10_000_000


def fail(message: str) -> None:
    ERRORS.append(message)


# --- enumeration ---------------------------------------------------------------


def _git(*args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), *args], capture_output=True, check=False
        )
    except (OSError, ValueError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.decode("utf-8")


def _git_tracked() -> list[Path] | None:
    """Return tracked files, or None when ROOT is not itself a Git checkout.

    ``git -C <dir>`` walks upward until it finds a repository. If this tree is
    merely nested inside an unrelated outer repository, that search succeeds and
    ``ls-files`` returns an empty list — which would enumerate zero public files
    and pass every check vacuously. Requiring the toplevel to equal ROOT is what
    makes the fallback trigger correctly instead.
    """
    toplevel = _git("rev-parse", "--show-toplevel")
    if toplevel is None:
        return None
    if Path(toplevel.strip()).resolve() != ROOT.resolve():
        return None
    output = _git("ls-files", "-z")
    if output is None:
        return None
    return [ROOT / n for n in output.split("\0") if n]


def _allowlist_walk() -> list[Path]:
    """Enumerate the public surface without Git, using the shared allowlist."""
    return _surface.allowlist_walk(ROOT)


def public_files() -> list[Path]:
    tracked = _git_tracked()
    if tracked is not None:
        return [p for p in tracked if p.is_file()]
    return _allowlist_walk()


def check_enumeration_boundary(files: list[Path]) -> None:
    """No enumerated file may sit outside the declared public surface."""
    for path in files:
        try:
            relative = path.relative_to(ROOT)
        except ValueError:
            fail(f"enumerated file outside repository root: {path}")
            continue
        top = relative.parts[0]
        if len(relative.parts) == 1:
            if top not in PUBLIC_ROOT_FILES:
                fail(f"unexpected root-level public file: {relative}")
        elif top not in PUBLIC_ROOTS:
            fail(f"file outside the declared public surface: {relative}")


# --- skill discovery -----------------------------------------------------------


def discover_skills() -> list[Path]:
    base = ROOT / "skills"
    if not base.is_dir():
        return []
    return sorted(p.parent for p in base.glob("*/SKILL.md"))


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    result: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


#: Present on disk during development, deliberately outside the public surface.
#: Listed so the stray-entry check below reports genuine surprises only.
KNOWN_NON_PUBLIC = {".git", ".gitleaks-report.json", "_qa", "dist", ".venv", ".ruff_cache", "__pycache__", ".DS_Store"}


def check_no_stray_root_entries() -> None:
    """Flag anything at the repository root that the allowlist does not cover.

    The allowlist makes unlisted files *invisible*, which is safe — they are
    never enumerated, so they cannot be published by these tools. But invisible
    is not the same as known, and silence here is dangerous in one specific way:
    a legitimate new public file that nobody added to the allowlist is skipped by
    both this validator and the privacy scanner, while still being perfectly
    committable by hand. It would reach a release having never been scanned.

    So the allowlist governs what is *read*, and this check reports what exists
    but is not covered. Enumeration stays closed; discovery stays loud.
    """
    for entry in sorted(ROOT.iterdir()):
        name = entry.name
        if name in KNOWN_NON_PUBLIC:
            continue
        if entry.is_dir():
            if name not in PUBLIC_ROOTS:
                fail(f"unlisted directory at repository root: {name}/ — add it to public_surface.PUBLIC_ROOTS or move it outside the repo")
        elif name not in PUBLIC_ROOT_FILES:
            fail(f"unlisted file at repository root: {name} — add it to public_surface.PUBLIC_ROOT_FILES or remove it")


def check_skills(skill_dirs: list[Path]) -> None:
    if not skill_dirs:
        fail("no released skill found: expected at least one skills/*/SKILL.md")
        return
    for directory in skill_dirs:
        skill_id = directory.name
        path = directory / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)

        name = frontmatter.get("name")
        if name != skill_id:
            fail(f"{skill_id}: SKILL.md name '{name}' must equal its directory name")

        description = frontmatter.get("description", "")
        if len(description) < 80:
            fail(f"{skill_id}: SKILL.md description must state capability and trigger")
        if "Use this skill" not in description and "Use when" not in description:
            fail(f"{skill_id}: SKILL.md description must state an activation condition")

        line_count = len(text.splitlines())
        if line_count > SKILL_LINE_LIMIT:
            fail(
                f"{skill_id}: SKILL.md is {line_count} lines, over the "
                f"{SKILL_LINE_LIMIT}-line progressive-disclosure limit"
            )

        if "RESTRICTED_DO_NOT_PROCESS" not in text:
            fail(f"{skill_id}: SKILL.md is missing restricted-data stop behavior")

        if not (directory / "README.md").is_file():
            fail(f"{skill_id}: package is missing README.md")

        for optional in ("references", "assets", "scripts"):
            candidate = directory / optional
            if candidate.is_dir() and not any(candidate.iterdir()):
                fail(f"{skill_id}: optional directory '{optional}/' exists but is empty")

        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1)
            if "://" in target or target.startswith("#"):
                continue
            if not (directory / target.split("#", 1)[0]).exists():
                fail(f"{skill_id}: broken SKILL.md link: {target}")


# --- catalog consistency -------------------------------------------------------


def load_collections() -> dict[str, dict]:
    base = ROOT / "collections"
    catalogs: dict[str, dict] = {}
    if not base.is_dir():
        return catalogs
    for path in sorted(base.glob("*/collection.json")):
        try:
            catalogs[path.parent.name] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid collection catalog {path.parent.name}: {exc}")
    return catalogs


def check_catalog(catalogs: dict[str, dict], skill_dirs: list[Path]) -> None:
    if not catalogs:
        fail("no collection catalog found: expected collections/*/collection.json")
        return

    on_disk = {d.name for d in skill_dirs}
    declared_released: dict[str, str] = {}
    STATUS_TALLY.clear()
    seen_ids: dict[str, str] = {}

    for directory, catalog in catalogs.items():
        if not (ROOT / "collections" / directory / "README.md").is_file():
            fail(f"collection {directory}: missing README.md")
        if catalog.get("collection") != directory:
            fail(
                f"collection {directory}: 'collection' field is "
                f"'{catalog.get('collection')}' but the directory is '{directory}'"
            )
        for entry in catalog.get("skills", []):
            skill_id = entry.get("id")
            status = entry.get("status")
            if not skill_id:
                fail(f"collection {directory}: catalog entry without an id")
                continue
            if status not in VALID_STATUSES:
                fail(f"{skill_id}: invalid catalog status '{status}'")
            if skill_id in seen_ids:
                fail(
                    f"{skill_id}: appears in two collections "
                    f"({seen_ids[skill_id]} and {directory}); a skill has exactly "
                    "one primary collection"
                )
            else:
                seen_ids[skill_id] = directory
            STATUS_TALLY[status] = STATUS_TALLY.get(status, 0) + 1
            if status in DIRECTORY_ALLOWED:
                declared_released[skill_id] = directory
                if status == "built" and not entry.get("evidence_gap"):
                    fail(f"{skill_id}: status 'built' requires an 'evidence_gap' "
                         f"stating what is missing before it can be released")
            elif skill_id in on_disk:
                fail(
                    f"{skill_id}: status is '{status}' but a package exists at "
                    f"skills/{skill_id}/ — only released candidates get a directory"
                )
            if status in {"held", "deferred"} and not (
                entry.get("hold_reason") or entry.get("defer_reason")
            ):
                fail(f"{skill_id}: status '{status}' requires a stated reason")

    for skill_id in sorted(declared_released):
        if skill_id not in on_disk:
            fail(
                f"{skill_id}: catalogued as released but no package exists at "
                f"skills/{skill_id}/"
            )
    for skill_id in sorted(on_disk):
        if skill_id not in declared_released:
            fail(
                f"{skill_id}: package exists but no collection catalogues it as "
                "released — orphan package"
            )


# --- remaining public checks ---------------------------------------------------


def check_root_catalog(catalogs: dict[str, dict], skill_dirs: list[Path]) -> None:
    """Validate ``catalog/catalog.json`` as a derived view, never as a second truth.

    The root catalog joins the two axes — artifact kind and domain collection —
    and is declared generated from ``collections/*/collection.json``. There is no
    generator script yet, so it is maintained by hand; that makes it exactly the
    kind of file that drifts silently while still looking authoritative.

    Every claim it makes is therefore re-derived here and compared. The
    collections remain the source of record; a disagreement always fails rather
    than being reconciled in favour of the catalog.
    """
    path = ROOT / "catalog" / "catalog.json"
    if not path.is_file():
        fail("missing catalog/catalog.json")
        return
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid catalog/catalog.json: {exc}")
        return

    artifacts = catalog.get("artifacts")
    if not isinstance(artifacts, list):
        fail("catalog/catalog.json: 'artifacts' must be a list")
        return

    # Re-derive status from the collections rather than trusting the catalog.
    declared: dict[str, str] = {}
    for collection in catalogs.values():
        for entry in collection.get("skills", []):
            ident = entry.get("id")
            if ident:
                declared[ident] = entry.get("status", "")
    if not declared:
        # A cross-check with an empty right-hand side passes vacuously and is
        # indistinguishable from a check that ran. Fail loudly instead.
        fail("catalog/catalog.json: no statuses derivable from collections — cross-check would be vacuous")

    on_disk = {d.name for d in skill_dirs}
    seen: set[str] = set()
    tally: dict[str, int] = {}

    for artifact in artifacts:
        ident = artifact.get("id")
        if not ident:
            fail("catalog/catalog.json: artifact missing 'id'")
            continue
        if ident in seen:
            fail(f"catalog/catalog.json: duplicate artifact id '{ident}'")
        seen.add(ident)

        status = artifact.get("status", "")
        tally[status] = tally.get(status, 0) + 1
        if status not in VALID_STATUSES:
            fail(f"catalog/catalog.json: '{ident}' has unknown status '{status}'")

        # 'built' means the package exists but the evaluation gate has NOT passed.
        # Without a stated gap the status silently reads as 'done' to a browser.
        if status == "built" and not artifact.get("evidence_gap"):
            fail(f"catalog/catalog.json: '{ident}' is 'built' but declares no evidence_gap")

        if status in DIRECTORY_ALLOWED and ident not in on_disk:
            fail(f"catalog/catalog.json: '{ident}' is '{status}' but no package on disk")

        # The collections are the source of record for status. This is the
        # invariant that stops a package being promoted to 'released' in the
        # browsable index without passing the gate that word claims.
        if ident not in declared:
            fail(f"catalog/catalog.json: '{ident}' appears in no collection")
        elif declared[ident] != status:
            fail(
                f"catalog/catalog.json: '{ident}' says '{status}' but its "
                f"collection says '{declared[ident]}'"
            )

        rel = artifact.get("path")
        if rel and not (ROOT / rel).exists():
            fail(f"catalog/catalog.json: '{ident}' points at missing path '{rel}'")

        primary = artifact.get("primary_collection")
        if primary and primary not in catalogs:
            fail(f"catalog/catalog.json: '{ident}' names unknown collection '{primary}'")

    for name in sorted(on_disk - seen):
        fail(f"catalog/catalog.json: package '{name}' on disk is absent from the catalog")

    # A counts block that is not re-derived is decoration.
    counts = catalog.get("counts")
    if isinstance(counts, dict):
        expected = {k: v for k, v in tally.items() if v}
        expected["total"] = len(artifacts)
        if {k: v for k, v in counts.items() if v} != expected:
            fail(f"catalog/catalog.json: counts {counts} do not match artifacts {expected}")


def check_expected() -> None:
    for relative in EXPECTED:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}")


def check_markdown_links(files: list[Path]) -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if "://" in target or target.startswith(("#", "mailto:")) or not target:
                continue
            file_target = target.split("#", 1)[0]
            if not file_target:
                continue
            if not (path.parent / file_target).resolve().exists():
                fail(
                    "broken local Markdown link: "
                    f"{path.relative_to(ROOT)} -> {raw_target}"
                )


def check_evals(catalogs: dict[str, dict], skill_dirs: list[Path]) -> None:
    """Every released skill needs an eval suite covering its declared modes."""
    declared_modes: dict[str, list[str]] = {}
    for catalog in catalogs.values():
        for entry in catalog.get("skills", []):
            if entry.get("status") == "released":
                declared_modes[entry["id"]] = entry.get("modes", [])

    for directory in skill_dirs:
        skill_id = directory.name
        candidates = [
            ROOT / "evals" / skill_id / "evals.json",
            ROOT / "evals" / "evals.json",
        ]
        path = next((c for c in candidates if c.is_file()), None)
        if path is None:
            fail(f"{skill_id}: no eval suite found under evals/")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{skill_id}: invalid evals JSON: {exc}")
            continue
        evals = payload.get("evals", [])
        if len(evals) < 7:
            fail(f"{skill_id}: eval suite must include at least seven cases")
        modes = {item.get("mode") for item in evals}
        for required in declared_modes.get(skill_id, []):
            if required not in modes:
                fail(f"{skill_id}: eval suite missing declared mode: {required}")
        for item in evals:
            if len(item.get("assertions", [])) < 3:
                fail(f"{skill_id}: eval {item.get('id')} needs three assertions")
            for input_path in item.get("inputs", []):
                if not (path.parent / input_path).resolve().is_file():
                    fail(
                        f"{skill_id}: eval {item.get('id')} has missing input: "
                        f"{input_path}"
                    )


def check_public_surface(files: list[Path]) -> None:
    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(f"forbidden public file type: {relative}")
        if path.stat().st_size > MAX_FILE_BYTES:
            fail(f"file exceeds 10 MB: {relative}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(text):
                    fail(f"possible secret in {relative}")


def check_template_defaults(skill_dirs: list[Path]) -> None:
    for directory in skill_dirs:
        for path in sorted((directory / "assets").glob("*.template.md")):
            text = path.read_text(encoding="utf-8")
            if (
                "data_classification:" in text
                and "data_classification: UNKNOWN" not in text
            ):
                fail(f"blank template must default to UNKNOWN: {path.relative_to(ROOT)}")


def check_action_pins() -> None:
    pattern = re.compile(r"^\s*(?:-\s+)?uses:\s+[^@\s]+@([^\s#]+)", re.MULTILINE)
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for reference in pattern.findall(text):
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                fail(
                    "GitHub Action must use a full commit SHA: "
                    f"{path.relative_to(ROOT)} -> {reference}"
                )


def check_docx(files: list[Path]) -> None:
    for path in files:
        if path.suffix.lower() != ".docx":
            continue
        try:
            with zipfile.ZipFile(path) as archive:
                if "word/document.xml" not in set(archive.namelist()):
                    fail(f"invalid DOCX: {path.relative_to(ROOT)}")
        except zipfile.BadZipFile:
            fail(f"corrupt DOCX: {path.relative_to(ROOT)}")


def main() -> int:
    files = public_files()
    source = "git ls-files" if _git_tracked() is not None else "public allowlist"
    skill_dirs = discover_skills()
    catalogs = load_collections()

    check_enumeration_boundary(files)
    check_no_stray_root_entries()
    check_expected()
    check_skills(skill_dirs)
    check_catalog(catalogs, skill_dirs)
    check_root_catalog(catalogs, skill_dirs)
    check_markdown_links(files)
    check_evals(catalogs, skill_dirs)
    check_public_surface(files)
    check_template_defaults(skill_dirs)
    check_action_pins()
    check_docx(files)

    if ERRORS:
        print(f"FAILED: {len(ERRORS)} repository contract error(s)")
        for error in ERRORS:
            print(f"- {error}")
        return 1

    released = STATUS_TALLY.get("released", 0)
    built = STATUS_TALLY.get("built", 0)
    print(
        f"PASS: repository contract validated across {len(files)} public files "
        f"(enumerated from {source}); {len(skill_dirs)} package(s) on disk — "
        f"{released} released, {built} built-but-unevaluated — "
        f"in {len(catalogs)} collection(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
