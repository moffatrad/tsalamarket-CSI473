# Traceability Matrix — Tsala Market

**Chain:** Requirement → Use case → Analysis element → Verification
**Sources:** `requirements.md`, `models/use-case-model.*`, `UC-01-check-fair-price.md`, `use-case-summaries.md`, `business-rules.md`, `acceptance-criteria.md`, `quality-scenarios.md`

**Note on analysis elements:** the class/entity names below (`PriceEntry`, `PriceBucket`, `FairPriceCheckResult`, `AuditLogRecord`, `ConversionFactorTable`, `SystemConfiguration`, `AggregateDashboardView`) are the candidate domain concepts implied by `business-rules.md` (BR-01–BR-12). They are listed here to drive `models/domain-model.*`, which is the next artefact to formalise them as classes with attributes, associations and multiplicities — this matrix should be re-checked against that model once it exists, per the studio-plan order (domain model before traceability).

## Core matrix

| Req. | Requirement summary | Use case(s) | Analysis element(s) | Verification |
|---|---|---|---|---|
| FR-01 | Farmer submits a Fair Price Check request (commodity, district, grade, offered price) | UC-01 | `FairPriceCheckQuery`, `Farmer` | AC-01 |
| FR-02 | Normalise every submitted price to P/kg via conversion-factor table | UC-01, UC-03 | `PriceEntry`, `ConversionFactorTable` | AC-04 |
| FR-03 | Reject a price submitted in an unrecognised unit at entry | UC-01 (Alt. Flow A2), UC-03 | `ConversionFactorTable`, `PriceEntry` | AC-04 |
| FR-04 | Verified Buyer/Vendor/Cooperative Lead submits a tagged price entry (commodity, district, grade, market level) | UC-03 | `PriceEntry`, `Vendor`, `VerifiedBuyer` | *Planned — UC-03 acceptance criteria not yet authored* |
| FR-05 | Ungraded entry defaults to Grade B and is flagged "ungraded" | UC-01 (Alt. Flow A1), UC-03 | `PriceEntry` | AC-05 |
| FR-06 | Promote entry from Community-reported to Verified under defined conditions | UC-03, UC-04, UC-05 | `PriceEntry`, verification rule (BR-02) | *Planned — UC-04/UC-05 acceptance criteria not yet authored* |
| FR-07 | Exclude unverified entries from Fair Price Check calculation | UC-01, UC-09 | `PriceBucket` | AC-01 (implicit — only Verified data used) |
| FR-08 | Calculate reference price as median of qualifying pooled entries | UC-01, UC-09 | `PriceBucket`, `FairPriceCheckResult` | AC-01, AC-02 |
| FR-09 | Require minimum 5 Verified entries / 2 submitters per bucket, else fallback | UC-01 (Alt. Flow A3), UC-09 | `PriceBucket` | AC-03 |
| FR-10 | Exclude entries beyond 1.5×IQR from calculation, log for review | UC-05, UC-09 | `PriceBucket`, `AuditLogRecord` | QS-05 |
| FR-11 | Assign fairness flag from percentage deviation thresholds | UC-01 | `FairPriceCheckResult` | AC-01, AC-02 |
| FR-12 | Assign confidence label (High/Medium/Low) | UC-01 | `FairPriceCheckResult` | AC-06 |
| FR-13 | Display indicative-guidance disclaimer with every result | UC-01 | `FairPriceCheckResult` | AC-07 |
| FR-14 | Farmer looks up current/historical price trends (web + USSD/SMS) | UC-02 | `PriceBucket`, `TrendView` | *Planned — UC-02 acceptance criteria not yet authored* |
| FR-15 | Extension Officer views anonymised aggregate district dashboard | UC-06 | `AggregateDashboardView`, `FairPriceCheckQuery` | QS-04 (district-level-only data) |
| FR-16 | Admin manually verifies/corrects entries, action is audit-logged | UC-05 | `PriceEntry`, `AuditLogRecord` | QS-07 |
| FR-17 | Admin configures thresholds/windows as parameters, not hardcoded | UC-07 | `SystemConfiguration` | *Planned — UC-07 acceptance criteria not yet authored* |

## Business-rule traceability

Business rules are invariants enforced by analysis elements rather than user-triggered behaviour, so they are tracked separately here rather than forced into the requirement-driven table above.

| Rule | Enforced by (analysis element) | Verified via |
|---|---|---|
| BR-01 (single verification status) | `PriceEntry` | AC-01 (implicit — no entry contributes as both) |
| BR-02 (verification transition conditions) | `PriceEntry`, verification rule | *Planned — UC-04/UC-05 acceptance criteria* |
| BR-03 (all prices stored in P/kg) | `PriceEntry`, `ConversionFactorTable` | AC-04 |
| BR-04 (ungraded defaults to Grade B) | `PriceEntry` | AC-05 |
| BR-05 (30-day Verified-only pooling) | `PriceBucket` | AC-01 |
| BR-06 (5-entry / 2-submitter minimum) | `PriceBucket` | AC-03 |
| BR-07 (outlier exclusion, not deletion) | `PriceBucket`, `AuditLogRecord` | QS-05 |
| BR-08 (median, not mean) | `PriceBucket`, `FairPriceCheckResult` | AC-01, AC-02 |
| BR-09 (uniform thresholds unless reconfigured) | `FairPriceCheckResult`, `SystemConfiguration` | AC-01, AC-02 |
| BR-10 (result never returned without confidence + disclaimer) | `FairPriceCheckResult` | AC-06, AC-07 |
| BR-11 (district-level-only location) | `Farmer`, `FairPriceCheckQuery`, `AggregateDashboardView` | QS-04 |
| BR-12 (immutable audit log on Admin actions) | `AuditLogRecord` | QS-07 |

## Coverage summary

- **17/17** functional requirements traced to at least one use case and one analysis element.
- **10/17** requirements already have concrete verification evidence (AC-xx or QS-xx); the remaining **7** (FR-04, FR-06, FR-14, FR-17, plus the BR-02 rule) are traced to a use case and analysis element but still need acceptance criteria written for UC-02, UC-03, UC-04, UC-05, and UC-07 — flagged above as *Planned* rather than left blank, so the gap is visible rather than silently missing.
- **12/12** business rules traced to an enforcing analysis element.

