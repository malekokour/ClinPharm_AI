---
module: drug-drug-interaction
version: "1.0"
owner: Malek Okour
reviewed: "2026-08-05"
anchors: [ich-m12, fda-labeling-cp]
consumers: [review-ddi-evidence, review-csr-pk-consistency, review-protocol-pk-sections, review-uspi-section-12-content, review-ctd-272-content, assess-development-plan-gaps, reconcile-cross-document-facts]
---

# Study-type module — drug-drug interaction

Reference content only. The workflow that consumes this module is unchanged by
it; only the criteria change.

Every DDI statement is either **perpetrator** (this drug changes another's
exposure) or **victim** (another changes this drug's). A ratio reported without
a named substrate cannot be checked at all — role assignment is the first check.

## Numeric cutoffs — read before using

`ich-m12` is Step 4, dated 2024-05 in `guidance-index`, on a **research-sourced**
row not independently re-verified. The basic-model cutoffs in circulation — R1
(reversible inhibition), R1,gut (intestinal CYP3A), R2 (time-dependent
inhibition), R3 (induction), and the transporter ratio cutoffs — are
**PROVISIONAL here**: widely applied and largely harmonised with prior FDA
in-vitro DDI practice, but deliberately **not** hardcoded in this module. A
stage-1 verification must transcribe them, and the strong / moderate / weak
magnitude bands, from the current M12 text before any numeric check below runs.
**UNVERIFIED:** any cutoff or band not read from that text at review time.

## Design conventions to check

- Perpetrator and victim roles stated explicitly for every arm.
- Index perpetrator or index substrate named, with dose and schedule.
- Dosing duration adequate for the mechanism claimed — a time-dependent
  inhibition or induction claim needs multiple-dose perpetrator administration.
- Sampling covers the interaction window; washout stated for crossover designs.
- Enzyme or transporter pathway under test named, not implied.
- Any model (PBPK or static) substituting for a clinical study identified as
  such, rather than the substitution left as a silent gap.
- Victim-side trigger pre-specified: fraction metabolised, with its source.

## Expected statements in a report

| Element | Expected form |
|---|---|
| Direction | Named perpetrator and named victim, per comparison |
| Comparison | Geometric mean ratio, with-perpetrator / alone |
| Precision | 90% confidence interval on the ratio |
| Parameters | Cmax and AUC at minimum, each with its own ratio and interval |
| In-vitro basis | Ki, IC50, or induction parameter, with the assay system named |
| Model output | Cutoff variable computed, with its inputs shown |
| Decision | In-vitro result carried to "study conducted" or "not conducted, with reason" |
| Management | What is done about it, or an explicit statement that no action follows |

## Mechanical checks this module enables

1. **Role assignment present and single-valued.** No named perpetrator, no named
   victim, or the same drug in both roles makes the comparison unreviewable.
2. **Direction versus ratio.** A stated "decreased exposure" alongside a ratio
   above 1.00 is a contradiction between two reported facts.
3. **Ratio recomputes** from the reported with-perpetrator and alone means, and
   the **CI brackets the point estimate** per parameter. Both delegated to T03.
4. **Cutoff variable recomputes** from its own stated inputs; arithmetic only,
   delegated to T03. Its threshold comes from the verified M12 text, not here.
5. **In-vitro-to-clinical decision logic is closed.** Every reported in-vitro
   signal terminates in a clinical study, a modelling substitution, or a stated
   reason for neither; an open branch is a findable gap.
6. **Potency units and terms consistent** across in-vitro tables, model inputs
   and text — µM versus ng/mL, Ki versus IC50 used interchangeably.
7. **Magnitude label matches the reported ratio** — a classification whose ratio
   falls outside the guidance band for that label is a mismatch.
8. **Management statement present wherever an interaction is reported**, worded
   consistently across CSR, module 2.7.2 and label. Delegated to T05.
9. **Victim-side coverage accounted for** — where a fraction metabolised by a
   pathway is reported, a victim assessment is present or its absence explained.

## Boundaries

This module does not decide whether an interaction is clinically significant,
select or adjust a dose, or choose between contraindication, dose reduction and
monitoring. It does not validate a PBPK model, assess in-vitro assay quality,
judge whether a modelling substitution was adequate, or make any regulatory
commitment. It checks that reported facts agree and required elements are
present. A qualified reviewer supplies every judgment.
