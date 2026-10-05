# Laboratory 5 — Peer Review Findings

**Reviewing team:** Team 16 (Tsala Market)
**Reviewed team:** _[fill in team number/name]_
**Reviewed team's project:** _[fill in project title]_
**Date of review:** _[fill in]_
**Artefacts reviewed:** _[list what the other team actually gave you access to — e.g. requirements.md, use-case-model.*, sequence-core-use-case.*, phase1-draft.pdf, etc.]_

This review is conducted against the CSI473 Phase 1 rubric (5 criteria, 2 marks each). For each criterion below: read the guidance, check the reviewed team's artefacts against it, record what you actually found, and give an honest rating. Be specific — "looks fine" is not a finding a team can act on.

---

## 1. Purpose and traceability
*What earns full credit: the artefact is linked to a named requirement, use case, scenario or quality concern in the team project.*

**What to check:** Pick 3–4 artefacts at random (a business rule, a CRC card, a diagram message). Can you trace each one back to a specific requirement or use-case ID without guessing? Or does it float free of any named justification?

**Findings:**
_[fill in — e.g. "BR-04 cites FR-05 correctly, but CRC-03's third responsibility has no FR/UC reference at all"]_

**Rating:** ☐ Full credit ☐ Partial ☐ Not met

---

## 2. Technical correctness
*What earns full credit: notation and content are appropriate, complete enough and internally valid.*

**What to check:** Does the use-case diagram use correct UML notation (actors, system boundary, include/extend used correctly rather than decoratively)? Do sequence diagram messages make sense given the lifelines shown? Are business rules stated as testable invariants rather than vague goals?

**Findings:**
_[fill in]_

**Rating:** ☐ Full credit ☐ Partial ☐ Not met

---

## 3. Design rationale
*What earns full credit: the team explains the choice, a realistic alternative and the consequence accepted.*

**What to check:** Pick one non-trivial design decision (a CRC responsibility allocation, a business-rule threshold, a diagram structure choice). Did the team say *why* they chose it, what the alternative was, and what trade-off they accepted — or did they just state the decision with no reasoning?

**Findings:**
_[fill in]_

**Rating:** ☐ Full credit ☐ Partial ☐ Not met

---

## 4. Consistency
*What earns full credit: names, responsibilities and decisions agree with related artefacts in the same project.*

**What to check:** Pick one class/entity name and grep for it across their requirements, CRC cards, and diagrams. Does it mean the same thing everywhere, with the same responsibilities? Look specifically for the kind of drift we found in our own Gap 1–3 (Section 7.3 of our Phase 1 draft): a class used on one diagram but undocumented elsewhere, or a rule asserted in one place with no matching model anywhere else.

**Findings:**
_[fill in]_

**Rating:** ☐ Full credit ☐ Partial ☐ Not met

---

## 5. Evidence and revision
*What earns full credit: editable source, readable export, meaningful commit and a visible revision after critique are present.*

**What to check:** For each diagram, is there an editable source file (not just a screenshot or an image with no origin)? Is there a commit history showing the artefact was revised after being reviewed, not just created once and left?

**Findings:**
_[fill in]_

**Rating:** ☐ Full credit ☐ Partial ☐ Not met

---

## Overall summary

**Strongest aspect of their Phase 1 draft:**
_[fill in]_

**Single most important issue found** *(this is what you'd tell them to fix first if they could only fix one thing)*:
_[fill in]_

**Given back to the reviewed team?** ☐ Yes, shared verbally/in writing ☐ Not yet

---

## What this review changed in our own project

The Lab 5 studio plan asks you to revise one high-risk inconsistency in the 110–120 min block. Use this space to note whether reviewing another team's work made you look again at something in your own Phase 1 draft (`submissions/phase1-draft.pdf`) — a category of problem you spotted in theirs that might also apply to yours.

_[fill in — e.g. "Reviewing Team X's use-case model, where an actor appeared on the diagram but not in their stakeholder table, made us re-check ours: FairPriceCheckQuery has the equivalent problem (Gap 1 in our own consistency-matrix.md) — already flagged and scheduled for the same revision pass."]_

---

*Commit this file to `evidence/lab-05-review.md` on the `lab-05` branch, alongside a visible revision commit addressing the exit-record inconsistency (see Section 7.3 / Section 15 of `phase1-draft.pdf` for our own tracked issue, Gap 3).*
