# Changelog

All notable changes to ClinPharm AI are documented here.

## [Unreleased]

Everything below is the initial content of this repository. Nothing has been
released yet; `v0.1.0` will be the first tag.

### Added

- **Sixteen skill packages** for clinical pharmacology document review.
  Two are `released` — `review-csr-pk-consistency` and `build-work-context`.
  Fourteen are `built`: the package exists and validates, but its evaluation has
  not been run, and each declares an explicit `evidence_gap`.
- **Six deterministic checkers** (T01–T06) with unit tests against cited sources,
  vendored into the packages that use them so each ZIP installs standalone.
- **Fifteen study-type modules** and six shared review assets.
- **An expert-keyed synthetic fixture** for the hero skill: 12 planted defects
  (5 Critical, 4 Major, 3 Minor) plus 5 documented false-positive traps.
- **Two-axis organisation** — artifact kind × domain collection — joined by
  `catalog/catalog.json`. The collections are the source of record; the catalog
  is a derived view, and CI fails when they disagree.
- Attach-first DOCX and Markdown starters, a static tracking-free site, and
  portable quality, privacy, benchmark-digest, and release checks.
- Public contribution, support, security, and governance documentation.

### Changed

- The privacy boundary is now **structural**: the Git root is a subdirectory of
  the working tree, so private material is a sibling of the repository rather
  than a child of it. No ignore rule is load-bearing for privacy.
- Enumeration is **allowlist-based** (`scripts/public_surface.py`), never a
  filesystem walk filtered by a denylist. A denylist fails silently on anything
  nobody thought to list.
- Repository validation is **discovery-based** over `skills/*/SKILL.md` rather
  than hard-coded to a single package.

### Note on version numbering

A `0.1.0` was released on 2026-07-30 under this project's predecessor, which had
a different name, a single skill, and a repository that no longer exists. That
history is preserved privately and is deliberately not carried forward here.
This repository starts from an empty history, and its `v0.1.0` is a different
artifact describing a different product. Nothing in this file refers to the
predecessor's release.
