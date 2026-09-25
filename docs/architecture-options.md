# Architecture Options — Tsala Market

**Traces to:** `quality-scenarios.md` (QS-01, QS-02, QS-06), Proposal §5 (Scope, assumptions and constraints), `crc-cards.md`, `business-rules.md`

Three quality concerns most strongly shape the architecture for this project. Two are measurable quality scenarios already written in Phase 1; the third is a hard constraint from the approved proposal's scope table, not a scenario, but it drives structure just as directly.

## 1. Quality-driven architectural obligations

| Driver | Requirement (summary) | Architectural obligation |
|---|---|---|
| **QS-01 — Performance** | 95% of Fair Price Check requests return within 5s over USSD; 100% within 10s | The reference price for a bucket (median + outlier-filtered) **cannot be computed from raw entries at request time** once a bucket holds more than a handful of entries — recomputing IQR and a median over every read does not bound response time as data grows. The architecture must separate *write-time aggregation* from *read-time lookup*, so a Fair Price Check is a fast, indexed read against an already-computed value. |
| **QS-06 — Scalability** | At 2,000 submissions/day, response-time increase ≤20%; 0% of valid submissions dropped | Price **ingestion** (submission, unit conversion, verification-condition checks) and price **querying** (Fair Price Check, trend lookup) have different load profiles and different growth curves as the system rolls out across districts. The architecture must let ingestion volume grow without directly degrading query latency — i.e., the two concerns must not compete for the same request-handling capacity under load. |
| **Constraint — dual-channel access, no live telecom/BAMB integration** (Proposal §5) | Farmers reach the system over USSD/SMS (feature phones) *and* a web dashboard; live USSD gateway and BAMB integration are explicitly out of scope for this semester and will be simulated/mocked | Core domain logic (`PriceEntry`, `PriceBucket`, `FairPriceCheckResult`, business rules BR-01–BR-12) **must not know which channel it's being called from**. A channel-adapter boundary is required so the USSD menu flow and the web API can both drive the same domain logic, and so the mocked telecom/BAMB integrations can later be swapped for real ones without touching domain code. |

These three obligations — *precompute, don't recompute*, *decouple ingestion load from query load*, and *keep channels out of the domain layer* — are the criteria both alternatives below are compared against.

## 2. Alternative A — Layered monolith with an in-process aggregate-recompute worker

**Structure:** One deployable service, three layers:
- **Channel adapters** — a USSD menu-flow adapter and a web/REST API adapter, both translating channel-specific input into the same internal commands (e.g. `CheckFairPrice(commodity, district, grade, price, unit)`), and both calling the same application layer. Neither adapter contains business logic.
- **Application/domain layer** — `PriceEntry`, `PriceBucket`, `FairPriceCheckResult`, `ConversionFactorTable`, `SystemConfiguration`, `AuditLogRecord` (per `crc-cards.md`), plus a scheduled/event-triggered **Aggregate Recompute Worker** running in-process. The worker recalculates a bucket's median and outlier-filtered entry set whenever a new entry in that bucket is promoted to Verified, and writes the result to a small `BucketAggregate` cache table (reference price, sample size, submitter count, confidence label, computed-at timestamp).
- **Data layer** — a single relational database holding `PriceEntry`, `BucketAggregate`, `AuditLogRecord`, and configuration tables.

A Fair Price Check request never touches raw `PriceEntry` rows directly — it reads the matching row from `BucketAggregate` (an indexed lookup by commodity/district/grade/market-level), which satisfies QS-01 by construction: the expensive part (median + IQR filtering over potentially hundreds of entries) already happened once, off the request path, not per query.

**Interfaces:** Channel adapters depend only on an application-layer interface (`ICheckFairPrice`, `ISubmitPriceEntry`); the domain layer depends only on a data-access interface, never on the adapters. The mocked USSD gateway and mocked BAMB feed sit behind that same adapter boundary, so replacing a mock with a real integration later changes only the adapter, not the domain.

**Operational cost:** One deployable, one database, one process to monitor and log. The recompute worker needs a safeguard against running twice if the service is ever scaled to two instances (e.g. a simple "only instance 1 runs the worker" flag), but for a semester-scale pilot this is a minor concern, not a redesign.

**Consequences:**
- *Positive:* Meets QS-01 directly; simple consistency story (one database, one transaction boundary); cheapest to build, run, and debug within a semester timeline (Proposal §5 constraint); the channel-adapter boundary independently satisfies the dual-channel obligation.
- *Negative:* `BucketAggregate` values are only as fresh as the last recompute — a short staleness window exists between an entry being Verified and its bucket's cached reference price updating. Under heavy submission bursts (QS-06), the recompute worker and the request-handling adapters compete for the same process's CPU/memory, since they are not independently scalable; only vertical scaling (a bigger single instance) or careful duplication with leader-election is available if ingestion volume grows well past 2,000/day.

## 3. Alternative B — Separate ingestion/aggregation service with an event-driven pipeline

**Structure:** Two independently deployable services connected by a lightweight message queue:
- **Ingestion & Aggregation Service** — owns all `PriceEntry` writes (submission, unit conversion, verification-condition checks per BR-02). On every entry promoted to Verified, it publishes a `PriceEntryVerified` event onto the queue. A consumer (part of the same service or a separate worker) picks up the event, recomputes only the affected bucket, and writes the result to a shared `BucketAggregate` store.
- **Query/API Service** — stateless, serves Fair Price Check and trend-lookup requests by reading `BucketAggregate` directly. Hosts both channel adapters (USSD, web), same adapter-boundary principle as Alternative A.
- **Shared aggregate store** — a database or cache the Query Service reads and the Ingestion Service's consumer writes to; the two services do not share a database for anything else.

**Interfaces:** The two services communicate only through the event queue and the shared aggregate store — there is no direct synchronous call from Query Service to Ingestion Service on the request path, which is what gives this alternative its scaling property.

**Operational cost:** Two deployables, a message broker (even a minimal one, e.g. Redis Streams or a managed queue), and a shared data store — three infrastructure components to provision, configure, and keep available, versus Alternative A's one. Local development and testing require running the broker as well as both services, which is a meaningfully higher setup cost for a five-person student team on a one-semester timeline.

**Consequences:**
- *Positive:* Ingestion load and query load scale independently, which satisfies QS-06 more directly than Alternative A under sustained heavy submission volume — the Query Service's latency is structurally insulated from ingestion bursts. Recompute happens per-event rather than on a batch interval, so staleness is typically lower than Alternative A's worker cycle.
- *Negative:* Introduces a new failure mode (the message broker) that Alternative A does not have — if the broker is unavailable or backs up, `BucketAggregate` staleness can *exceed* Alternative A's predictable recompute interval, working against QS-02 (availability) unless the broker itself is made highly available, which adds still more operational cost. This is a larger and more complex system than the "feasible semester-sized vertical slice" the Proposal §5 constraint calls for, for a scalability benefit (2,000 submissions/day) that the project's synthetic/mocked data (Proposal §5 assumption) cannot yet demonstrate is actually needed.

## 4. Comparison (same criteria, both alternatives)

| Criterion | Alternative A — Layered monolith + in-process worker | Alternative B — Event-driven ingestion/query split |
|---|---|---|
| Meets QS-01 (performance) | Yes — cached read, bounded latency | Yes — cached read, bounded latency |
| Meets QS-06 (scalability) | Partially — vertical scaling only; worker and query compete for resources | Yes — ingestion and query scale independently |
| Meets QS-02 (availability) | One failure domain to keep available (the single service + DB) | Three failure domains (two services + broker); broker outage can exceed A's staleness bound |
| Satisfies dual-channel constraint | Yes — adapter boundary in the application layer | Yes — adapter boundary in the Query Service |
| Operational cost for a 5-person, one-semester team | Low — one deployable, one datastore | High — two deployables, a broker, a shared store |
| Consistency/staleness behaviour | Predictable, bounded by recompute-interval | Lower typical staleness, but unbounded under broker backlog |
| Fit with Proposal §5 ("feasible semester-sized vertical slice") | Direct fit | Conflicts — scope exceeds what a semester vertical slice needs |

## 5. Preliminary direction

Alternative A is the stronger fit for this phase: it satisfies QS-01 and the dual-channel constraint outright, satisfies QS-06 well enough for the volumes this project can realistically demonstrate with synthetic data, and matches the semester-scope constraint the team already committed to in the approved proposal. Alternative B's independent-scaling advantage is real but currently unevidenced — the project has no live submission data yet to show ingestion load actually threatens query latency in practice.

The full decision, including what evidence would justify revisiting this in favour of Alternative B later, is recorded in `decisions/ADR-001-architecture.md`.
