# User Profile and Tasks — Tsala Market

**Team 16 · Tsala Market · CSI473 Laboratory 10**
**Traces to:** Proposal §1, §4, §5 · UC-01, UC-03 · FR-01–FR-05, FR-14 · QS-01, QS-03, QS-04 · `core-operation.md` · `data-integrity.md` (DI-1, DI-2)

## 1. Evidence base, and what it cannot tell us

This profile is built from the approved proposal (§4 stakeholder evidence, §5 assumptions), the API contract and the quality scenarios. **No farmer or vendor has been interviewed or observed.** Anything below that those sources do not state is tagged **[A#]** and listed in §5 as an assumption to validate.

The usability check in this laboratory uses three people who are not on the team. They are not farmers. The check can expose interface problems such as unclear wording, dead ends and recovery failures. It cannot show that the design fits farmers' real conditions, and results should be described that way.

## 2. Primary user: the smallholder horticulture farmer

| Attribute | Profile | Basis |
|---|---|---|
| Who | Grows vegetables or fruit on a small holding and sells to traders at the farm gate or at market | Proposal §1 |
| Device | A basic mobile phone. No smartphone, and often no mobile data | Proposal §4 ("USSD is the primary access point given low smartphone penetration"), §5 assumption |
| Channel | Dials a USSD code and answers numbered menus; SMS is possible. The web dashboard is a secondary channel | FR-14 |
| Moment of use | A buyer has just made an offer, or is waiting for an answer, and the farmer wants to know whether it is fair before replying | UC-01 trigger |
| Goal | Decide whether to accept, negotiate, or look for another buyer | UC-01 step 12 |
| Not a goal | Reading statistics, submitting prices, browsing trends | Scope: UC-01 is the farmer's core task |
| Time available | A couple of minutes at most, with a buyer present; a long process will be abandoned | [A1] |
| Reading and numbers | Comfortable with prices and short words. Terms such as "deviation", "median" or "confidence interval" are likely to be skipped or misread | [A2] |
| Language | Not decided in any requirement: English, Setswana or both | [A3] |
| Cost | A USSD session may cost money, depending on the carrier, so extra screens may cost the farmer | [A4] |
| Phone sharing | The phone may be shared with family, so nothing personal should appear on screen or be remembered | [A5], consistent with BR-11 |
| Frustration | Being told "that is the going rate" with no way to check it | Proposal §1 |

### What this profile asks of the interface

| Trait | Interface rule |
|---|---|
| Feature phone, USSD | Everything possible as numbered choices. The only typed value is the price |
| Little time, buyer waiting | Few screens (QS-03). Do not ask for the grade; default to Grade B and say so (FR-05) |
| Limited reading | Lead the result with the flag in plain words, then the farmer's price and the reference price, each in P/kg, then the short disclaimer. No statistical terms |
| Language undecided | All screen text kept in one place so it can be translated without changing logic |
| Cost of each screen | After an error, keep what the farmer already entered and say exactly what to fix |
| Shared phone, no identity (BR-11) | Nothing is remembered between sessions. **Cost accepted:** the farmer re-enters the crop and district every time |
| Must trust a number from an unfamiliar system | Show how much data stands behind the answer, in words (the confidence label), and that it is a guide, not a promise (FR-13) |

## 3. Tasks

### T1 — Check an offer *(primary user, primary channel USSD)*

**Scenario.** A trader arrives at the farm and offers P152 for a crate of tomatoes, about 20 kg. The farmer is unsure whether that is a good price and does not want to say yes or no without checking. The farmer dials the service, says which crop and district, says the offer was per crate, and enters 152. The service answers. The farmer then tells the trader yes, no, or "I will think about it".

**Success criteria.**

| Criterion | Target | Source | In this lab's check |
|---|---|---|---|
| Completes the check **without help** | 3 of 3 participants | QS-03 asks for ≥80% of ≥5 first-time users, later | Counted per participant |
| Number of screens | ≤5 | QS-03 | Counted. **See open question OQ-1: the shortest path currently has six** |
| **Understands the result** | Each participant says in their own words whether the offer is fair, low or high | New criterion; the point of the feature | Asked after the result screen |
| **Understands it is a guide** | Each participant says the result is not a guaranteed price | FR-13, BR-10 | Asked after the result screen |
| Recovers from a wrong unit | Fixes an unsupported unit on the next attempt, unaided | FR-03, UC-01 A2 | Scenario card gives a unit not on the list |
| Result returned quickly | ≤5 s for 95% of requests | QS-01 | Not user-measured on paper; checked in implementation |

**Situations the interface must handle:** unsupported unit, not enough verified data (no flag is shown), database unavailable, session timeout, a zero or non-numeric price. These are designed in `docs/ui-states.md`.

**Secondary channel.** The same task on the web dashboard, for a farmer or helper with a smartphone. It must give the same result and the same error meanings (contract §5).

### T2 — Submit a price entry *(secondary user: market vendor or cooperative lead, web)*

**Who.** The proposal describes this role by need and concern only: it needs to submit or view price data for a ward or district, and it worries about the time cost of manual entry and an unclear incentive to take part (Proposal §4). Its device and skills are not stated **[A6]**.

**Scenario.** After the morning's trading at a municipal market, a cooperative lead wants to record today's farm-gate price for tomatoes in Kweneng: P152 per crate, standard quality. The lead opens the submission page, enters the details, and wants to be sure the system recorded what was meant.

**Success criteria.**

| Criterion | Target | Source |
|---|---|---|
| Completes the entry unaided | 3 of 3 | Lab check |
| Time taken | About 60 seconds or less | **[A7]** a target to test, not a stated requirement |
| Sees what was stored | Confirmation shows the price as **P/kg (7.60)**, not only the figure typed | FR-02 |
| Understands the unit rule | If a unit is not accepted, the page lists the units that are | FR-03 |
| Understands the grade default | If grade is left blank, the page says it was recorded as Grade B | FR-05 |
| Fixes an error without retyping other fields | All other fields are kept | Design rule from §2 |
| Understands the entry's status | Can say whether the entry counts yet | BR-02. **Wording depends on DI-1** (OQ-4) |

**Situations the interface must handle:** unsupported unit, non-positive price, unknown district, not logged in, account not yet approved (if DI-1 is accepted), data unavailable.

### T3 — Review and exclude a suspicious entry *(administrator; described, not wireframed this lab)*

**Scenario.** An Admin sees an entry flagged as an outlier, checks it against the others in its bucket, excludes it with a reason, and sees that the action was recorded.

**Why not wireframed now.** This task depends on the exclusion feature (DI-2) and on how accounts are approved (DI-1), neither of which the team has decided. Wireframing it now would design a feature that may not exist. It is the natural third perspective once those decisions are made, and its unauthorised state (a non-Admin reaching the page) is straightforward.

### Which tasks get wireframes

T1 and T2, which gives two roles (farmer and vendor) and the two main channels (USSD and web). Trend lookup (UC-02), the Extension Officer dashboard (UC-06) and configuration (UC-07, UC-08) are outside this laboratory.

## 4. How the three-person check will use these tasks

- Each participant gets one **scenario card** per task, in the words of the scenarios above, with no screen names or instructions on how to do it.
- Participants are not told what the result screen means; that is what the comprehension criteria test.
- One participant is given a card containing a unit that is not on the list, to test recovery.
- The observer records for each task: completed unaided (yes/no), screens or steps used, errors made, points of hesitation, and what the participant said the result meant.
- At least one design change must follow from something observed (the lab's evaluation standard). Results are recorded in `evidence/usability-test.md`.

## 5. Assumptions and open questions

| ID | Item | How to settle it |
|---|---|---|
| **A1** | Farmers have only a couple of minutes for the task | Ask the Extension Officer role or a farmer contact; observe in the lab check |
| **A2** | Farmers read short words and numbers comfortably but may skip technical terms | Comprehension questions in the check; ask a farmer contact |
| **A3** | Language is undecided | See OQ-2 |
| **A4** | USSD sessions may cost the farmer | Check the carrier terms when a real gateway is considered |
| **A5** | The phone may be shared | Ask a farmer contact; the design is safe either way |
| **A6** | Vendors have web access, on a smartphone or a shared computer | See OQ-3 |
| **A7** | About 60 seconds is an acceptable time for a vendor to submit one entry | Time it in the check; ask a vendor contact whether it would be tolerated daily |
| **OQ-1** | **Screen budget.** The shortest USSD path is: menu (1), crop (2), district (3), unit (4), price (5), result (6), which is six screens, but QS-03 says five or fewer. Options: a dedicated short code that skips the menu; a default unit for each crop; or counting only screens that need an answer. | Decide in the navigation model and, if the budget is redefined, update QS-03 |
| **OQ-2** | **Which language or languages** the screens use, and who translates and reviews them | Team decision, ideally with a farmer or Extension Officer contact |
| **OQ-3** | **Vendor channel:** web only, or USSD as well | Team decision; this document assumes web for T2 |
| **OQ-4** | **Wording of the submission outcome** (counts now, or awaits corroboration) | Follows the DI-1 decision |

## 6. Traceability

| Task | Use case | Requirements | Quality scenarios and contract | Next artefacts |
|---|---|---|---|---|
| T1 Check an offer | UC-01 | FR-01, FR-02, FR-03, FR-05, FR-11–FR-14 | QS-01, QS-03, QS-04; `core-operation.md` (codes and `disclaimer_short`) | `models/navigation.*`, `prototype/wireframes.*`, `docs/ui-states.md` |
| T2 Submit a price entry | UC-03 | FR-04, FR-05, FR-02, FR-03, FR-06 | QS-03 (usability); no submission contract yet | Same; a submission contract is needed before implementation |
| T3 Exclude an entry | UC-05 | FR-16 | QS-07 | After DI-1 and DI-2 are decided |
