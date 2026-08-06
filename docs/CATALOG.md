# Catalog

> **Generated from `catalog/catalog.json`. Do not hand-edit.**

*Generated 2026-08-05.*

## What each status means

| Status | Meaning |
|---|---|
| `released` | package exists AND passed its qualification gate |
| `built` | package exists; qualification gate NOT passed — see evidence_gap |
| `planned` | no package |
| `held` | no package; risk or ownership gate |
| `deferred` | no package; outside the current programme |

**`released` and `built` both have a package on disk. Only `released` has passed
its qualification gate.** A `built` entry states exactly what is missing.

## Counts

| Status | Count |
|---|---:|
| built | 14 |
| released | 2 |
| **total** | **16** |

## Artifacts

### clinical-pharmacology

| ID | Title | Status | Evidence | Gap |
|---|---|---|---|---|
| [`review-csr-pk-consistency`](../skills/review-csr-pk-consistency/) | CSR PK Consistency Review | `released` | synthetic-benchmark-pending-run | — |
| [`assess-development-plan-gaps`](../skills/assess-development-plan-gaps/) | Development Plan Gap Assessment | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. The plan-gap / evidence-gap merge re… |
| [`map-agency-question-evidence`](../skills/map-agency-question-evidence/) | Agency Question Evidence Map | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. |
| [`prepare-briefing-package-content`](../skills/prepare-briefing-package-content/) | Briefing Package Content | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. |
| [`prepare-dose-justification-evidence`](../skills/prepare-dose-justification-evidence/) | Dose Justification Evidence | `built` | package-only-no-evaluation | No fixture or evals. RISK VETO recorded in the research scoring (62.5) — output sits on… |
| [`reconcile-cross-document-facts`](../skills/reconcile-cross-document-facts/) | Cross-Document Fact Reconciliation | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. T05 programme mode not exercised aga… |
| [`review-bioanalytical-report`](../skills/review-bioanalytical-report/) | Bioanalytical Report Review | `built` | package-only-no-evaluation | No fixture or evals. Tier C: the research withheld a card because the reviewable surfac… |
| [`review-ctd-272-content`](../skills/review-ctd-272-content/) | CTD 2.7.2 Content Review | `built` | package-only-no-evaluation | No fixture or evals. OWNERSHIP GATE open: 2.7.2 authorship is a practice convention ass… |
| [`review-ddi-evidence`](../skills/review-ddi-evidence/) | DDI Evidence Review | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. M12 decision-tree checker not implem… |
| [`review-fih-dose-rationale`](../skills/review-fih-dose-rationale/) | FIH Dose Rationale Review | `built` | package-only-no-evaluation | No fixture or evals. HIGHER-RISK, dose-adjacent. Hardened review gate not validated wit… |
| [`review-model-analysis-deliverable`](../skills/review-model-analysis-deliverable/) | Model Analysis Deliverable Review | `built` | package-only-no-evaluation | No fixture or evals. Tier C: proposed for PHARMACOMETRICS primary ownership; collection… |
| [`review-protocol-pk-sections`](../skills/review-protocol-pk-sections/) | Protocol PK Section Review | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. Activation separation against review… |
| [`review-study-conduct-pk`](../skills/review-study-conduct-pk/) | Study Conduct PK Review | `built` | package-only-no-evaluation | No fixture or evals. RISK VETO recorded in the research scoring (55.0), the lowest-scor… |
| [`review-uspi-section-12-content`](../skills/review-uspi-section-12-content/) | USPI Section 12 Content Review | `built` | package-only-no-evaluation | No fixture or evals. LEGALLY SENSITIVE: label text is binding. Review-only contract not… |
| [`verify-nca-outputs`](../skills/verify-nca-outputs/) | NCA Output Verification | `built` | package-only-no-evaluation | No synthetic fixture, eval suite or benchmark run. Activation separation against review… |

### utilities

| ID | Title | Status | Evidence | Gap |
|---|---|---|---|---|
| [`build-work-context`](../skills/build-work-context/) | Pharma Work Context | `released` | synthetic-example-and-eval-suite | — |

