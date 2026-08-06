---
module: biologics-mab-pk
version: "1.0"
owner: Malek Okour
reviewed: "2026-08-05"
anchors: [fda-poppk, ema-immunogenicity, fda-labeling-cp]
consumers: [review-csr-pk-consistency, verify-nca-outputs, review-protocol-pk-sections, review-uspi-section-12-content, assess-development-plan-gaps, prepare-dose-justification-evidence, review-ctd-272-content, reconcile-cross-document-facts]
---

# Study-type module — monoclonal antibody pharmacokinetics

Reference content only. The workflow that consumes this module is unchanged by
it; only the criteria change.

## Scope note on the anchors

`fda-poppk` is general and prescribes no mAb-specific criteria;
`ema-immunogenicity` covers the ADA side only. **Everything here concerning
target-mediated drug disposition, fixed versus weight-based dosing, and
subcutaneous bridging rests on practice convention, not a guidance requirement —
treat the whole of it as PROVISIONAL.** No FDA or EMA document dedicated to mAb
PK was verified for this module; if one is later confirmed, re-anchor.

## Design conventions to check

- Dose levels stated with their unit, consistent across protocol, CSR and label
  — `mg` for a fixed dose, `mg/kg` for weight-based. A "fixed" dose expressed in
  `mg/kg` is a contradiction.
- A weight-based-to-fixed switch stated with the study or timepoint at which it
  occurred, and its supporting bridging analysis identified.
- Sampling duration adequate for the terminal phase, stated in a time unit
  reconcilable with the reported half-life.
- Nonlinearity, where claimed, tied to a stated dose or concentration range. TMDD
  is one explanation among several — check the claim has a range and a supporting
  analysis, never which mechanism is right.
- Subcutaneous arms state injection site, volume, and presentation; an IV
  reference arm named wherever absolute bioavailability is reported.
- ADA sampling schedule pre-specified and aligned to the PK timepoints, so
  ADA-status subgroups can be formed at all.

## Expected statements in a report

| Element | Expected form |
|---|---|
| Dosing basis | Fixed (mg) or weight-based (mg/kg), stated once and used consistently |
| Exposure parameters | Cmax, Ctrough, AUC over a stated interval; Cmax,ss and AUCtau at steady state |
| Disposition parameters | CL (or CL/F for SC), Vz or Vss, t½, each with its unit |
| Nonlinearity | Explicit statement, with the dose or concentration range it applies to |
| SC versus IV | Bioavailability as a number, with the IV comparator arm named |
| SC bridging comparison | Geometric mean ratio with a 90% confidence interval, SC / IV or SC / SC |
| Immunogenicity | ADA incidence with numerator and denominator; NAb subset stated separately |
| ADA–PK interface | Exposure summarised by ADA status, with n per subgroup |
| Covariate effects | Effect size with a stated reference subject or covariate value |

## Mechanical checks this module enables

1. **Dosing-unit consistency** across protocol, CSR, CTD 2.7.2 and label.
   Delegated to T05.
2. **Weight-based dose recomputes** against the stated reference body weight
   where both the mg/kg dose and a converted mg dose appear. Delegated to T03.
3. **Accumulation versus half-life and dosing interval.** Delegated to T03; a
   deviation is an inconsistency, not proof either number is wrong.
4. **Bioavailability has a named IV comparator** and is a value, not an adjective.
5. **Bridging ratio and CI internally consistent** — the CI brackets the point
   estimate, and the stated direction matches the ratio. Delegated to T03.
6. **ADA denominators reconcile.** ADA-positive + ADA-negative = ADA-evaluable N;
   ADA-evaluable ≤ analysis population; NAb-positive ≤ ADA-positive.
7. **ADA subgroup n values** in the PK-by-ADA-status table match the incidence
   table. Delegated to T05 where the tables sit in different documents.
8. **Nonlinearity claim carries a range and a supporting analysis.** A bare
   "nonlinear PK consistent with TMDD" with neither is an unsupported claim.
9. **Unit and time-scale coherence** — half-life against sampling duration,
   clearance units against the dosing basis. Delegated to T03.
10. **Every parameter named in the label** carries the same value in the source
    CSR or population-PK report. Delegated to T05.

## Boundaries

This module does not decide whether nonlinearity is target-mediated, whether an
immunogenicity signal is clinically meaningful, or whether a subcutaneous
presentation is bridgeable to an intravenous one. It does not select between
fixed and weight-based dosing, set an exposure target, adjust a dose, or approve
a labelling claim. It supplies checkable criteria; a qualified reviewer applies
judgment. ADCs (see `fda-adc`), bispecifics, and cell therapies are out of scope
— their analyte and disposition conventions differ.
