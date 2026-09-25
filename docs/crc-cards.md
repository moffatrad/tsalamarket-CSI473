# CRC Cards — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 4**
**Traces to:** `business-rules.md` (BR-01–BR-12), `requirements.md`, `traceability-matrix.md`

Each responsibility below is allocated to the class that already holds the information needed to perform it (information-expert principle) — not to whichever class happens to be convenient, or to a screen/controller. These six classes are the candidate analysis elements introduced in `traceability-matrix.md`; this laboratory formalises their responsibilities and collaborators.

### CRC-01 — `PriceEntry`

| Responsibilities | Collaborators |
|---|---|
| Know its own commodity, district, quality grade, market level, normalised price (P/kg), submitter identity, timestamp, and current verification status (BR-01) | `ConversionFactorTable` |
| Convert its submitted price to P/kg at creation time, using the commodity's conversion factor; refuse to be created if the submitted unit is unrecognised (BR-03) | `ConversionFactorTable` |
| Default its own grade to `B` and mark itself `ungraded` if no grade was declared at submission (BR-04) | — |
| Know whether it currently qualifies for promotion from Community-reported to Verified, given a second corroborating entry or a registered-submitter flag (BR-02) | `PriceEntry` (a corroborating entry), `Vendor`/`VerifiedBuyer`/`CooperativeLead` |
| Report itself to an `AuditLogRecord` whenever its verification status, grade, or market-level tag is changed by a System Admin (BR-12) | `AuditLogRecord` |

**Rationale:** `PriceEntry` is the information expert for everything about a single submission — it is the only object that knows its own raw and normalised values, so unit conversion and grade defaulting belong here rather than in a submission-handling service.

### CRC-02 — `PriceBucket`

| Responsibilities | Collaborators |
|---|---|
| Group and hold the `PriceEntry` objects that share a commodity × district × grade × market-level combination (BR-05, BR-06) | `PriceEntry` |
| Pool only entries that are Verified and within the trailing 30 days when asked to compute a reference value (BR-05) | `PriceEntry` |
| Determine whether it has the minimum 5 Verified entries from 2 distinct submitters required to produce a result; if not, report itself ineligible so a fallback bucket (nearest district/regional) can be tried instead (BR-06) | — |
| Identify and exclude entries more than 1.5×IQR outside its own Q1–Q3 range before calculating a reference value, and hand each excluded entry to an `AuditLogRecord` for review rather than discarding it (BR-07) | `PriceEntry`, `AuditLogRecord` |
| Calculate its reference price as the median (never the mean) of its qualifying, outlier-filtered entries (BR-08) | `SystemConfiguration` (for window/threshold parameters) |

**Rationale:** the bucket — not an individual `PriceEntry` or a generic "calculator" service — is the only object that has visibility over the whole pooled set, so eligibility, outlier detection and the median calculation all belong to it.

### CRC-03 — `FairPriceCheckResult`

| Responsibilities | Collaborators |
|---|---|
| Know the farmer's offered price, the reference median used, and the calculated percentage deviation between them | `PriceBucket` |
| Classify itself with a fairness flag (Fair / Below Average / Significantly Underpaid) using the current configurable thresholds (BR-09) | `SystemConfiguration` |
| Assign itself a confidence label (High/Medium/Low) based on the sample size, submitter diversity, and recency of the `PriceBucket` it was built from (FR-12) | `PriceBucket` |
| Refuse to be considered complete/valid without a confidence label and the indicative-guidance disclaimer attached (BR-10) | — |
| Report itself (anonymised — commodity, district, deviation, flag only) to the aggregate log used by `AggregateDashboardView` | `FairPriceCheckQuery` |

**Rationale:** bundling the flag, confidence label and disclaimer into one object — rather than three separate lookups the UI must remember to call — is what makes BR-10 ("never returned without both") enforceable at the object level instead of by convention in the UI layer.

### CRC-04 — `ConversionFactorTable`

| Responsibilities | Collaborators |
|---|---|
| Know the accepted sale units and their kg-equivalent conversion factor for each commodity (e.g., a standard tomato crate ≈ 20kg) | — |
| Answer whether a given (commodity, unit) pair is recognised | `PriceEntry` |
| Convert a submitted (price, unit) pair into P/kg for a recognised unit | `PriceEntry` |
| Allow a System Admin to add, correct, or retire a conversion factor | `Admin` |

**Rationale:** commodity conversion factors are domain reference data, not behaviour that belongs to any single `PriceEntry` — centralising it here means every entry converts consistently and a factor only needs correcting in one place.

### CRC-05 — `AuditLogRecord`

| Responsibilities | Collaborators |
|---|---|
| Know the admin identity, timestamp, and before/after values for any manual change to a `PriceEntry`'s verification status, grade, or market-level tag (BR-12) | `PriceEntry`, `Admin` |
| Know which `PriceEntry` was excluded from a `PriceBucket` calculation as a statistical outlier, and when (BR-07) | `PriceEntry`, `PriceBucket` |
| Refuse modification or deletion once written, even by the admin who created it (BR-12) | — |

**Rationale:** keeping audit records immutable and separate from the entries they describe is what makes the audit trail trustworthy — if `PriceEntry` tracked its own history, an admin correcting the entry could also quietly rewrite the record of the correction.

### CRC-06 — `SystemConfiguration`

| Responsibilities | Collaborators |
|---|---|
| Know the current values of all admin-configurable parameters: the fairness-classification thresholds (±10% / 25%), the 30-day aggregation window, the 72-hour corroboration window, and the 5-entry minimum sample size (BR-09, FR-17) | `Admin` |
| Supply its current parameter values to a `PriceBucket` or `FairPriceCheckResult` whenever they need to evaluate eligibility or classify a result | `PriceBucket`, `FairPriceCheckResult` |
| Allow a System Admin to update a parameter without requiring a code change or deployment | `Admin` |

**Rationale:** without a dedicated configuration object, the thresholds in BR-09 would end up hardcoded inside `PriceBucket` or `FairPriceCheckResult`, which would violate FR-17 (admin-adjustable parameters) and force every recalibration through a code change.
