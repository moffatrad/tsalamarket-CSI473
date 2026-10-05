# Core Operation Contract — Check Fair Price

**Team 16 · Tsala Market · CSI473 Laboratory 8**
**Machine-readable source:** `docs/api-contracts/core-operation.yaml` (OpenAPI 3.0.3, validated)
**Traces to:** UC-01 · FR-01, FR-02, FR-03, FR-05, FR-08–FR-13 · AC-01–AC-07 · BR-03–BR-11 · QS-01, QS-04 · `ADR-001-architecture.md` · `models/logical-data-model.md`

## 1. The operation
| **Service operation** | `ICheckFairPrice.checkFairPrice(command) → FairPriceCheckResult` or a stable error (`FairPriceCheckService`, per `component-architecture.mmd`) |
| **HTTP binding** | `POST /v1/fair-price-checks`, exposed by the Web/REST adapter |
| **USSD binding** | The USSD adapter calls the same operation in-process. Error codes and result fields are identical on both channels; only presentation differs. |
| **Why this operation** | It is the only fully dressed use case (UC-01), it is the direct realisation of Objective 2, and it exercises every layer: adapter, service, `BucketAggregate` read, `SystemConfiguration`, and the `FairPriceCheckQuery` log. |

## 2. Request and validation

| Field | Required | Rule |
|---|---|---|
| `commodity` | Yes | Non-empty, ≤64 chars; matched case-insensitively against the commodities present in `ConversionFactorTable` |
| `district` | Yes | Non-empty, ≤64 chars; must be in the `valid_districts` configuration list. District is the finest location accepted (BR-11) |
| `grade` | No | `A`, `B` or `C`. If omitted, Grade B is used and `grade_assumed = true` |
| `offered_price` | Yes | Number, > 0 and ≤ 1,000,000 (Pula, per `unit`) |
| `unit` | Yes | Must exist for this commodity in `ConversionFactorTable` |
| anything else | — | Rejected. The schema has `additionalProperties: false`, so a client cannot send a phone number, name or coordinates even by accident (BR-11) |

**Validation order** (fixed, so the same bad request always produces the same error):

1. Body parses as JSON and has all required fields with the right types, no unknown fields → else `MALFORMED_REQUEST`
2. `offered_price` is a finite number > 0 → else `INVALID_PRICE`
3. `grade`, if present, is A/B/C → else `INVALID_GRADE`
4. `commodity` known → else `UNKNOWN_COMMODITY`
5. `district` known → else `UNKNOWN_DISTRICT`
6. `unit` supported for the commodity → else `UNSUPPORTED_UNIT`
7. Only now does the operation touch `BucketAggregate`

Steps 1–3 are syntactic (HTTP 400). Steps 4–6 and the data rules below are domain rules (HTTP 422).

## 3. Processing rules

| # | Rule | Source |
|---|---|---|
| P1 | Convert `offered_price` to P/kg using `ConversionFactorTable`, round half-up to 2 decimals | FR-02, BR-03 |
| P2 | Use Grade B when `grade` is absent and report `grade_assumed = true` | FR-05, UC-01 A1 |
| P3 | Read exactly **one** `BucketAggregate` row, keyed (commodity, district, grade, `Farm-gate`). Never scan or aggregate `PriceEntry` rows on this path | QS-01, ADR-001 |
| P4 | The row is usable only if `sample_size` ≥ the configured minimum (5) **and** `submitter_count` ≥ the configured minimum (2). Otherwise the row is treated as absent | BR-06, FR-09 |
| P5 | If no usable row exists → `INSUFFICIENT_VERIFIED_DATA`. No flag is issued and nothing is written | UC-01 A3 |
| P6 | Compute `deviation_pct = (offered − reference) / reference × 100` from the two 2-decimal prices | FR-11 |
| P7 | Classify using thresholds from `SystemConfiguration`. Defaults: ≥ −10.0 → Fair; −25.0 to < −10.0 → Below Average; < −25.0 → Significantly Underpaid. An offer **above** the reference is Fair | BR-09 |
| P8 | `confidence_label` comes from the aggregate row; it is forced to `Low` whenever `basis.scope` ≠ `district` | FR-12, UC-01 A3 |
| P9 | Attach `disclaimer` and `disclaimer_short` to every successful result | FR-13, BR-10 |
| P10 | Write one `FairPriceCheckQuery` row (commodity, district, grade, market level, offered P/kg, reference price **snapshot**, deviation, flag, confidence, time) and return its id as `check_id`. No account, phone or session identifier is stored | FR-15, BR-11 |

P7 settles a boundary the proposal left ambiguous: "within ±10%" and "10–25% below" both seem to cover exactly 10% below. This contract makes −10.0 exactly **Fair**, and −25.0 exactly **Below Average**.

## 4. Success response (HTTP 200)

All fields are always present — that invariant is how BR-10 is enforced at the contract level.

| Field | Meaning |
|---|---|
| `check_id` | UUID of the logged query row |
| `commodity`, `district` | Echo of the request (`district` is the district asked about, even if a wider area was used) |
| `grade_used`, `grade_assumed` | Grade applied, and whether it was defaulted |
| `offered_price_per_kg`, `reference_price_per_kg` | Normalised offer and median reference, P/kg, 2 decimals |
| `deviation_pct` | Signed percentage, 1 decimal; negative = below reference |
| `fairness_flag` | `Fair` / `Below Average` / `Significantly Underpaid` |
| `confidence_label` | `High` / `Medium` / `Low` |
| `basis` | `sample_size`, `submitter_count`, `computed_at`, `scope` (`district` / `neighbouring_district` / `region`) |
| `disclaimer` / `disclaimer_short` | Full text (≤300 chars) and USSD/SMS-length text (≤90 chars). Adapters must show one |
| `checked_at` | Server time of the check |

Worked examples in the YAML match the acceptance criteria: AC-01 (152 per 20 kg crate → P7.60/kg vs P8.00 → −5.0% → Fair), AC-02 (112 per crate → P5.60/kg → −30.0% → Significantly Underpaid), AC-03 (Butternut, Ngamiland, widened to a neighbouring district → Low confidence).

## 5. Error catalogue

Clients branch on `code`, never on `message`. Codes are never renamed or reused.

| HTTP | `code` | Meaning | `details` | Retry? | Rule / AC |
|---|---|---|---|---|---|
| 400 | `MALFORMED_REQUEST` | Body unreadable, required field missing, wrong type, or unknown field present | `{field}` when identifiable | No — fix the request | — |
| 400 | `INVALID_PRICE` | `offered_price` not a number > 0 | `{field}` | No | — |
| 400 | `INVALID_GRADE` | `grade` not A, B or C | `{field, allowed}` | No | — |
| 422 | `UNKNOWN_COMMODITY` | Commodity not in `ConversionFactorTable` | `{commodity}` | No | — |
| 422 | `UNKNOWN_DISTRICT` | District not in `valid_districts` | `{district}` | No | — |
| 422 | `UNSUPPORTED_UNIT` | Unit not defined for this commodity | `{commodity, supported_units[]}` | No — pick a supported unit | FR-03, BR-03, **AC-04** |
| 422 | `INSUFFICIENT_VERIFIED_DATA` | Valid request, but no area has enough verified data; no flag issued | `{commodity, district, scopes_tried[]}` | Later — data may arrive | FR-09, BR-06, **AC-03** |
| 409 | `IDEMPOTENCY_KEY_REUSED` | Same `Idempotency-Key`, different body | `{}` | No — use a new key | §6 |
| 503 | `AGGREGATE_STORE_UNAVAILABLE` | Database/aggregate store unreachable. `Retry-After` header set | `{}` | **Yes**, same key | §6 |
| 500 | `INTERNAL_ERROR` | Unexpected failure | `{}` | Yes, same key | §6 |

## 6. State guarantees: what gets written, and when

| Outcome | `FairPriceCheckQuery` row written? |
|---|---|
| 200 (first time) | Exactly one |
| 200 replay (same key, same body) | None — returns the original response with `Idempotent-Replayed: true` |
| Any 400 / 409 / 422 | None |
| 503 / 500 | None (the write and the response are one transaction; if the write fails, the caller gets no result) |

So a caller never receives a result that was not logged, and never causes two log rows for one farmer decision. The second guarantee matters because USSD sessions drop and retry, and double-logging would inflate the Extension Officer's underpayment counts (FR-15). Full retry/timeout behaviour is modelled in `models/failure-recovery.*`.

## 7. Non-functional obligations on this operation

- **QS-01:** the request path is one indexed read plus one insert. No scan of `PriceEntry`, no median or IQR computation.
- **QS-04 / BR-11:** the request schema has no identity fields, and the logged row has no account reference — privacy is structural, not just a policy.
- **QS-03:** `disclaimer_short` and short, stable `code` values let the USSD adapter keep screens within the 5-screen budget.

## 8. Design rationale

- **Insufficient data is an error (422), not a 200 with an `outcome` field.** *Alternative:* return 200 with `outcome: "INSUFFICIENT_DATA"` and null result fields. *Why not:* it would make every result field nullable, so BR-10 ("never a result without confidence and disclaimer") could no longer be seen in the schema. *Consequence accepted:* clients must handle a 422 as a normal, expected outcome, not a failure; the error body carries enough detail (`scopes_tried`) to show a useful message.
- **Idempotency via a client-supplied key, not server-side de-duplication by content.** *Alternative:* treat two identical requests within N seconds as duplicates. *Why not:* two different farmers in the same district legitimately ask identical questions in the same minute. *Consequence accepted:* adapters must generate keys, and the service must store them (§9, OI-1).
- **Domain-rule failures use 422, syntax failures use 400.** Lets the USSD and web adapters treat "fix your input" (400) and "valid input, no answer for you" (422) differently without parsing messages.

## 9. Open issues and required changes to other artefacts

These were found while writing the contract. They are recorded here rather than silently patched in other files.

| ID | Issue | Needed change |
|---|---|---|
| **OI-1** | Idempotency needs storage the logical data model does not have. | Add nullable, unique `idempotency_key` and `request_hash` to `FairPriceCheckQuery` in `logical-data-model.mmd`. The key is a hash derived by the adapter, so it is not an identity column under BR-11. |
| **OI-2** | `BucketAggregate` is recomputed when a `PriceEntry` becomes Verified (ADR-001), but BR-05's 30-day window also removes entries by **ageing out**, which triggers no event. A bucket with no new verifications would keep serving a median that includes expired entries, and a `High` confidence label whose "within 7 days" condition is no longer true. `basis.computed_at` makes this visible but does not fix it. | Add a scheduled sweep (e.g. daily) that recomputes any bucket with entries crossing the 7- or 30-day boundary; record it in ADR-001 and `docs/data-integrity.md`. |
| **OI-3** | This contract assumes the worker precomputes the widened (neighbouring-district / region) value into the farmer's own district row, so the request path is a single read (P3). `sequence-core-use-case.mmd` shows fallback happening inside `PriceBucket` on the read path. | Reconcile in the Lab 8 cross-check: update the sequence diagram so fallback is shown as worker-side, or relax P3. |
| **OI-4** | Validation depends on configuration not yet listed: `valid_districts`, `district_adjacency`, `district_regions`. | Add these keys to the `SystemConfiguration` seed list (no schema change needed — it is a key/value table). |

OI-2 is the strongest candidate for this laboratory's **main integrity risk** (see exit record).
