# Pattern Decisions — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 9**
**Traces to:** `ADR-001-architecture.md` · `component-architecture.mmd` · `logical-data-model.md` · `core-operation.md` · `deployment.md` · `failure-recovery.md` · `data-integrity.md` · `crc-cards.md`

Each decision below starts from a problem found in this project's own artefacts, names the classes and interfaces that take part, states what the pattern costs, and says which test will show it works. The participants listed here are the names the detailed class model (`models/detailed-class-design.*`) and the code in `src/interfaces-or-ports/` must use.

## 1. Design problems found

| ID | Problem | Where it shows up |
|---|---|---|
| **DP-1** | **Persistence coupling.** Domain and service logic must be testable without a live database, and the code must respect two different database roles (`app`, `worker`). | `failure-recovery.md` tests T3 and T7 need an injected database failure; `deployment.md` §3 gives `app` read-only access to `BucketAggregate` and `AuditLogRecord` insert-only access (DC-10, DC-18, DC-19) |
| **DP-2** | **External formats.** The USSD gateway sends session callbacks in its own format; the web client sends JSON. Both must reach one operation and produce identical results and error codes. The real gateway does not exist yet. | ADR-001 obligation 3 (domain must not know the channel); `core-operation.md` (same codes on both channels); `deployment.md` (simulator now, real gateway later) |
| **DP-3** | **Secondary effects.** Several different changes must lead to the same follow-up: recompute one or more `BucketAggregate` rows. The code that changes an entry should not know about the worker. | Component diagram (`PriceEntry` → `AggregateRecomputeWorker`); DI-5 lists five triggers; OI-2 |
| **DP-4** | **Object creation and invariants.** A result must never exist without a flag, confidence label and disclaimer; a stored price must always be in P/kg; an ungraded entry must default to B. | BR-10, BR-03, BR-04; DC-04 to DC-06, DC-17 |
| **DP-5** | **Variable behaviour.** (a) Fairness thresholds change by configuration. (b) Verification can happen three ways (registered account, corroboration, Admin confirmation), and DI-1 and DI-3 show those rules are still being settled. | BR-09, FR-17; BR-02, DI-1, DI-3 |

## 2. Decisions

DP-1 to DP-3 each get a named pattern. DP-4 and DP-5 are deliberately solved **without** one (§4).

| # | Problem | Decision | Status |
|---|---|---|---|
| **P1** | DP-1 | **Repository behind ports**, split along the database roles | Accepted |
| **P2** | DP-2 | **Adapter** per channel, translating into one **command** object | Accepted |
| **P3** | DP-3 | **Domain events** published after commit, with a **coalescing recompute queue** | Accepted |
| — | DP-4 | Constructors that refuse invalid state (no named pattern) | Accepted (technique) |
| — | DP-5 | Plain configuration values and one ordinary method (no Strategy) | Accepted, revisit on trigger |

### P1 — Repository behind ports, split by database role

**Why it fits here.** The database role table already divides access: the request path may only read `BucketAggregate`; only the worker writes it; nothing may update `AuditLogRecord` or `FairPriceCheckQuery`. If the code uses one general-purpose data-access class, none of that shows in the design and a later change could break it silently. Giving each access pattern its own small interface makes the privilege rules visible in the code and lets tests replace the database.

| Participant (port) | Used by | Methods | Database role |
|---|---|---|---|
| `BucketAggregateReader` | `FairPriceCheckService`, `TrendLookupService` | `find(bucketKey)` | `app` (read-only) |
| `BucketAggregateWriter` | `AggregateRecomputeWorker` | `upsert(aggregate)` | `worker` |
| `BucketInputSource` | `AggregateRecomputeWorker` | `qualifyingEntries(bucketKey, window)` | `worker` (read-only) |
| `PriceEntryRepository` | `PriceSubmissionService`, `AdminService` | `insert`, `find`, `updateVerification`, `updateClassification`, `findCorroborationCandidates` | `app` |
| `QueryLog` | `FairPriceCheckService` | `findByIdempotencyKey`, `insert` | `app` (insert and select only) |
| `AuditLog` | `AdminService`, `AggregateRecomputeWorker` | `append` | both (insert only) |
| `ConfigurationStore` | services, worker | `get(key)`, `set(key, value)` | `app` writes, `worker` reads |
| `ConversionFactors` | `PriceSubmissionService`, `FairPriceCheckService` | `kgPerUnit(commodity, unit)`, `unitsFor(commodity)` | `app` |
| `Transaction` | all services | `run(work)` — one database transaction around `work` | — |

`AuditLog` has **no** update or delete method, and `QueryLog` has no update method, so the code cannot express what DC-18 and DC-19 forbid even before the database refuses it. `Transaction.run` is how DC-16 (check and log in one transaction) and DC-20 (Admin change and audit record together) are made hard to get wrong.

**Cost.** About nine interfaces, each with an in-memory fake and a real database implementation to keep in step. Transactions are the usual leak: an in-memory fake that does not roll back would make tests pass for the wrong reason.
**Consequence accepted.** More files and a discipline to keep fakes honest, in return for visible privilege boundaries and database-free tests.

**Confirming test.** (1) A shared *repository contract* test suite (insert then find, unique key rejected, rollback leaves nothing) runs against **both** the fake and the real database implementation. (2) `failure-recovery.md` T3 and T7 run against the fake with a failure injected at commit; T4 (process kill after commit) needs the real database and a real process. (3) An architecture test fails the build if any class in the domain or service packages imports a database driver.

### P2 — Adapter per channel, one command object

**Why it fits here.** Only one class should know the USSD gateway's callback format, because that format is unknown today and will change when the real gateway replaces the simulator. The contract promises identical outcomes on both channels, so everything after translation must be shared, including validation.

| Participant | Role |
|---|---|
| `UssdCallbackAdapter` | The only class that knows gateway field names and session semantics. Turns a callback into a `CheckFairPriceCommand`, derives the idempotency key, and asks `UssdScreenPresenter` to render the outcome |
| `WebApiAdapter` | Turns an HTTP request into the same command; passes the client's `Idempotency-Key` through |
| `CheckFairPriceCommand` | Immutable carrier of `commodity`, `district`, `grade?`, `offeredPrice`, `unit`, `idempotencyKey?`. Holds raw values only |
| `ICheckFairPrice` | The port both adapters call (`checkFairPrice(command) → FairPriceCheckOutcome`) |
| `FairPriceCheckOutcome` | Either a `FairPriceCheckResult` or an error with a stable code from `core-operation.md` §5 |
| `UssdScreenPresenter`, `JsonPresenter` | Turn an outcome into short screens (using `disclaimer_short`) or into the JSON body |
| `UssdSessionStore` | In-memory session state, including the check counter used for the key (limitation L2 in `failure-recovery.md`) |
| `IdempotencyKeyDeriver` | HMAC of session id and check counter (DC-24) |

**Rule that keeps this honest:** validation (contract steps 1–6) lives in `FairPriceCheckService`, **not** in the adapters. If adapters validated for themselves, the two channels would eventually disagree on error codes.

**Cost.** Two presenters to keep consistent, and a command type that duplicates the request fields. The USSD session store is the weak spot: it is in memory and lost on a crash.
**Consequence accepted.** A second place to change whenever an outcome field is added, in exchange for swapping the simulator for the real gateway by replacing one class.

**Confirming test.** A parametrised contract test sends the same set of inputs through both adapters and asserts the **same outcome and error code** for each of the ten codes. A second check replaces the simulator's callback format with a different one and confirms only `UssdCallbackAdapter` had to change.

### P3 — Domain events with a coalescing recompute queue

**Why it fits here.** DI-5 found that five different changes must lead to the same follow-up (recompute a bucket): an entry becoming Verified, an entry ageing past a boundary, a grade or market-level correction (two buckets), an exclusion, and a configuration change (all buckets). If each of those code paths called the worker directly, the worker would be wired into `PriceSubmissionService`, `AdminService` and configuration handling, and a sixth trigger would mean editing all of them. Events keep that knowledge in one place.

| Participant | Role |
|---|---|
| `BucketKey` | Value object (commodity, district, grade, market level) identifying one `BucketAggregate` row |
| `BucketInvalidated` | The single event: "this `BucketKey` needs recomputing", with a `reason` (verified, aged, corrected, excluded, configuration) for logging |
| `EventPublisher` | Port the services use to publish after their transaction commits |
| `RecomputeQueue` | In-process set of pending `BucketKey`s. **Coalesces:** publishing a key already waiting adds nothing |
| `AggregateRecomputeWorker` | Takes keys from the queue, reads `BucketInputSource`, calculates the median and outlier exclusion, writes `BucketAggregateWriter`, appends exclusions to `AuditLog` |
| `DailySweep` | Scheduled producer: marks every bucket whose entries crossed a 7- or 30-day boundary since its last `computed_at` |

Services publish **after** commit, never before: publishing first could trigger a recompute that cannot see the change, or one for a transaction that then rolled back.

**Cost.** In-process events are lost if the process dies between commit and recompute, so a bucket can serve a stale value until the next sweep. Event flow is also harder to follow than a direct call.
**Consequence accepted.** Staleness after a crash is bounded by the sweep interval, which therefore doubles as the safety net, not only the ageing mechanism. The interval is a decision for the ADR-001 update and must not be longer than the staleness the team will accept. To keep flow traceable, every recompute logs its `BucketKey` and `reason`.

**Confirming test.** (1) 100 `BucketInvalidated` events for one key produce **one** recompute. (2) A grade correction that moves an entry between buckets recomputes **both**. (3) Commit a verification, kill the process before the recompute runs, restart, and confirm the next sweep recomputes the bucket and `computed_at` advances. (4) A rolled-back transaction publishes no event.

## 3. Summary of decisions against problems

| Problem | Pattern | Participants visible in the model | Cost | Test |
|---|---|---|---|---|
| DP-1 | P1 Repository / ports | Nine ports above | Fakes and real implementations to keep in step | Contract suite on fake and real DB; T3, T7; no-driver-import architecture test |
| DP-2 | P2 Adapter + command | `UssdCallbackAdapter`, `WebApiAdapter`, `CheckFairPriceCommand`, `ICheckFairPrice`, presenters | Duplicated presenters; in-memory session state | Same inputs through both adapters give same codes; swap gateway format touching one class |
| DP-3 | P3 Domain events + coalescing queue | `BucketInvalidated`, `RecomputeQueue`, `AggregateRecomputeWorker`, `DailySweep` | Lost events after a crash; harder flow tracing | 100 events → one recompute; both buckets on correction; crash then sweep recovers |

## 4. Solved without a named pattern

- **DP-4 (invariants).** `FairPriceCheckResult` has a single constructor that requires a flag, confidence label and both disclaimer texts, and refuses to build otherwise. `PriceEntry` takes a price and a conversion factor and stores only the P/kg value. Grade defaults inside the constructor. This is ordinary defensive construction, not a Factory or Builder, because there is exactly one valid way to build each object.
- **DP-5(a) (thresholds).** Fairness thresholds are a small `FairnessThresholds` value object read from `ConfigurationStore`. They differ by *value*, not by *behaviour*, so there is nothing for a Strategy to vary.
- **DP-5(b) (verification rules).** One ordinary method in `PriceSubmissionService` checks the three conditions in order. See R4 for when this should change.

## 5. Considered and rejected

| # | Candidate | Why rejected | Reconsider if |
|---|---|---|---|
| **R1** | **Strategy** for fairness classification | The thresholds are data. A Strategy hierarchy (`DefaultFairness`, `StrictFairness`…) would add classes that differ only in three numbers, and would hide the BR-09 rule that thresholds apply **uniformly** across commodities | A rule appears that changes the *formula*, not the numbers, for some commodity |
| **R2** | **CQRS** (separate read and write models and stores) | `BucketAggregate` is already a precomputed read model in the same database (ADR-001). Splitting stores adds the second failure domain and eventual consistency that ADR-001 rejected in Alternative B | ADR-001 reconsideration trigger 1 or 2 fires (measured load or staleness) |
| **R3** | **Factory / Builder** for `FairPriceCheckResult` | One construction path, five fields. A Builder would allow a partly built result to exist, which BR-10 says must never happen | Results gain optional sections or several construction paths |
| **R4** | **Strategy / Chain of responsibility** for the three verification conditions | Three conditions with one combination rule (any one is enough) do not justify extra classes **yet**. DI-1 and DI-3 are still changing what those conditions mean, so abstracting them now would freeze guesses | DI-1 and DI-3 are decided and a fourth condition is proposed, or the conditions need configuring per district |
| **R5** | **Caching Proxy / Decorator** around `BucketAggregateReader` | `BucketAggregate` **is** the cache. A second cache layer would add a staleness source on top of the one P3 already manages | QS-01 is missed despite the single-row read |

Technology-level rejections (for example an ORM, a dependency-injection container, a message broker) are recorded with the framework decision in `docs/framework-decision.md` and `decisions/ADR-002.md`.

## 6. Effects on earlier artefacts

These refinements follow from the decisions above and should be reflected in the detailed class model. They are noted here, not silently applied.

- **CRC-01 (`PriceEntry`):** its responsibility to report changes to `AuditLogRecord` moves to `AdminService`. With P1, domain objects do not hold persistence ports, which keeps them testable on their own.
- **Component diagram and ADR-001:** `PriceEntry` no longer "raises `PriceEntryVerified`" directly. Services publish `BucketInvalidated` after commit (P3). The worker's triggers widen from one to five, as DI-5 proposes, and the sweep interval needs deciding.
- **CRC-02 (`PriceBucket`):** its pooling, outlier and median behaviour stays, but is carried out as a pure calculation over entries supplied by `BucketInputSource`, not by an object that reads the database.

## 7. Exit record (draft)

- **Interface boundary with the greatest benefit:** the P1 ports split by database role, because they turn the database privilege rules (DC-10, DC-18, DC-19) and the transaction rules (DC-16, DC-20) into something the code cannot easily violate, and they make the failure tests possible without a real outage.
- **Cost:** about nine interfaces with two implementations each, and the risk of a fake that behaves differently from the real database.
- **Test that confirms it works:** the shared repository contract suite passing against both the fake and the real database, plus the architecture test that fails the build if core packages import a database driver.
