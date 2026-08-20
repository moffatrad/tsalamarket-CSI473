# Tsala Market — Project Problem Proposal (Sections 1–8)

## 1. Problem Statement

Smallholder farmers across Botswana's grain, horticulture, and livestock sectors consistently sell their produce without knowing what it is actually worth. For grains and pulses, the Botswana Agricultural Marketing Board (BAMB) publishes monthly producer prices, but access is structurally limited to large commercial farms in the north — smallholders in the south, east, and central districts often cannot reach one of BAMB's eleven branches, cannot meet bulk purchase thresholds such as the roughly 200-bag minimum, and frequently do not even know the current price before they sell. Horticulture producers face an even starker gap: no pricing board exists at all, so farm-gate prices are set entirely by middlemen, disconnected from actual demand in urban markets like Gaborone and Francistown. Livestock sellers face similar uncertainty, with cattle and goat prices varying unpredictably by auction, buyer, and season, despite livestock representing a primary store of household wealth for many rural families. The consequence across all three sectors is the same: farmers routinely accept below-market offers because they have no reliable reference point to negotiate from, eroding already-thin household incomes and reinforcing dependency on the buyers who benefit from that information gap. Without a way to close this asymmetry, smallholders remain structurally disadvantaged relative to buyers who always know the going rate, and the exclusion these farmers experience under existing systems like BAMB will persist.

## 2. Evidence of the Problem

| Evidence/source | Date/origin | What it shows |
|---|---|---|
| BAMB's monthly producer pricing structure and 11-branch network | BAMB operations, ongoing (current) | Confirms BAMB sets official prices for grains/pulses but distributes access through only 11 physical branches, structurally limiting reach for smallholders outside those catchment areas |
| BAMB's bulk purchase/minimum-volume requirement (~200-bag threshold) | BAMB contract/purchase terms | Demonstrates a concrete, quantifiable barrier: most individual smallholders cannot produce enough volume to qualify for direct BAMB sales, pushing them toward informal buyers |
| Absence of any pricing board for horticulture or livestock | Market structure observation (current) | Confirms there is no formal price-transparency mechanism at all outside grains — horticulture and livestock producers rely entirely on middleman/auction pricing with no reference point |
| Botswana's rural geography and connectivity constraints (~70% desert landscape, uneven mobile data access) | Ongoing national infrastructure context | Supports the rationale for a USSD/SMS channel, since a meaningful share of smallholders in remote districts lack reliable smartphone or data access to use a web/app-only system |

*Note: pick the two strongest rows for the form (it only provides two blank rows), and consider swapping one for a citable external source if your course requires traceable evidence.*

## 3. Goal and Objectives

| Item | Team response |
|---|---|
| Goal | To reduce information asymmetry between smallholder farmers and buyers across Botswana's grain, horticulture, and livestock markets by giving farmers accessible, verified price information and a way to check whether an offer they've received is fair before they sell. |
| Objective 1 | Design and implement a multi-channel price-lookup system (web dashboard and USSD/SMS) covering grains, horticulture, and livestock, sourced from major Botswana trading points, so farmers without smartphones or data can still check current prices. |
| Objective 2 | Develop a "Fair Price Check" feature where a farmer submits a price they've been offered, and the system compares it against the verified market average for that commodity and district, returning a clear fairness flag (fair / below average / significantly underpaid). |
| Objective 3 | Implement a "Verified" vs "Community-reported" price-tagging and submission workflow — drawing on market vendors, cooperatives, and BAMB data — to build a crowd-sourced pricing dataset that is trustworthy enough to underpin the Fair Price Check calculation. |

## 4. Stakeholders

| Stakeholder/role | Need | Concern | Evidence/access |
|---|---|---|---|
| Smallholder Farmer | Access accurate, timely prices before selling, and a way to check if an offer is fair | Reliability of the data source, and whether the system is usable without a smartphone or reliable data | Direct observation of rural farmer selling behaviour; USSD is the primary access point given low smartphone penetration |
| Market Vendor / Cooperative Lead | Coordinate group sales and submit or view price data on behalf of a ward/district | Time burden of manual data entry, and unclear incentive to participate consistently | Existing cooperative structures already used informally to meet BAMB's bulk purchase thresholds |
| Verified Buyer (BAMB rep / registered trader) | Reach organised supply and post demand/pricing to relevant districts | Integrity of crowd-sourced price data feeding into the averages they're compared against | BAMB's publicly published monthly producer prices and 11-branch network data |
| Extension Officer / Ministry of Agriculture | Regional oversight of price trends and underpayment incidents to inform policy | Data privacy/anonymisation of farmer-level data, and staying within their advisory mandate | Existing district agricultural office reporting channels |
| System Admin | Manage user accounts, verify data sources, and maintain overall data integrity | Risk of fraudulent or manipulated price submissions undermining trust in the system | Admin logs and the verification workflow built into price submission |

## 5. Scope, Assumptions and Constraints

### In scope / Out of scope

| In scope | Out of scope |
|---|---|
| Price lookup and historical trend viewing (web + USSD/SMS) for grains, horticulture, and livestock | Full ML-based price forecasting (only a simple trend/seasonal-average model, if attempted at all) |
| The "Fair Price Check" offer validator comparing a farmer's offer against the verified market average | Real payment processing or financial transactions between buyers and farmers |
| Verified vs. community-reported price tagging and submission workflow | Buyer trust/reputation rating system |
| Core user roles: Farmer, Vendor/Cooperative Lead, Verified Buyer, Extension Officer/Admin | Live integration with BAMB systems or real telecom USSD gateways (data will be synthetic/mocked) |

### Assumptions / Constraints

| Assumptions | Constraints |
|---|---|
| Synthetic/anonymised price and user data will stand in for real farmer and BAMB data during development and testing | The semester timeline requires a feasible vertical slice rather than the full multi-tier feature set from the original concept |
| Users have access to at least basic mobile phones (USSD/SMS), even without smartphones or mobile data | No live integration with BAMB or telecom USSD gateways is possible — these will be simulated/mocked |
| Cooperative and BAMB branch structures modelled in the system reflect realistic but generalised Botswana market conditions, not live operational data | Limited team resources for full translation/localisation and accessibility testing within the timeframe |

## 6. Proposed Core Workflow / Vertical Slice

**Primary actor:** Smallholder Farmer, completing a Fair Price Check on an offer they've just received.

1. The farmer dials the USSD short-code (or opens the app) and selects "Check My Offer."
2. The farmer selects their crop or livestock type and district, then enters the price a buyer has just offered them.
3. The system retrieves the current verified market average for that commodity and district from the price database.
4. **Important rule enforced:** only prices tagged "Verified" and submitted within the last 30 days are included in the average calculation — stale or unverified community-reported entries are excluded, so a single bad-faith submission can't skew the reference price.
5. The system calculates the percentage deviation between the farmer's offered price and the verified average.
6. **State/result created:** the system returns a fairness flag — Fair, Below Average, or Significantly Underpaid — along with the reference average it used, and logs the (anonymised) query for the Extension Officer's aggregate dashboard.
7. The farmer decides whether to accept the offer, negotiate, or seek the nearest alternative buyer, based on the flag received.
8. **Failure/exception to test:** if no verified price exists for that commodity/district combination (e.g., an under-reported area or an uncommon crop), the system does not fail silently or guess — it tells the farmer insufficient data is available and offers the nearest district or a broader regional average as a fallback instead.

## 7. Design-Suitability Check

| Check | Yes/No | Short evidence |
|---|---|---|
| Clear stakeholders and a genuine current problem | Yes | Farmers, vendors/cooperatives, verified buyers, and Ministry extension officers are all identified; the problem is grounded in BAMB's documented structure and the total absence of pricing transparency for horticulture and livestock |
| At least one state-sensitive workflow or entity | Yes | Price entries move through unverified → verified states; a farmer's offer query moves through submitted → evaluated states in the Fair Price Check |
| Important business/validation/security rule | Yes | Only "Verified" price entries submitted within the last 30 days feed the fairness-check average — stale or unverified data is excluded from the calculation |
| Relevant quality trade-offs | Yes | Trade-off between data freshness/coverage (allowing more crowd-sourced input) and data reliability (requiring a verification step before data is trusted) |
| Relevant failure/exception condition | Yes | No verified price exists for a given commodity/district combination, requiring a fallback response rather than a silent or misleading result |
| Feasible semester-sized vertical slice | Yes | Scope is limited to price lookup plus the Fair Price Check for a defined subset of commodities/districts, excluding forecasting, payments, and reputation features |
| Synthetic/anonymised data is sufficient | Yes | Historical BAMB prices and market averages will be synthesised/mocked rather than sourced from live BAMB or telecom systems |
| Not the University Service Hub or a renamed copy | Yes | The problem is an original agricultural market-transparency system for Botswana smallholders, unrelated in domain and structure to the University Service Hub case |

## 8. Data, Ethics, Safety and Dependency Risks

| Risk/concern | How the team will control it |
|---|---|
| Farmer/user data privacy (location, phone number, price submissions) | Store location data at district level only rather than precise coordinates; collect no personally identifiable information beyond what login requires |
| Reliance on synthetic/mocked BAMB and market price data rather than live feeds | Clearly document all price data as synthetic/for demonstration purposes; design the data model so real data sources can be substituted later without changing the architecture |
| Risk of inaccurate or malicious crowd-sourced price submissions | Enforce the "Verified" vs "Community-reported" tagging system, and restrict the Fair Price Check calculation to verified, recent entries only |
| Dependency on an external USSD gateway/telecom provider for real-world deployment | Simulate USSD interactions locally for the semester build, and document the live gateway as an external dependency and risk for any future real deployment |

---

*Sections still to complete: Team/admin fields (team number, members, repository URL, etc.) and Section 9 (Lecturer decision), which is not filled in by the team.*
