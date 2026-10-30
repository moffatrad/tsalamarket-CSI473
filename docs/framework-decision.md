# Framework Decision — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 9**
**Status:** Proposed — depends on assumption A1 below, which the team must confirm before this becomes ADR-002
**Traces to:** `ADR-001-architecture.md` · `pattern-decisions.md` · `detailed-class-design.md` · `core-operation.md` · `deployment.md` · `data-integrity.md` (DC-05, DC-16, DC-18, DC-19, DC-22)

## 1. What has to be decided

The earlier artefacts are deliberately language-neutral. To start the implementation the team needs: a language and web framework, a database, a way to talk to the database, a test setup, and a rule for adding dependencies. The architecture does not change with these choices (ports, adapters, one deployable, one database); they only decide the tools.

**Assumption A1 (not verified):** at least some team members can work in Python. I do not know the team's strongest language, and for a one-semester project that matters more than any technical difference below. If A1 is wrong, §7 shows the equivalent choices in other languages, and everything in `pattern-decisions.md` still applies unchanged.

## 2. Criteria

The same criteria are used for every option. They come from this project's own constraints.

| ID | Criterion | Comes from |
|---|---|---|
| **C1** | The database enforces our integrity rules: separate roles, `INSERT`-only tables, column-level update rights, `CHECK` and `UNIQUE` constraints | DC-18, DC-19, DC-22, DC-07, DC-15; deployment B3 |
| **C2** | Exact decimal arithmetic is built in, with half-up rounding to 2 places | FR-02, DC-05 (152 per 20 kg crate must store exactly 7.60) |
| **C3** | Ports can be expressed simply, and the dependency rule can be checked automatically | `pattern-decisions.md` P1; the no-driver-import architecture test |
| **C4** | The framework does not impose its own validation or error format on the contract's stable codes | `core-operation.md` §2 and §5 |
| **C5** | Light to run: one process, one database | ADR-001 |
| **C6** | The team can deliver it in one semester | Proposal §5 (unverified, see A1) |

## 3. Decision

| Choice | Decision |
|---|---|
| Language | **Python** (one pinned version, 3.12 or later), with type hints checked by `mypy` |
| Web framework | **Flask**, used only inside the adapters, served by `gunicorn` with **one worker process** and several threads |
| Database | **PostgreSQL** (a currently supported major version) |
| Database access | **Hand-written parameterised SQL** through `psycopg`, inside the repository implementations. **No ORM** (see R1) |
| Ports | `typing.Protocol` classes in `src/interfaces-or-ports/`, so in-memory fakes satisfy a port without inheriting from it |
| Wiring | A single **composition root** (`src/main.py`) that constructs concrete classes and passes them to constructors. **No dependency-injection container** (see R2) |
| Tests | `pytest`; repository contract tests run against the fake **and** a real PostgreSQL; contract tests check responses against `core-operation.yaml` |
| Dependency-rule check | `import-linter` contracts, run in CI |
| Local environment | Docker Compose: an application container and a PostgreSQL container on **separate networks**, keeping the B3 boundary from `deployment.md` |

### Why these, against the criteria

| Option | C1 DB integrity | C2 Decimals | C3 Ports and rule check | C4 Contract not overridden | C5 Light | C6 Delivery |
|---|---|---|---|---|---|---|
| **Python + Flask + PostgreSQL (chosen)** | Yes | Yes — `decimal.Decimal` with `ROUND_HALF_UP` | Yes — `Protocol` + `import-linter` | Yes — Flask validates nothing unless asked | Yes | Unverified (A1) |
| Python + FastAPI | Yes | Yes | Yes | **Partial** — automatic request validation returns its own 422 error shape, which clashes with our 400/422 meanings; it must be switched off or overridden | Yes | Unverified |
| TypeScript + Express | Yes | **Partial** — `number` is binary floating point; needs a decimal library and discipline | Yes — `dependency-cruiser` | Yes | Yes | Unverified |
| Java + Spring Boot | Yes | Yes — `BigDecimal` | Yes — ArchUnit | **Partial** — default error handling must be replaced | **No** — heavier runtime and a container-centred design | Unverified |

Flask is chosen over FastAPI for one concrete reason: the contract defines its own validation order and error codes, and the adapters are meant to translate and nothing more (P2). FastAPI's strength, automatic validation from request models, would pull validation into the adapter and produce responses the contract does not describe. Flask gives no such help, which here is a benefit.

### Database choice

| Option | Roles and column grants | `CHECK` / `UNIQUE` | Decision |
|---|---|---|---|
| **PostgreSQL** | Yes | Yes | **Chosen** |
| MySQL 8 | Yes | Yes (`CHECK` enforced from 8.0.16) | Meets C1 as well. PostgreSQL is chosen mainly because schema changes can be rolled back as part of a migration, which MySQL cannot do; the difference is small |
| SQLite | **No** — it has no users or privileges | Yes | Rejected (R3) |

## 4. Consequences

**Accepted costs**
- **Hand-written SQL:** roughly fifteen queries across the nine ports, each parameterised (never string-built), with the mapping from rows to domain objects written by hand.
- **No automatic API validation:** the validator and the contract tests carry that work.
- **One gunicorn worker:** the in-process recompute worker (ADR-001) must run exactly once, so the application cannot be scaled across worker processes without the "single active worker" safeguard ADR-001 already flagged. This is the same limitation as ADR-001's highest risk, not a new one.
- **Flask is synchronous:** adequate for the loads in QS-01 and QS-06, which are small, but a long recompute must run on its own thread so it does not hold request threads.
- **Python's typing is checked, not enforced at run time:** `mypy` in CI is the safeguard.

**Gained:** exact decimals without a library, fakes that need no base class, the dependency rule checked automatically, and no framework behaviour between the contract and the code.

## 5. Dependency management

| Rule | Detail |
|---|---|
| **Declared in one place** | `pyproject.toml` lists direct dependencies with version ranges |
| **Locked** | A lock file with hashes is committed (generated with `pip-compile --generate-hashes` or an equivalent). CI and Docker install **only** from the lock file |
| **Runtime kept small** | Four direct runtime dependencies: Flask, gunicorn, psycopg, and the standard library for everything else (HMAC, hashing, JSON, decimals) |
| **Development separate** | `pytest`, `mypy`, `import-linter`, `ruff`, an OpenAPI validator for the contract tests, and `pip-audit` — never installed in the runtime image |
| **Where dependencies may be imported** | Flask only in `src/adapters/`; psycopg only in `src/infrastructure/`. `import-linter` fails the build if `src/domain/` or `src/application/` import either (this is the dependency rule from `detailed-class-design.md` §1) |
| **Adding a runtime dependency** | Needs a one-line entry in the table below, saying what it is for and what was considered instead |
| **Updates and advisories** | `pip-audit` runs in CI; dependencies are reviewed at the start of each phase, not mid-task |
| **Runtime pinned** | Python version fixed in `.python-version` and the Docker image tag; PostgreSQL major version fixed in Docker Compose |

| Dependency | Used for | Considered instead |
|---|---|---|
| Flask | Routing and request/response for the web adapter and USSD callback endpoint | FastAPI (rejected on C4, §3) |
| gunicorn | Production-style server, one worker process | Flask's development server (not for use beyond development) |
| psycopg | PostgreSQL driver for the SQL repositories | An ORM (R1) |

## 6. Explicit rejection decisions

### R1 — No ORM or entity-mapping layer *(the main rejection)*

**What was considered:** an object-relational mapper (SQLAlchemy ORM, or the equivalent in another language) with `PriceEntry`, `BucketAggregate` and the other tables as mapped classes.

**Why rejected, using this project's evidence:**
1. **Hidden writes against DC-22.** Mapped objects track their own changes and write any changed column when a session flushes. The design lets `app` update only classification and verification columns, and wants price fields never to change. An ORM would make a stray assignment to `price_per_kg` a silent database call, instead of something the code cannot express.
2. **Hidden reads against the dependency rule.** Lazy loading and auto-flush put database access inside objects that the class design says must depend on nothing. It would also blur the transaction boundary that DC-16 and DC-20 depend on.
3. **The domain classes are not the tables.** `PriceBucket` and `FairPriceCheckResult` have no table of their own (`logical-data-model.md`), `BucketAggregate` is a cache written by one role and read by another, and `QueryLogRecord` is insert-only. Mapping these as entities would force the database shape onto the domain.
4. **Two database roles.** The design uses separate `app` and `worker` roles. That is a few lines with two plain connection pools; with an ORM session it is more configuration to get right.
5. **Little to save.** About fifteen short queries across nine ports. The mapping configuration for a composite key (`BucketAggregate`), a self-referencing relation (`PriceEntry.corroborating_entry_id`) and snapshot columns would be comparable in size to the SQL it replaces.

**Cost accepted:** hand-written SQL, hand-written row mapping, and the risk of code and schema drifting apart. Controls: every query is parameterised, and the repository contract tests run against a real PostgreSQL so a column mismatch fails a test, not production.

**Reconsider if:** the number of distinct queries passes about thirty, the schema is changing more than weekly, or the team finds it spends more time on mapping code than on features.

### Other rejections

| ID | Rejected | Reason | Reconsider if |
|---|---|---|---|
| **R2** | **Dependency-injection container** | Around a dozen collaborators are wired in one composition root, and explicit constructor calls show every dependency at a glance. A container adds reflection and configuration through which a dependency can appear that no one wrote down — the kind of hidden dependency this laboratory warns about | Wiring grows past roughly thirty collaborators or needs per-request scoping |
| **R3** | **SQLite, even for development** | It has no roles or privileges, so DC-18, DC-19 and DC-22 could not be tested against it, and developers would meet different behaviour from the real database | The privilege rules are dropped from the design |
| **R4** | **A message broker or a second service** | Already rejected in `ADR-001-architecture.md` (Alternative B); nothing in this decision changes that evidence | ADR-001's reconsideration triggers fire |
| **R5** | **An asynchronous web framework** | The loads in QS-01 and QS-06 are small, and asynchronous code makes the in-process worker and the transaction rules harder to reason about | Measured request concurrency exceeds what threads handle |

## 7. If the team's language is not Python (A1 fails)

The decisions in §3 follow from the criteria, not from Python in particular. Equivalent choices:

| Need | Java | TypeScript | C# |
|---|---|---|---|
| Exact decimals | `BigDecimal` | A decimal library (not `number`) | `decimal` |
| Ports | Interfaces | Interfaces / types | Interfaces |
| Dependency-rule check | ArchUnit | dependency-cruiser | NetArchTest |
| Thin web layer | A minimal HTTP library, **not** a full-stack framework | Express or similar | Minimal APIs |
| Database access | JDBC with SQL | A SQL driver, not an ORM | ADO.NET / Dapper-style, not an ORM |

R1 to R5 and the dependency rules in §5 carry over unchanged.

## 8. Evidence that would reopen this decision

1. **A1 fails:** the team cannot work comfortably in Python within the first week of implementation.
2. **QS-01 is missed** on measurement and profiling points at the framework rather than the design.
3. **The single worker process** proves unable to host the recompute worker and request threads together (ADR-001 trigger 1).
4. **PostgreSQL is unavailable** in the team's lab or hosting environment.

## 9. Open items

| Item | Needed |
|---|---|
| **A1** | The team confirms its language, or names the alternative. `ADR-002` is written only after that |
| Migration tool | Plain numbered SQL files run by a small script, or an existing SQL-migration tool. Either way the grants for DC-18, DC-19 and DC-22 are written in SQL in the migrations and tested |
| Hosting | No hosting target is chosen beyond Docker Compose; `deployment.md` describes the layout only |
