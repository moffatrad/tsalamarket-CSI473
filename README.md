# Laboratory 7 Evidence — Architecture Alternatives and Component Structure

**Team 16 · Tsala Market · CSI473**
**Branch:** `lab-07`
**Date:** 25 September 2026

## What's in this evidence set

| File | What it contains |
|---|---|
| `docs/architecture-options.md` | Three quality-driven architectural obligations (from QS-01, QS-06, and the dual-channel constraint), two realistic alternatives compared against the same criteria, and a preliminary direction. |
| `models/component-architecture.mmd` (+ `.svg`) | The component/module diagram for the chosen alternative: channel adapters, application services, domain model, the aggregate-recompute worker, the data layer, and three explicit boundaries (trust, security, failure). |
| `decisions/ADR-001-architecture.md` | The formal decision: context, the two alternatives, consequences (positive and negative), and four concrete pieces of evidence that would trigger reconsideration. |
| `docs/quality-to-architecture.md` | All seven Phase 1 quality scenarios checked against the architecture, not just the three that drove it — 4 fully addressed, 2 partially, 1 (availability) not yet addressed at all. |

## Studio plan cross-check

| Time block | Work | Evidence produced |
|---|---|---|
| 00–20 | Translate quality scenarios into architectural obligations | `architecture-options.md` §1 |
| 20–45 | Compare at least two feasible alternatives | `architecture-options.md` §2–4 |
| 45–75 | Component/module diagram | `component-architecture.mmd`/`.svg` |
| 75–95 | ADR-001 | `ADR-001-architecture.md` |
| 95–110 | Review coupling, data ownership, security/failure boundaries | Boundary annotations in `component-architecture.mmd`; Gap 1/2 in `quality-to-architecture.md` |
| 110–120 | Revise, commit, record highest risk | This README's exit record, below |

## Exit record

**Which quality requirement most influenced the architecture?**

**QS-01 (Performance)** — the requirement that 95% of Fair Price Check requests return within 5 seconds over USSD, with 100% within 10 seconds. This single scenario is the direct cause of the core architectural decision in ADR-001: computing a bucket's median and outlier-filtered reference price from raw entries on every request cannot guarantee that bound as the dataset grows, so the entire write-time-aggregation structure (`AggregateRecomputeWorker` writing to a `BucketAggregate` cache, `FairPriceCheckService` only ever reading from it) exists to satisfy QS-01. QS-06 (scalability) and the dual-channel constraint shaped the architecture too, but QS-01 is what ruled out the simplest possible design (recompute-per-request) before either alternative in `architecture-options.md` was even drafted.

**What evidence would cause the team to revise the decision?**

The four triggers already recorded in ADR-001 are restated here as the answer to this exit record, not duplicated with new wording, since they are the actual answer:

1. Measured submission volume approaching or exceeding 2,000/day with **observed** (not just theoretical) degradation in Fair Price Check response time beyond QS-06's 20% bound.
2. Measured staleness in `BucketAggregate` that exceeds what BR-05's 30-day pooling window tolerates in practice.
3. A missed QS-02 uptime target where root-cause analysis shows the single-deployable coupling of ingestion and query was a contributing factor.
4. Project scope growing beyond the current semester vertical slice, removing the constraint that favoured Alternative A's operational simplicity in the first place.

Of these, **#1 is the one most likely to surface first** once implementation begins, since it is the one directly tied to the risk named as highest in ADR-001 (shared resource contention between the worker and the channel adapters) — it is therefore the one to watch most closely during Phase 2 load testing, well before the others become relevant.
