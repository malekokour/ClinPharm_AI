# ClinPharm AI

**Open, evidence-led AI workflows for Clinical Pharmacology and Pharmacometrics.**

[![Quality](https://github.com/malekokour/ClinPharm_AI/actions/workflows/quality.yml/badge.svg)](https://github.com/malekokour/ClinPharm_AI/actions/workflows/quality.yml)
[![Release](https://img.shields.io/github/v/release/malekokour/ClinPharm_AI?display_name=tag)](https://github.com/malekokour/ClinPharm_AI/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-0B7A75.svg)](LICENSE)

Portable Agent Skills for quantitative drug development. Each performs one
bounded workflow — check a study report's PK content against its sources,
reconcile values across a document thread, structure a DDI evidence package —
and returns something a qualified clinical pharmacologist can act on.

**Every skill reviews, reconciles, verifies, structures and flags. Qualified
humans decide, approve, sign off and submit.** No skill edits your documents,
reruns an analysis, decides which of two conflicting values is correct, or
selects a dose. That boundary is the product, not a disclaimer.

## Start in 60 seconds

| I want to… | Skill | Route |
|---|---|---|
| Check a study report's PK content against its sources | `review-csr-pk-consistency` | [starter](starter/review-csr-pk-consistency/) · [skill](skills/review-csr-pk-consistency/SKILL.md) |
| Give an AI my working context before I start | `build-work-context` | [starter](starter/build-work-context/) · [skill](skills/build-work-context/SKILL.md) |

**Ordinary chat** — download the starter, attach it with your documents, say what
you want. No install, no terminal. The starter states on its own page that it
cannot run the deterministic checks.

**Skill-aware host** — download the release ZIP and extract into your skills
directory. It extracts to `<skill-id>/` and carries its own `LICENSE`, so it
works from extraction alone.

## The catalog, and what its statuses mean

[**docs/CATALOG.md**](docs/CATALOG.md) lists every workflow, generated from
[`catalog/catalog.json`](catalog/catalog.json).

**Two of sixteen packages are `released`.** The other fourteen are `built` — the
package exists and is complete, but it has **not** passed its qualification gate,
and each states exactly what evidence is missing. A `planned` or `held` candidate
has no directory at all.

That distinction is deliberate. A catalog that presents unevaluated packages as
ready is the failure this structure exists to prevent.

Collections: [Clinical Pharmacology](collections/clinical-pharmacology/) ·
[Utilities](collections/utilities/) · Pharmacometrics *(research in progress)*

## How a skill is evaluated

Against a synthetic fixture with **expert-keyed planted defects**, across four
proof layers: activation, execution, safety, portability.

The first published result is the hero's deterministic path —
[6/6 recall, 0 false positives](benchmark/review-csr-pk-consistency/results/2026-08-05-script-path.md),
with a reproduce command. Reaching it exposed four real defects in the tooling,
two of which had been reporting *clean* on a document containing planted Critical
defects.

**A synthetic benchmark is not clinical validation, not a GxP qualification, and
not evidence of real-world performance.** Where a benchmark has not run, the
catalog says so rather than staying silent.

## Also here

[`catalog/awesome-pharma-ai.md`](catalog/awesome-pharma-ai.md) — a curated index
of open resources for AI in pharmaceutical R&D, including projects that compete
with this one, annotated with licence and whether they ship evaluation
artifacts. Those two properties decide whether you can trust a skill you did not
write.

> [!IMPORTANT]
> Use only information permitted in your current AI environment. Never upload
> patient-level data, credentials, sponsor-confidential material, regulatory
> submission drafts, or employer-proprietary content to an unapproved service.

## Repository map

```text
catalog/       cross-artifact registry + a curated index of the wider field
collections/   domain catalogs — navigation only, never a skill body
skills/        flat, independently installable packages
shared/        canonical contracts, deterministic tools, study-type modules
starter/       generated Markdown + DOCX chat routes, one per skill
examples/ evals/ benchmark/ tests/    proof material, kept out of the install
scripts/ docs/ site/                  build tooling, documentation, Pages source
```

Two independent axes — artifact type and domain — joined by `catalog.json`.
Adding a collection or a new artifact type is append-only and restructures
nothing.

## Status

`v0.1.0`. Sixteen packages: **2 released**, 14 `built` with their evidence gaps
stated. Pharmacometrics research is in progress; Translational Medicine is
preserved as research and has no public collection.

This is early software. Read [docs/CATALOG.md](docs/CATALOG.md) before relying
on any package, and treat every output as a draft for qualified human review.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) ·
[Architecture](docs/ARCHITECTURE.md) · [Privacy](docs/PRIVACY.md) ·
[Compatibility](docs/COMPATIBILITY.md) · [Roadmap](docs/ROADMAP.md)

A skill is accepted only with a stated workflow, artifact-exact inputs, an
explicit human-review boundary, a synthetic fixture with planted defects, and an
evaluation rubric. Breadth without evidence is the thing this library exists to
avoid.

## License

MIT — see [LICENSE](LICENSE). Cite via [CITATION.cff](CITATION.cff).

## Important boundary

These skills support qualified professionals. They do not replace clinical
pharmacology, pharmacometrics, medical, regulatory, or quality judgment, and
nothing here is validated for GxP use or for patient-specific decisions.
