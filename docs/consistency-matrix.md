# Consistency Matrix — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 5**
**Chain:** Use-case step → Sequence message(s) → Responsible class (CRC) → Business rule / lifecycle state → Requirement(s)
**Sources:** `UC-01-check-fair-price.md`, `sequence-core-use-case.mmd`, `crc-cards.md`, `business-rules.md`, `lifecycle-or-activity.mmd`, `requirements.md`

This matrix cross-checks that every step of the core use case is actually realised by a message on the sequence diagram, that message is owned by the class the CRC cards say owns it, and that ownership matches the invariant the business rules and lifecycle model claim — closing the loop back to the functional requirement(s) that motivated it in the first place.

## Core matrix

| UC-01 step | Sequence message(s) | Responsible class (CRC) | Business rule / lifecycle state | Requirement(s) |
|---|---|---|---|---|
| 1–2. Farmer selects "Check My Offer", picks commodity/district/grade | msgs #1–3 (`Select`, `Prompt`, `Commodity, district, grade`) | USSD/Web Interface (UI only, no domain class) | — | FR-01 |
| 3. Farmer enters offered price + unit | msgs #4–6 (`Offered price, unit`, `createQuery(...)`) | `FairPriceCheckQuery` (CRC not yet written — see gap below) | — | FR-01 |
| Unit validation | msg #7 `isRecognisedUnit(commodity, unit)?` → #8/#9 (rejected path) or #11 (accepted path) | `ConversionFactorTable` (CRC-04) | — | FR-02, FR-03 |
| — *(Alt. Flow A2)* Unrecognised unit rejected | msgs #8–10 (`rejected`, `error: unsupported unit...`) | `ConversionFactorTable` (CRC-04) | — | FR-03 |
| Price normalisation | msg #12 `normalise price to P/kg (BR-03)` | `PriceEntry` (CRC-01) | BR-03 | FR-02 |
| — *(Alt. Flow A1)* No grade declared | *not shown as a separate message — folded into query construction; see gap below* | `PriceEntry` (CRC-01) | BR-04 | FR-05 |
| 4. Retrieve reference value | msg #13 `getReferenceValue(...)` | `PriceBucket` (CRC-02) | — | FR-08 |
| **Important rule enforced**: pool only Verified, ≤30-day entries | msg #14 `pool Verified entries, last 30 days only (BR-05)` | `PriceBucket` (CRC-02) | BR-01 (status check), BR-05, lifecycle state **Verified → Eligible for pooling** | FR-07, FR-08 |
| Minimum-sample threshold check | msgs #15–16 (`getThresholds`, `minSample=5, minSubmitters=2`) | `PriceBucket` (CRC-02) + `SystemConfiguration` (CRC-06) | BR-06 | FR-09, FR-17 |
| — *(Alt. Flow A3)* Bucket under threshold → fallback | msgs #17–20 (`apply fallback...`, `insufficient data...`) | `PriceBucket` (CRC-02) | BR-06 | FR-09 |
| Outlier exclusion | msgs #21, #24 (`exclude entries beyond 1.5x IQR (BR-07)`) | `PriceBucket` (CRC-02) | BR-07, lifecycle end state **Excluded from calculation** | FR-10 |
| 5. Calculate reference price | msgs #22, #25 (`reference price = median(...) (BR-08)`) | `PriceBucket` (CRC-02) | BR-08, lifecycle end state **Contributes to a result** | FR-08 |
| 6. Build result | msg #27 `build(offeredPrice, referencePrice, sampleData)` | `FairPriceCheckResult` (CRC-03) | — | FR-11, FR-12, FR-13 |
| 6. Classify fairness flag | msgs #28–30 (`getFairnessThresholds()`, `classify fairness flag (BR-09, FR-11)`) | `FairPriceCheckResult` (CRC-03) + `SystemConfiguration` (CRC-06) | BR-09 | FR-11, FR-17 |
| 6. Assign confidence label | msg #31 | `FairPriceCheckResult` (CRC-03) | — | FR-12 |
| 6. Attach disclaimer | msg #32 `attach indicative-guidance disclaimer (BR-10, FR-13)` | `FairPriceCheckResult` (CRC-03) | BR-10 | FR-13 |
| 6. Log anonymised query | msg #34 `logAnonymisedQuery(...)` | `FairPriceCheckQuery` (CRC not yet written) | BR-11 (district-level only) | FR-15 |
| 7. Farmer decides (accept/negotiate/seek buyer) | msgs #35–36 (`Display result + disclaimer`) | — (farmer action, no system responsibility) | — | — |
| 8. *(Alt. Flow A3, no bucket qualifies)* | msgs #18–20 | `PriceBucket` (CRC-02) | BR-06 | FR-09 |

## Gaps and contradictions identified

Cross-checking the five artefacts surfaced three inconsistencies. None are severe, but all three should be resolved before the Phase 1 report is finalised.

### 1. `FairPriceCheckQuery` is used on the sequence diagram but has no CRC card
The sequence diagram gives `FairPriceCheckQuery` real responsibilities — constructing itself from farmer input (msg #6), coordinating the calls to `ConversionFactorTable` and `PriceBucket`, and logging the anonymised query (msg #34) — but `crc-cards.md` only documents six classes and does not include it. Right now the coordinating logic in msgs #6–#34 has no documented owner.
**Resolution needed:** add a seventh CRC card for `FairPriceCheckQuery` before the domain model is finalised, or explicitly fold its responsibilities into `PriceEntry`/`PriceBucket` and remove it from the sequence diagram — but not leave it undocumented in one artefact and load-bearing in another.

### 2. Alternative Flow A1 (ungraded submission) has no matching sequence message
`UC-01-check-fair-price.md` Alt. Flow A1 and `business-rules.md` BR-04 both describe the ungraded-defaults-to-Grade-B behaviour, and it is fully modelled in `lifecycle-or-activity.mmd` (the `GradeCheck` decision). But the sequence diagram jumps straight from `createQuery(...)` to unit validation — there is no message showing the grade-default decision happening during a Fair Price Check *lookup* (as opposed to a *submission*, where the lifecycle diagram places it).
**Resolution needed:** clarify whether Grade defaulting only happens at **submission** time (per the lifecycle diagram, on `PriceEntry` creation) or also needs to happen at **lookup** time (per UC-01 Alt. Flow A1, when a farmer doesn't select a grade to check against). These are two different moments and the artefacts currently conflate them. The likely fix is to rename UC-01's Alt. Flow A1 to be about the farmer's *lookup* grade defaulting to B for comparison purposes, distinct from BR-04's *submission-time* default — and add the missing sequence message once that's settled.

### 3. BR-02's "downgrade" path is asserted but never modelled anywhere
`business-rules.md` BR-02 states "a Verified entry is never automatically reverted... only a System Admin action can downgrade it" — but:
- `requirements.md` has no FR describing an Admin downgrade action (FR-16 only covers verify/reject/correct grade or market-level tag, not reverting verification status).
- `lifecycle-or-activity.mmd` has no transition arrow from the `Verified` state back to `Community-reported` or any other state.
- `crc-cards.md` CRC-01 (`PriceEntry`) says it "reports itself to an `AuditLogRecord`" on status changes but does not list downgrade as one of its responsibilities.

This is a genuine contradiction between what the business rule asserts is possible and what every other artefact models as possible.
**Resolution needed:** either (a) add an explicit FR and a lifecycle transition for Admin-initiated downgrade, or (b) narrow BR-02's wording to remove the downgrade claim if it was aspirational rather than intended for this vertical slice. Given the Lab 5 "feasible semester-sized vertical slice" constraint, **(b) is the recommended fix** — downgrade is a reasonable feature to explicitly place out of scope alongside the other exclusions already listed in Proposal §5, rather than quietly implying it exists.
