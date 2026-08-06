---
module: oncology-dose-optimization
version: "1.0"
owner: Malek Okour
reviewed: "2026-08-05"
anchors: [fda-optimus, fda-exposure-response, ich-e4]
consumers: [prepare-dose-justification-evidence, assess-development-plan-gaps, review-protocol-pk-sections, review-csr-pk-consistency, review-ctd-272-content]
---

# Study-type module — oncology dose optimization

Reference content only. The workflow that consumes this module is unchanged by
it; only the criteria change.

## Anchor status — read before applying

`fda-optimus` is carried in the guidance index as **final, 2024-08**, but that
row is `research-sourced` and has **not** been re-verified against FDA's own
page. Verify it in pipeline stage 1 before this module is treated as frozen.

Consequence: every criterion below is stated as an **expected element**, never as
quoted requirement. No section number and no numeric threshold from the guidance
is reproduced, because none was verified against the primary text.

## Design conventions to check

- **Dosage selection rests on a randomised parallel comparison**, not on
  escalation to the highest tolerated dose alone. A single dosage carried
  forward from escalation, with no randomised comparison and no stated
  justification for its absence, is a findable absence. UNVERIFIED: the
  guidance's own wording on the minimum number of dosages is not reproduced
  here — verify before citing a count.
- **The dosages compared are named** with their schedules and allocation.
- **Sample size stated with its purpose** — characterising dose-response versus
  powering a superiority test. PROVISIONAL: practice convention, not regulation.
- **Safety follow-up extends beyond the escalation DLT window**, period stated.
  Longer-term and low-grade toxicity, dose modification, interruption and
  discontinuation are expected inputs, so absence is checkable.
- **Exposure metric pre-specified** (Cmax, Ctrough, AUC over a stated interval)
  rather than chosen after the analysis, and **PK sampling adequate to derive
  it** — a trough-based analysis needs pre-dose samples on the stated days.
- **Exposure-response pre-specified for both efficacy and safety**, each naming
  its endpoint and its exposure metric.
- **Tolerability or patient-reported collection described** where it is cited as
  supporting the selected dosage.

## Expected statements in a report

| Element | Expected form |
|---|---|
| Dosages compared | Each named, with schedule and randomised allocation |
| Exposure by dosage | Summary exposure statistic per arm, with dispersion |
| E-R, efficacy | Endpoint named, exposure metric named, supporting statistic |
| E-R, safety | Endpoint named, exposure metric named, supporting statistic |
| Tolerability over time | Modification, interruption, discontinuation per arm |
| Selected dosage | Stated explicitly, with the arm it corresponds to |
| Basis for selection | Which analyses are claimed to support the selection |

## Mechanical checks this module enables

1. **The selected dosage is one of the dosages actually studied.** A selected
   dosage or schedule absent from the arm list is a contradiction.
2. **Every arm named in the design appears in the results** — present in methods,
   absent from exposure or outcome tables is a missing element.
3. **Exposure orders with dose where the report claims it does.** Delegated to
   T03; a mismatch is a numeric inconsistency between two reported values, not
   evidence either is wrong.
4. **The E-R exposure metric matches the metric defined in the methods.** A
   methods-defined AUC with a trough-based E-R result is a mismatch.
5. **Both E-R directions present** — efficacy and safety — or the absence stated.
6. **Dosage agrees across report, protocol and labelling or CTD summary**,
   including schedule and modification rules. Delegated to T05.
7. **Denominators reconcile**: per-arm N in the exposure table, the E-R analysis
   population and the safety table match, or the difference is stated.
8. **Any "optimised" or "supported by exposure-response" claim names an
   analysis.** A bare claim with no reference is unsupported.

## Boundaries

This module does not decide which dosage is correct, does not select or adjust a
dosage, and does not judge whether an exposure-response relationship is
clinically meaningful, flat, or adequately characterised. It does not assess
benefit-risk, does not judge whether a comparison was adequately sized, and makes
no regulatory commitment about Optimus sufficiency — a programme can satisfy
every check here and still be judged inadequate, and the reverse. It supplies
criteria; a qualified reviewer applies judgment.
