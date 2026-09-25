# ADR-001: Layered monolith with an in-process aggregate-recompute worker

**Status:** Accepted (for Phase 2 implementation; open to revision — see "Evidence that would trigger reconsideration" below)
**Date:** 25 September 2026
**Traces to:** `docs/architecture-options.md`, `models/component-architecture.mmd`, `quality-scenarios.md` (QS-01, QS-02, QS-06), Proposal §5 (Scope, assumptions and constraints), `crc-cards.md`, `business-rules.md`

## Context

Three architectural drivers were identified from the Phase 1 artefacts (full derivation in `docs/architecture-options.md`):

1. **QS-01 (Performance):** 95% of Fair Price Check requests must return within 5 seconds over USSD; 100% within 10 seconds.
2. **QS-06 (Scalability):** at 2,000 submissions/day, Fair Price Check response time must not degrade by more than 20%, and 0% of valid submissions may be dropped.
3. **Constraint (Proposal §5):** the system must serve both a USSD/SMS channel and a web dashboard, with no live telecom or BAMB integration this semester (both are mocked); and the team must deliver a "feasible semester-sized vertical slice", not the full multi-tier concept.

The core technical tension these create: computing a Fair Price Check reference price requires pooling a bucket's Verified entries, excluding statistical outliers (1.5×IQR), and taking a median (BR-05, BR-07, BR-08) — an operation whose cost grows with bucket size. Doing this from raw entries on every request cannot guarantee QS-01's bound as the dataset grows, and doing it inline with entry submission risks submission volume (QS-06) degrading query latency if the two are not architecturally separated.

## Decision

We will build Tsala Market as **a single deployable, layered monolith**, structured as:

- **Channel Adapters** (USSD Adapter, Web/REST API Adapter) — translate channel-specific input into calls against four channel-agnostic interfaces (`ICheckFairPrice`, `ISubmitPriceEntry`, `ITrendLookup`, `IAdminActions`). No business logic lives in this layer.
- **Application services** (`FairPriceCheckService`, `PriceSubmissionService`, `TrendLookupService`, `AdminService`) — each implements one interface and orchestrates the domain model.
- **Domain model** (`PriceEntry`, `PriceBucket`, `FairPriceCheckResult`, `ConversionFactorTable`, `SystemConfiguration`, `AuditLogRecord`, per `crc-cards.md`).
- **An in-process `AggregateRecomputeWorker`**, triggered whenever a `PriceEntry` is promoted to Verified (BR-02), which recomputes the affected bucket's median and outlier-filtered sample and writes it to a `BucketAggregate` cache table.
- **A single relational database** holding `PriceEntry`, `BucketAggregate`, `AuditLogRecord`, and `SystemConfiguration`.

A Fair Price Check request reads only from `BucketAggregate` — an indexed lookup — never recomputing the median/IQR filter live. The full component structure is diagrammed in `models/component-architecture.mmd`.

## Alternatives considered

**Alternative B — Event-driven split between a separate Ingestion & Aggregation Service and a Query/API Service**, connected by a message queue, with the two services scaling independently. Full comparison against the same three criteria (QS-01, QS-06, and the dual-channel constraint) is in `docs/architecture-options.md` §4. In summary: Alternative B scales ingestion and query independently more cleanly than Alternative A, but requires two deployables plus a message broker — three infrastructure components to provision and keep available, versus Alternative A's one — and introduces a new failure mode (the broker) with no corresponding demonstrated need, since the project's data is synthetic/mocked (Proposal §5) and has never actually shown ingestion load threatening query latency.

No other alternative was considered a realistic fit for this project's scale; a fully synchronous, no-caching design (recompute on every Fair Price Check read) was rejected outright rather than treated as a second alternative, since it cannot satisfy QS-01 once a bucket holds more than a small number of entries — it was a starting point that motivated this decision, not a competing option.

## Consequences

### Positive
- QS-01 is met by construction: a Fair Price Check is a single indexed read against a precomputed value, not a live aggregation.
- Lowest operational cost of any option considered — one deployable, one database, one process to monitor — fitting the Proposal §5 constraint that the team deliver a feasible semester-sized vertical slice rather than the original multi-tier concept.
- The channel-adapter boundary satisfies the dual-channel constraint directly: USSD and web both drive the same four interfaces, and the mocked USSD Gateway can later be replaced with a real integration by changing only `USSDAdapter`, not the application or domain layers.
- Consistency is simple to reason about: one database, one transaction boundary, no distributed-consistency handling required.

### Negative
- **Staleness window:** `BucketAggregate` values lag behind the most recent Verified entry by however long the worker takes to run after a `PriceEntryVerified` event. This is judged acceptable against BR-05's 30-day pooling window, but it is a genuine, disclosed trade-off, not a non-issue.
- **Shared resource contention under load:** the `AggregateRecomputeWorker` and the request-handling adapters run in the same process. Under a sustained heavy submission burst (approaching or exceeding QS-06's 2,000/day figure), the worker's recompute work and incoming Fair Price Check reads compete for the same CPU/memory, and only vertical scaling (a larger single instance) is available — Alternative A does not scale ingestion and query independently the way Alternative B would.
- **Single point of failure:** because it is one deployable, an outage of the service takes down both ingestion and query together, whereas Alternative B could in principle keep the Query Service available even if ingestion were degraded. This is a deliberate trade against QS-02 (availability) in exchange for the operational-simplicity benefit above.
- **Scaling to two instances requires a safeguard:** if the service is ever horizontally scaled for availability, the worker must not run twice concurrently (double recompute is wasteful, not incorrect, but wasteful work should still be guarded against) — a "single active worker" mechanism will be needed and is not yet designed.

## Evidence that would trigger reconsideration

This decision is not final for the life of the project. We will revisit it in favour of something closer to Alternative B if any of the following is observed once real (or realistic load-tested) data exists:

1. **Measured submission volume approaches or exceeds QS-06's 2,000/day figure** and the single-instance worker measurably degrades Fair Price Check response time beyond the 20% bound QS-06 allows — i.e., the resource-contention risk named above is actually observed, not merely theoretical.
2. **Measured staleness exceeds what BR-05's 30-day window tolerates in practice** — for example, if the recompute worker's queue backs up long enough that farmers are seeing reference prices meaningfully out of date relative to very recent Verified submissions.
3. **QS-02's 99% uptime target is missed** and root-cause analysis shows the coupling of ingestion and query into one deployable was a contributing factor (e.g. a spike in submission processing caused the whole service, including reads, to become unresponsive).
4. **The project's scope grows beyond the current semester vertical slice** (e.g. a Phase 2 extension or post-course continuation) to the point where the "feasible semester-sized vertical slice" constraint that favoured Alternative A's simplicity no longer applies.

If none of these are observed by the end of Phase 2, Alternative A is expected to remain the right choice: its costs are lower and its capabilities are sufficient for the load this project can actually demonstrate.

## Risk carried forward

The single highest architectural risk from this decision is the **shared resource contention** point above: the in-process worker and channel adapters are not independently scalable. This is the risk to monitor most closely once implementation begins, and it is the first thing to check if QS-01 or QS-06's measured evidence starts trending toward the reconsideration thresholds in the section above.
