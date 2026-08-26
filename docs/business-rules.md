# Business Rules and Invariants — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 4**
**Traces to:** `requirements.md` (FR-02, FR-05, FR-06, FR-08–FR-13, FR-16, FR-17) · `UC-01-check-fair-price.md` · Proposal §6a (Price normalisation, verification, aggregation and classification methodology) · Proposal §8 (Data, ethics, safety and dependency risks)

These are domain-level constraints and invariants — statements that must always hold true about the data and its state, independent of any particular screen or interaction. They are the rules the domain model (`models/domain-model.*`) and CRC responsibilities (`docs/crc-cards.md`) must enforce.

---

### BR-01 — A price entry has exactly one verification status at all times
A `PriceEntry` is always in exactly one of two states: `Community-reported` or `Verified`. It cannot be both, and it cannot be unset. This is the invariant the Verification workflow (BR-02) operates on.
**Traces to:** FR-06 · UC-03, UC-04, UC-05

### BR-02 — Verification status only moves forward, and only under defined conditions
A `PriceEntry` may transition from `Community-reported` to `Verified` only when at least one of three conditions holds: (a) it was submitted by a registered Verified Buyer, Market Vendor, or Cooperative Lead account; (b) it is corroborated by a second independent entry for the same commodity/district/grade/market-level within 72 hours and within 15% of the original price; or (c) a System Admin manually confirms it. A Verified entry is never automatically reverted to Community-reported by the system — only a System Admin action can downgrade it, and that action must satisfy BR-08 (audit logging).
**Traces to:** FR-06, FR-16 · UC-04, UC-05

### BR-03 — All stored prices are normalised to Pula per kilogram
A price is never persisted in its original submission unit (crate, bag, heap, bundle). Every `PriceEntry` stores a normalised value in P/kg, calculated at entry time via the commodity's conversion-factor table. An entry in an unrecognised unit is never stored — it is rejected before creation.
**Traces to:** FR-02, FR-03 · UC-01 (Alternative Flow A2), UC-03

### BR-04 — An entry with no declared grade defaults to Grade B, never A or C
If a submitter does not declare a quality grade at the time of submission, the `PriceEntry`'s grade is set to `B` (standard market quality) by default — never `A` (premium) or `C` (below-standard). The entry is additionally flagged `ungraded` for Admin correction. This is a conservative default: it must never bias a Fair Price Check result toward either extreme.
**Traces to:** FR-05 · UC-01 (Alternative Flow A1), UC-03

### BR-05 — Only Verified entries within the trailing 30 days may feed a Fair Price Check calculation
A `PriceEntry` is eligible to be pooled into a reference-price calculation only if its status is `Verified` and it was submitted within the last 30 days. Community-reported entries and entries older than 30 days remain visible for trend display but are excluded from any Fair Price Check result.
**Traces to:** FR-07, FR-08 · UC-01, UC-09

### BR-06 — A bucket needs a minimum of 5 independent Verified entries from 2 distinct submitters before it can produce a result
A `PriceBucket` (defined by commodity × district × grade × market level) may only be used to generate a Fair Price Check result if it contains at least 5 qualifying Verified entries from at least 2 different submitter accounts. A bucket that does not meet this threshold cannot be used directly; the system must apply the fallback rule (nearest district or broader regional bucket) instead of returning a thin or single-submitter average.
**Traces to:** FR-09 · UC-01 (Alternative Flow A3), UC-09

### BR-07 — Statistical outliers are excluded from calculation but never deleted
Any `PriceEntry` whose value lies more than 1.5× the interquartile range (IQR) outside its bucket's Q1–Q3 range is excluded from the reference-price calculation for that bucket. The entry itself is retained in the dataset (not deleted) and is queued for System Admin review. An excluded entry may still be re-included later if an Admin overturns the exclusion.
**Traces to:** FR-10 · UC-05, UC-09

### BR-08 — The reference price is always the median of qualifying entries, never the mean
When a `PriceBucket` computes its reference value, it must use the median of the remaining pooled entries (after BR-05 and BR-07 filtering) — never the arithmetic mean. This choice is deliberate: the median is less distorted by the small, unevenly distributed samples expected from an early-stage crowd-sourced dataset.
**Traces to:** FR-08 · UC-09

### BR-09 — Fairness classification thresholds apply uniformly unless explicitly reconfigured
The percentage-deviation bands that determine a fairness flag (±10% = Fair; 10–25% below = Below Average; more than 25% below = Significantly Underpaid) apply identically across every commodity and district. They may only be changed by a System Admin updating the system-wide configurable parameters (BR-06's 5-entry minimum, the 30-day window, and the 72-hour corroboration window are governed the same way) — never hardcoded per commodity or district in application logic.
**Traces to:** FR-11, FR-17 · UC-01, UC-07

### BR-10 — A Fair Price Check result is never returned without a confidence label and disclaimer
It is invalid for the system to produce a fairness flag without also attaching a confidence label (High/Medium/Low) and the indicative-guidance disclaimer. A `FairPriceCheckResult` without both of these attached is an incomplete, invalid object — the two are not optional decorations added afterward.
**Traces to:** FR-12, FR-13 · UC-01

### BR-11 — Farmer location is never stored more precisely than district level
No record in the system — a `PriceEntry`, a `FairPriceCheckQuery` log, or any Extension Officer dashboard aggregate — may store or expose farmer location more precisely than district level. Precise coordinates or addresses are never captured for farmer-originated data.
**Traces to:** Proposal §8 (Data, ethics, safety and dependency risks) · UC-01, UC-06

### BR-12 — Every manual Admin action that alters an entry's classification is immutably logged
Any System Admin action that changes a `PriceEntry`'s verification status, grade, or market-level tag must create a corresponding, immutable `AuditLogRecord` capturing the admin's identity, a timestamp, and the before/after values. An Admin cannot alter or delete their own prior audit records.
**Traces to:** FR-16 · UC-05

---

*12 business rules/invariants — exceeds the Lab 4 minimum of six. BR-01–BR-04 govern entry state and normalisation; BR-05–BR-08 govern aggregation and calculation; BR-09–BR-10 govern classification and result completeness; BR-11–BR-12 govern privacy and auditability. These map directly onto the candidate domain classes expected next in `models/domain-model.*` (e.g., `PriceEntry`, `PriceBucket`, `FairPriceCheckResult`, `AuditLogRecord`).*
