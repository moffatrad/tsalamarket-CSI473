# Quality-to-Architecture Traceability — Tsala Market

**Chain:** Quality scenario → architectural obligation → component/element → status
**Sources:** `quality-scenarios.md`, `docs/architecture-options.md`, `models/component-architecture.mmd`, `decisions/ADR-001-architecture.md`

This matrix checks all seven Phase 1 quality scenarios against the architecture decided in ADR-001 — not just the three that drove the decision (QS-01, QS-02, QS-06), so gaps in the scenarios the architecture wasn't explicitly designed for are visible rather than assumed away.

## Core matrix

| QS | Attribute | Response measure (summary) | Architecture element(s) | How it's addressed | Status |
|---|---|---|---|---|---|
| **QS-01** | Performance | 95% of Fair Price Check requests return within 5s; 100% within 10s | `BucketAggregate` table, `PriceBucket` (read path), `FairPriceCheckService` | The reference price is never computed live from raw entries on the request path — `FairPriceCheckService` reads a precomputed `BucketAggregate` row via an indexed lookup. This is the entire reason ADR-001 chose a write-time-aggregation architecture over a naive recompute-per-request design. | **Addressed by design** |
| **QS-02** | Availability | ≥99% uptime monthly; unplanned outages restored within 30 minutes | Whole service (single deployable) | Not addressed by the current architecture — explicitly named as a **negative consequence** in ADR-001: one deployable means an outage takes down ingestion and query together. No redundancy/failover mechanism is designed yet. | **Gap — see below** |
| **QS-03** | Usability | ≥80% of first-time USSD users complete a check unaided in ≤5 screens | `USSDAdapter` | The adapter owns menu flow and session state in isolation from domain complexity — `USSDAdapter` translates USSD input into the same `ICheckFairPrice` call the web adapter uses, so the screen count is a property of the adapter's own menu design, not of the domain logic underneath. The 5-screen budget is a design constraint on `USSDAdapter` specifically, not yet verified against an actual menu-flow design. | **Partially addressed — adapter isolated, menu flow not yet designed** |
| **QS-04** | Security / Privacy | 100% of audited records contain no farmer data more precise than district level; unauthorised access rejected | `AdminService` / `IAdminActions`, security boundary in `component-architecture.mmd` | The security boundary restricts writes to `AuditLogRecord` and `SystemConfiguration` to `AdminService` behind an authenticated-role interface. However, the district-level-only storage constraint (BR-11) is a **data-modelling** obligation, not a component-boundary one — the `PriceEntry` table's schema does not yet exist in enough detail to confirm it stores district rather than finer-grained location. | **Partially addressed — access boundary exists, schema-level enforcement not yet designed** |
| **QS-05** | Reliability / Data integrity | 100% of entries beyond 1.5×IQR excluded and queued for review within 1 minute | `AggregateRecomputeWorker`, `AuditLogRecord` | The worker performs outlier exclusion (BR-07) as part of every recompute triggered by a `PriceEntryVerified` event, and writes excluded entries to `AuditLogRecord` for review — the "within 1 minute" bound depends on the worker running promptly after the triggering event, which is the same mechanism QS-01 relies on. | **Addressed by design** |
| **QS-06** | Scalability | At 2,000 submissions/day, response-time increase ≤20%; 0% dropped | `AggregateRecomputeWorker` vs. `Channel Adapters` (shared process) | Read/write separation via `BucketAggregate` insulates query performance from ingestion *volume* to a point, but the worker and adapters share one process — ADR-001 names this as the **single highest architectural risk carried forward**, since ingestion and query are not independently scalable the way the rejected Alternative B would have made them. | **Partially addressed — risk explicitly tracked in ADR-001** |
| **QS-07** | Auditability | 100% of manual Admin actions logged within 1 second; zero omissions on spot-check | `AdminService`, `AuditLogRecord` table (append-only) | `AdminService` is the only component permitted to write `AuditLogRecord`, and the table is modelled as append-only in the data layer, directly satisfying BR-12's immutability requirement. | **Addressed by design** |

## Gaps identified

Two scenarios are only partially addressed, and one is not addressed at all by the current architecture. These are carried forward honestly rather than implied to be solved by the component diagram's existence:

### Gap 1 — QS-02 (Availability) has no architectural answer yet
The single-deployable structure chosen in ADR-001 was a deliberate trade favouring operational simplicity (Proposal §5's semester-scope constraint) over availability. This is not an oversight — it is a named negative consequence in ADR-001 — but it means **no mechanism exists yet** to meet the 99% uptime / 30-minute restoration target beyond "keep the one process running." Standard mitigations (process supervision/auto-restart, database backups with a restore procedure) have not been designed. This should be picked up explicitly once implementation begins, rather than assumed to fall out of the architecture for free.

### Gap 2 — QS-04's district-level-only constraint (BR-11) is a data-modelling obligation, not yet a schema
The component diagram shows *who* may write farmer-related data (the security boundary around `AdminService`), but not *what granularity* `PriceEntry` actually stores. BR-11 requires district-level-only location; this needs to be enforced in the logical data model (Laboratory 9, `docs/quality-to-architecture.md`'s natural successor), not assumed satisfied because a component diagram exists.

### Gap 3 — QS-06's partial coverage is already tracked, not new
This is not a new finding — ADR-001 already names the worker/adapter resource-contention risk as the single highest architectural risk carried forward, with four concrete reconsideration triggers. It is included in this matrix for completeness, so a reader checking quality-scenario coverage does not have to cross-reference ADR-001 separately to learn that QS-06 is only partially satisfied.

*4 of 7 quality scenarios are fully addressed by the current architecture; 2 are partially addressed with the gap explicitly named; 1 (QS-02) has no architectural mechanism yet. This 4/2/1 split, not a claim of full coverage, is the honest status to carry into Laboratory 8.*
