# Data Integrity — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 8**
**Traces to:** `logical-data-model.md` · `core-operation.md` · `deployment.md` · `failure-recovery.md` · `business-rules.md` (BR-01–BR-12) · `quality-scenarios.md` · `ADR-001-architecture.md`

This file gathers every integrity constraint the Lab 8 artefacts depend on into one catalogue, says **where** each is enforced and **how** it will be tested, then records what the cross-check of those artefacts found. Four properties matter for this system:

- **Accuracy** — the reference price a farmer sees must be built only from data that deserves to be trusted.
- **Consistency** — no partial, duplicate or half-written state, including after a failure.
- **Accountability** — every change to classified data can be traced to who made it.
- **Privacy** — no stored value can identify a farmer (BR-11).

## 1. Where a constraint can be enforced

| Level | Meaning | Strength |
|---|---|---|
| **S** | Schema: primary/foreign key, `UNIQUE`, `NOT NULL`, `CHECK` | Cannot be bypassed by application bugs |
| **P** | Database privilege: which role may `INSERT`, `UPDATE`, `DELETE` (`deployment.md` §3) | Cannot be bypassed by application bugs |
| **A** | Application logic, inside a transaction | Only as good as the code and its tests |
| **O** | Operational: schedules, backups, log hygiene | Only as good as the process |

Where a constraint is marked A or O only, it **needs a test**; that is why every row has a "Verified by" entry.

## 2. Constraint catalogue

### A. Identity and references

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-01 | Every table has the primary key shown in the data model. `ConversionFactorTable` is unique on (commodity, unit); `BucketAggregate` on (commodity, district, grade, market_level) | S | Data model | Duplicate insert rejected |
| DC-02 | Every foreign key resolves (`submitted_by`, `verified_by`, `corroborating_entry_id`, `actor_account_id`, `target_entry_id`, `updated_by`). No role has `DELETE`, so referenced rows never disappear; accounts are deactivated, not deleted | S + P | Data model, deployment §3 | Insert with missing parent rejected; `DELETE` denied |

### B. Values

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-03 | Enumerated columns (`status`, `grade`, `market_level`, `role`, `fairness_flag`, `confidence_label`, `action_type`, `fallback_scope`) accept only their listed values | S | BR-01, BR-04 | Invalid value rejected |
| DC-04 | `price_submitted`, `price_per_kg`, `offered_price_per_kg`, `kg_per_unit` are > 0; `submitter_count` ≥ 1 and ≤ `sample_size` | S | BR-03 | Zero and negative values rejected |
| DC-05 | `price_per_kg` is `NOT NULL` and equals `price_submitted ÷ kg_per_unit` (2 dp, half-up) when the row is created. Changing a conversion factor never rewrites stored prices | S + A | BR-03, FR-02 | 152 per 20 kg crate stores 7.60; change the factor, old rows unchanged |
| DC-06 | `grade` is `NOT NULL`, defaults to `B`, and `grade_was_declared = false` whenever it was defaulted | S + A | BR-04, FR-05 | Insert without a grade |

### C. Verification state

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-07 | Verification columns agree with `status`. Community-reported ⇒ `verification_reason`, `verified_at`, `verified_by`, `corroborating_entry_id` all `NULL`. Verified ⇒ reason and `verified_at` set. Reason `admin_confirmed` ⇒ `verified_by` set; `corroborated` ⇒ `corroborating_entry_id` set | S (`CHECK`) | BR-01, BR-02 | One violating row per clause rejected |
| DC-08 | A corroborating entry is a different row, same commodity/district/grade/market level, within 72 h and 15 %, and from a **different submitter** | A | BR-02(b), FR-06 | Boundary tests at 71 h / 73 h and 14 % / 16 %; same-submitter attempt rejected. See DI-3 |
| DC-09 | Verification never moves backward by system action; no code path sets Community-reported after creation (a database trigger is recommended as a backstop) | A (+ trigger) | BR-02 | Attempted downgrade rejected. See DI-2 |

### D. Derived data (`BucketAggregate`)

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-10 | Only role `worker` can write `BucketAggregate`; the request path is read-only | P | ADR-001, failure-recovery I5 | `INSERT`/`UPDATE` by role `app` denied |
| DC-11 | An aggregate is built only from Verified, in-window, non-outlier entries, and the reference is their **median** | A (worker) | BR-05, BR-07, BR-08 | Fixture with unverified, expired and outlier entries: median unchanged |
| DC-12 | An aggregate is served only if `sample_size` ≥ the minimum **and** `submitter_count` ≥ 2, re-checked at read time | A | BR-06, FR-09 | 4 entries, or 1 submitter ⇒ `INSUFFICIENT_VERIFIED_DATA` (AC-03) |
| DC-13 | An aggregate is recomputed whenever its inputs change (see DI-5); `computed_at` always shows its age | A + O | BR-05, QS-01 | Change each input type, confirm the row changes |
| DC-14 | Outliers are excluded, **never deleted**, and each exclusion writes an `AuditLogRecord` | A + P | BR-07, QS-05 | Outlier row still present; audit row exists |

### E. Query log and idempotency

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-15 | `idempotency_key` is `UNIQUE`; a matching key with a different `request_hash` returns 409 | S + A | I1, REC-1 | T1, T2, T5 |
| DC-16 | A `FairPriceCheckQuery` row and its result are written in one transaction; every error writes nothing | A | I2, I3 | T3, T7 |
| DC-17 | The row stores the full result snapshot (`fairness_flag` and `confidence_label` `NOT NULL`, plus `grade_assumed` and `basis_*`), and a replay returns it verbatim | S + A | I4, BR-10 | T6 |
| DC-18 | Query rows are immutable: role `app` has `INSERT` and `SELECT` only | P | BR-11, FR-15 | `UPDATE` denied |

### F. Audit and configuration

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-19 | `AuditLogRecord` is append-only: `INSERT`-only for both roles, no `updated_at` column | P + S | BR-12 | `UPDATE`/`DELETE` denied |
| DC-20 | Every Admin change and its `AuditLogRecord` commit in **one transaction** | A | BR-12, QS-07 | Force the audit insert to fail ⇒ the change rolls back. See DI-4 |
| DC-21 | `SystemConfiguration` values are validated on write: fair band < underpaid band, windows ≥ 1, minimum sample ≥ 3 (proposed), minimum submitters fixed at ≥ 2 | A | BR-09, FR-17 | Out-of-range value rejected. See DI-4 |
| DC-22 | Submitted facts are immutable after insert: role `app` may `UPDATE` only `grade`, `grade_was_declared`, `market_level`, `status` and the verification columns | P (column grants) | BR-03, BR-12 | `UPDATE price_per_kg` denied. See DI-7 |

### G. Privacy

| ID | Constraint | Level | Source | Verified by |
|---|---|---|---|---|
| DC-23 | No column finer than district exists on any table; `FairPriceCheckQuery` has no account reference; the request schema rejects unknown fields; logs hold no request bodies | S + A + O | BR-11, QS-04 | Schema review; request with a phone field ⇒ 400; log inspection |
| DC-24 | `idempotency_key` is an **HMAC** (server-side secret) of session id and check counter — never the raw phone number or a plain hash | A | BR-11, DI-6 | Key cannot be reproduced without the secret |

## 3. Updated traceability

**Business rules → constraints**

| Rule | Constraints | Strongest level reached |
|---|---|---|
| BR-01 | DC-03, DC-07 | S |
| BR-02 | DC-07, DC-08, DC-09 | S for state shape; **A only** for who may verify |
| BR-03 | DC-04, DC-05 | S |
| BR-04 | DC-06 | S |
| BR-05 | DC-11, DC-13 | **A / O only** |
| BR-06 | DC-12 | **A only** (configurable, so not a `CHECK`) |
| BR-07 | DC-11, DC-14 | A + P |
| BR-08 | DC-11 | **A only** |
| BR-09 | DC-21 | **A only** |
| BR-10 | DC-17 | S |
| BR-11 | DC-18, DC-23, DC-24 | S + P |
| BR-12 | DC-19, DC-20, DC-22 | P; DC-20 is **A only** |

**Quality scenarios → constraints**

| Scenario | Constraints | Note |
|---|---|---|
| QS-01 | DC-10, DC-12, DC-13 | Read path stays one indexed read only while the aggregate is trustworthy |
| QS-04 | DC-23, DC-24 | Privacy is structural, not policy |
| QS-05 | DC-11, DC-14 | |
| QS-07 | DC-19, DC-20 | "Zero omissions" holds only if DC-20 is implemented as a transaction |
| QS-02 | — | Availability is not an integrity constraint; see DEP-1 |

## 4. Cross-check findings

Checking the data model, contract, deployment and failure model against the domain rules turned up seven new problems. They are recorded here, not silently patched.

| ID | Finding | Evidence | Proposed resolution |
|---|---|---|---|
| **DI-1** | **"Registered" is undefined, so auto-verification may make the rest of the verification workflow unreachable.** BR-02(a) verifies any entry from a "registered" Verified Buyer, Vendor or Cooperative Lead. FR-04 and the lifecycle diagram say those same three roles are the only submitters. If "registered" just means "has such an account", every entry is Verified on arrival and conditions (b) and (c) can never apply. `Account` has a `role` but no approval status. | FR-04, FR-06(a), `lifecycle-or-activity.mmd` `RegisteredCheck`, `Account` in the data model | Add `Account.registration_status` (Pending / Approved / Suspended). Condition (a) requires **Approved**. Entries from Pending accounts stay Community-reported until corroborated or Admin-confirmed. Needs a team decision. |
| **DI-2** | **A wrong Verified entry cannot be retracted, and "reject" has no representation.** FR-16 and `AuditLogRecord.action_type` include *reject*, but `PriceEntry.status` has only two values (BR-01), and the Gap 3 decision removed Admin downgrade. A typo inside the IQR range, or data from a compromised account, would stay in the median until it ages out. | FR-16, BR-01, Phase 1 report Gap 3 | Add `PriceEntry.excluded` (boolean) with `excluded_by` and a reason. An excluded entry is skipped by the worker (like an outlier, BR-07), is never deleted, writes an audit row, and triggers recompute. "Reject" becomes "exclude". |
| **DI-3** | **"Independent" corroboration is undefined.** Nothing says a corroborating entry must come from a different account, so one submitter could post twice and verify themselves. | FR-06(b), BR-02(b) | Define independent as a different `submitted_by` (DC-08). Add to BR-02. |
| **DI-4** | **Admin changes are not required to be atomic with their audit record, and configuration values have no bounds.** A configuration change that commits while its audit insert fails breaks BR-12; a minimum sample of 0 would switch off BR-06. | CRC-05, FR-17, QS-07 | DC-20 (one transaction) and DC-21 (validated ranges). |
| **DI-5** | **Recompute triggers are incomplete.** ADR-001 recomputes only when an entry becomes Verified. Inputs also change when entries age past the 7- and 30-day boundaries (OI-2), when an Admin corrects a grade or market level (**both the old and new bucket**), when an entry is excluded (DI-2), and when a window or minimum is reconfigured (**all buckets**). | ADR-001, FR-16, FR-17 | Recompute on all five triggers: verification, ageing (scheduled sweep), correction, exclusion, configuration change. Update ADR-001. |
| **DI-6** | **The idempotency key is described as "a hash".** A plain hash of a guessable session id can be brute-forced, which would let someone with database access link query rows to gateway sessions. | `core-operation.yaml` header description, BR-11 | Use an HMAC with a server-side secret (DC-24). Reword the contract. |
| **DI-7** | **The deployment role table lets `app` update any `PriceEntry` column.** That includes `price_per_kg` and `submitted_by`, which should never change after insert. | `deployment.md` §3 | Column-level grants (DC-22). Update the role table. |

## 5. Open items from the Lab 8 artefacts

Everything below is **still open**; no artefact has been edited to apply it.

| IDs | Item | Artefact to change |
|---|---|---|
| OI-1, REC-1 | Add `idempotency_key` (unique), `request_hash`, `grade_assumed`, `basis_*` to `FairPriceCheckQuery` | `logical-data-model.mmd` |
| OI-2, DI-5 | Add scheduled sweep and the other recompute triggers | `ADR-001-architecture.md` |
| OI-3, REC-3 | Show fallback as worker-side, and logging as one transaction with the key check first | `sequence-core-use-case.mmd` |
| OI-4 | Seed `valid_districts`, `district_adjacency`, `district_regions` | `SystemConfiguration` seed list |
| REC-2 | Remove the 24-hour replay limit | `core-operation.yaml` |
| DI-6 | Reword key derivation as an HMAC | `core-operation.yaml` |
| DEP-1 | Time a restore against the 30-minute target; review the 24-hour backup window | `deployment.md` (test) |
| DEP-2 | Decide Admin protection: multi-factor login or network restriction | `deployment.md` |
| DEP-3, DI-7 | Idempotency columns and column-level grants in the role table | `deployment.md` |
| DI-1 – DI-4 | Decisions listed in §4 | `business-rules.md`, `logical-data-model.mmd`, `requirements.md` |

## 6. Main integrity risk

**Wrong or poisoned data can become Verified immediately, and nothing can take it back out.** DI-1 and DI-2 combine:

1. Under the current wording, any submitter's entry is Verified on arrival (DI-1).
2. Once Verified, an entry stays in the median until it ages out, unless the IQR rule happens to catch it (DI-2).
3. The Fair Price Check exists to give farmers a reference they can trust when deciding whether to accept an offer. A poisoned median directly causes the harm the project is meant to prevent, and it does so with a "High" confidence label.

The existing backstops (five entries from two submitters, IQR exclusion, audit log) help against a single careless entry but not against a compromised account or a small group posting consistent prices.

**Why this ranks above the other open items:** duplicate rows (failure-recovery) and stale aggregates (OI-2) degrade the data in ways that can be measured and bounded; this risk degrades it in a way the system would report as high-confidence.

## 7. Exit record (recommended)

- **Risk:** an entry from an unvetted or compromised account is Verified at once and cannot be retracted, skewing the reference price farmers rely on.
- **Mechanism:** `Account.registration_status` so only **Approved** accounts verify on submission (DI-1), plus `PriceEntry.excluded` with an audit record and forced recompute so a bad entry can be taken out without deleting it (DI-2).
- **Test:** (1) an entry from a Pending account stays Community-reported and does not change the median; (2) excluding a Verified entry changes the bucket's reference price, leaves the row in place, and writes one `AuditLogRecord`; (3) the same exclusion is rolled back if the audit insert fails (DC-20).

`failure-recovery.md` §7 holds the alternative draft (duplicate or half-written query row, tested by T2 and T3). Use whichever the team agrees is the main risk; this one is recommended because of its impact on the reference price itself.
