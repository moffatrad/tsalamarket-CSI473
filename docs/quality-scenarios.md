# Quality Scenarios — Tsala Market

Traces to: `UC-01-check-fair-price.md`, `requirements.md` (FR-06, FR-08–FR-14, FR-16), Proposal §5 (Scope, assumptions and constraints), §8 (Data, ethics, safety and dependency risks)

Each scenario follows the six-part quality-attribute form (source, stimulus, artifact, environment, response, response measure) so the response level is verifiable rather than a vague aspiration like "the system should be fast."

## Quick-scan summary

| ID | Quality attribute | One-line scenario |
|---|---|---|
| QS-01 | Performance | Fair Price Check returns a result within a bounded time over USSD |
| QS-02 | Availability | System stays reachable through peak selling-season load |
| QS-03 | Usability | A first-time feature-phone farmer completes a check without help |
| QS-04 | Security / Privacy | Farmer-identifiable data never leaves district-level granularity |
| QS-05 | Reliability / Data integrity | Outlier submissions are excluded, not allowed to skew the reference price |
| QS-06 | Scalability | Response time holds as submission volume grows with adoption |
| QS-07 | Auditability | Every manual Admin override is captured in an immutable log |

### QS-01 — Performance: Fair Price Check response time

| Part | Detail |
|---|---|
| **Source** | Smallholder Farmer, using the USSD channel |
| **Stimulus** | Submits a Fair Price Check request during normal business hours |
| **Artifact** | Fair Price Check calculation service (aggregation, outlier filtering, fairness classification — FR-08–FR-11) |
| **Environment** | Normal operation; up to 50 concurrent USSD sessions; the matching bucket already holds enough Verified data (no district fallback needed) |
| **Response** | The system computes the reference median, applies outlier filtering, assigns the fairness flag and confidence label, and returns the result over USSD |
| **Response measure** | 95% of requests return a complete result within 5 seconds end-to-end (session start to result display); 100% return within 10 seconds |

### QS-02 — Availability: uptime during peak selling season

| Part | Detail |
|---|---|
| **Source** | All actor types (farmers, vendors, buyers, extension officers) |
| **Stimulus** | Users attempt price lookups, submissions, or Fair Price Checks during peak harvest/selling months |
| **Artifact** | The whole Tsala Market system (web dashboard, USSD gateway, backend) |
| **Environment** | Normal operation, including planned maintenance windows |
| **Response** | The system continues serving lookup, submission, and Fair Price Check requests without interruption |
| **Response measure** | ≥99% uptime measured monthly; any unplanned outage is detected and service restored within 30 minutes |

### QS-03 — Usability: first-time USSD completion without assistance

| Part | Detail |
|---|---|
| **Source** | Smallholder Farmer using a basic feature phone with no internet access, first-time user of the system |
| **Stimulus** | Wants to complete a Fair Price Check on an offer just received from a buyer |
| **Artifact** | USSD menu flow ("Check My Offer" — UC-01, steps 1–3) |
| **Environment** | Normal field conditions, no prior training or written instructions provided |
| **Response** | The farmer navigates the numeric USSD menu and completes the check unaided |
| **Response measure** | In usability testing with ≥5 representative first-time users, ≥80% complete a full Fair Price Check in 5 or fewer USSD screens, with no external help |

### QS-04 — Security / privacy: farmer data protection

| Part | Detail |
|---|---|
| **Source** | An unauthorised party, or an authorised Extension Officer/Admin operating within their normal role |
| **Stimulus** | A request to view, export, or query price-submission records, including the Extension Officer's aggregate district dashboard (FR-15) |
| **Artifact** | Price and query database; Extension Officer dashboard; Admin data-access layer |
| **Environment** | Normal operation, including scheduled data audits |
| **Response** | The system stores farmer location at district level only (never precise coordinates), never surfaces phone numbers or farmer identity on the Extension Officer dashboard, and requires authentication for any Admin-level record access; unauthorised attempts are rejected |
| **Response measure** | 100% of records sampled in an audit contain no farmer-identifiable data beyond district-level granularity; 100% of unauthenticated access attempts are logged and rejected on the same request |

### QS-05 — Reliability / data integrity: outlier resistance

| Part | Detail |
|---|---|
| **Source** | A Market Vendor, Cooperative Lead, or Verified Buyer submitting a price entry |
| **Stimulus** | A submitted entry deviates by more than 1.5× the interquartile range (IQR) from the existing bucket (mistyped price or bad-faith submission) |
| **Artifact** | Aggregation and outlier-filtering component (FR-10) |
| **Environment** | Normal operation; the target bucket already holds ≥5 Verified entries |
| **Response** | The entry is excluded from the reference-price calculation and logged for System Admin review rather than silently accepted or silently discarded |
| **Response measure** | 100% of entries beyond the 1.5×IQR threshold are excluded from the calculated reference price, and appear in the Admin outlier-review queue within 1 minute of submission |

### QS-06 — Scalability: submission volume growth

| Part | Detail |
|---|---|
| **Source** | Growing number of Market Vendors and Verified Buyers as district coverage expands |
| **Stimulus** | Daily price-submission volume grows from ~50/day (single-district pilot) to 2,000/day (multi-district rollout) |
| **Artifact** | Price ingestion, verification, and aggregation pipeline |
| **Environment** | Peak submission periods (e.g., start of harvest across multiple districts simultaneously) |
| **Response** | The system continues to ingest, verify, and aggregate submissions without degrading Fair Price Check performance |
| **Response measure** | At 2,000 submissions/day, Fair Price Check response time (per QS-01) does not increase by more than 20%, and 0% of valid submissions are dropped |

### QS-07 — Auditability: manual Admin overrides

| Part | Detail |
|---|---|
| **Source** | System Admin |
| **Stimulus** | Manually verifies, rejects, or corrects the grade or market-level tag on a price entry (FR-16) |
| **Artifact** | Admin action handler and audit-log subsystem |
| **Environment** | Normal operation |
| **Response** | The system records the action with Admin identity, timestamp, and before/after values in an audit log that cannot be edited or deleted by the same Admin account |
| **Response measure** | 100% of manual verification actions appear in the audit log within 1 second of the action, with zero omissions found when spot-checked against a sample of 50 logged actions |
