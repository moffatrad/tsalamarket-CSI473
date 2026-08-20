# Use Case Summaries — Tsala Market

UC-01 is the only fully dressed use case required for Laboratory 3 (see `UC-01-check-fair-price.md`). The remaining use cases shown in `models/use-case-model.*` are summarised briefly below for traceability; each can be dressed fully in a later laboratory if the team selects it.

| ID | Use case | Primary actor(s) | Goal (one line) | Traces to |
|---|---|---|---|---|
| UC-01 | Check Fair Price | Smallholder Horticulture Farmer | Decide whether a buyer's offer is fair before selling | FR-01, FR-02, FR-06–13 |
| UC-02 | Look Up Price Trends | Smallholder Horticulture Farmer | See current and historical prices for a commodity/district before approaching a buyer | FR-14 |
| UC-03 | Submit Price Entry | Market Vendor/Cooperative Lead, Verified Buyer | Contribute a price observation to the shared dataset | FR-04, FR-05 |
| UC-04 | Corroborate Price Entry | Market Vendor/Cooperative Lead, Verified Buyer | Independently confirm another submitter's price so it can be promoted to Verified | FR-06 |
| UC-05 | Verify Price Entry Manually | System Admin | Resolve entries that cannot be auto-verified, or review flagged outliers | FR-06, FR-10, FR-16 |
| UC-06 | View Aggregate District Dashboard | Extension Officer | Monitor regional price trends and underpayment patterns to inform policy | FR-15 |
| UC-07 | Configure System Parameters | System Admin | Recalibrate thresholds (fairness bands, windows, minimum sample size) as real data accumulates | FR-17 |
| UC-08 | Manage User Accounts | System Admin | Register, verify, or deactivate Vendor/Buyer/Cooperative accounts that feed the dataset | — (supporting/administrative) |
| UC-09 | Retrieve Verified Market Average | System (included by UC-01) | Compute the aggregated, outlier-filtered reference price for a bucket | FR-08, FR-09, FR-10 |

**Relationships shown in the model:**
- UC-01 «include» UC-09 — every Fair Price Check always needs a reference average computed.
- UC-05 «extend» UC-03 and UC-04 «extend» UC-03 — manual verification and peer corroboration are alternative paths that a submitted entry may (but need not always) go through on its way to "Verified" status.
