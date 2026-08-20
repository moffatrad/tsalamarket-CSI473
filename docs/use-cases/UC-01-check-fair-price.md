# UC-01 — Check Fair Price

**Team 16 · Tsala Market · CSI473 Laboratory 3**
**Traces to:** FR-01, FR-02, FR-06–FR-13 (requirements.md) · Goal and Objective 2 (Proposal §3) · Stakeholder "Smallholder Horticulture Farmer" (Proposal §4) · Workflow §6 / Methodology §6a of the Project Problem Proposal

---

## Actor goal
A **Smallholder Horticulture Farmer** wants to know, before accepting or rejecting an offer, whether the price a buyer has just offered them for their produce is fair — so they can decide whether to accept, negotiate, or look for another buyer. This is a genuine actor goal (a decision the farmer needs to make), not a single click, field entry, or database action.

## Primary actor
Smallholder Horticulture Farmer

## Secondary actors
- **System** (Tsala Market pricing engine — computes the aggregated reference price)
- **Extension Officer** (receives an anonymised log of the query for the district dashboard, but does not participate synchronously)

## Stakeholders and interests
| Stakeholder | Interest |
|---|---|
| Smallholder Horticulture Farmer | Wants an accurate, fast, low-cost way to check an offer without needing a smartphone or data bundle |
| Market Vendor / Cooperative Lead, Verified Buyer | Want the reference price used in the comparison to be trustworthy, since it is built from their submissions |
| System Admin | Wants the calculation to be defensible and auditable (verified-only data, documented thresholds) |
| Extension Officer | Wants an anonymised record of underpayment patterns by district for policy purposes |

## Preconditions
1. The farmer has access to a basic mobile phone capable of USSD/SMS, or the web dashboard.
2. At least one commodity/district/grade bucket exists in the system (may or may not have enough Verified entries to clear the minimum-sample threshold — see Alternative Flow A3).
3. The farmer has just received (or is about to accept) a price offer from a buyer and knows the commodity, their district, and the offered price.

## Postconditions (success guarantee)
- A fairness flag (Fair / Below Average / Significantly Underpaid) and a confidence label (High / Medium / Low) have been returned to the farmer, along with the reference price and the disclaimer that the result is indicative guidance, not a guarantee.
- The query has been logged (commodity, district, deviation, flag — no personally identifiable data) for the Extension Officer's aggregate dashboard.

## Minimal guarantee (failure guarantee)
- No fairness flag is presented without a reference value to support it: if insufficient verified data exists, the system explicitly reports "Low Data" / insufficient data rather than fabricating or silently omitting a result (see Alternative Flow A3).

## Trigger
The farmer selects "Check My Offer" (USSD menu option or web/app action) after receiving a buyer's offer.

---

## Main success scenario

| Step | Actor/System | Action |
|---|---|---|
| 1 | Farmer | Dials the USSD short-code (or opens the app/dashboard) and selects "Check My Offer." |
| 2 | Farmer | Selects their commodity/crop type and district from a presented list. |
| 3 | Farmer | Enters the price the buyer has just offered them, and the unit it was quoted in (e.g., per crate, per bag). |
| 4 | System | Converts the offered price to P/kg using the commodity-specific conversion-factor table (FR-02). |
| 5 | System | Retrieves the pooled Verified entries for the matching commodity × district × grade × Farm-gate bucket from the trailing 30 days (FR-08). |
| 6 | System | Excludes any entry beyond 1.5× IQR from the bucket's Q1–Q3 range (FR-10), then confirms the bucket meets the 5-entry / 2-submitter minimum (FR-09). |
| 7 | System | Calculates the reference price as the median of the remaining pooled entries (FR-08). |
| 8 | System | Calculates the percentage deviation of the farmer's offered price below the reference median and assigns a fairness flag: Fair (±10%), Below Average (10–25% below), or Significantly Underpaid (>25% below) (FR-11). |
| 9 | System | Assigns a confidence label — High, Medium, or Low — based on sample size, submitter diversity, and data recency (FR-12). |
| 10 | System | Returns the fairness flag, confidence label, reference price, and an explicit "indicative guidance, not a guarantee" disclaimer to the farmer (FR-13). |
| 11 | System | Logs the anonymised query (commodity, district, deviation, flag, timestamp — no farmer identity) for the Extension Officer's aggregate dashboard. |
| 12 | Farmer | Reviews the result and decides whether to accept the offer, negotiate, or seek an alternative buyer. |

## Alternative flows

**A1 — Ungraded submission at step 2/3:**
If the farmer does not know or does not select a specific quality grade for their produce, the system defaults the lookup to Grade B (the same default applied to ungraded entries at submission, FR-05) and proceeds from step 5, noting to the farmer that the result assumes standard/Grade B quality.

**A2 — Unrecognised unit at step 3:**
If the farmer enters a price in a unit not present in the conversion-factor table (e.g., an unlisted local measure), the system rejects the input at entry, tells the farmer which units are supported for that commodity, and returns to step 3 rather than guessing a conversion (consistent with FR-03).

**A3 — Insufficient verified data (failure/exception condition, tested explicitly):**
At step 6, if the matching commodity/district/grade bucket has fewer than 5 independent Verified entries from at least 2 submitters, the system does not guess or silently return a thin average. Instead it:
1. Applies the fallback rule: widens the lookup to the nearest neighbouring district, or to a broader regional bucket for the same commodity/grade.
2. If a fallback bucket clears the minimum threshold, proceeds from step 7 using that bucket, and marks the result confidence as "Low" and clearly labels it as based on a wider area than the farmer's own district.
3. If no fallback bucket clears the threshold either, the system informs the farmer that insufficient verified data is available for that commodity in their area, and does not issue a fairness flag at all — ending the use case without a postcondition-guaranteeing result, but still satisfying the minimal guarantee (no fabricated flag).

**A4 — Farmer abandons the check before step 10:**
If the farmer exits the USSD session or navigates away before a result is returned, no result is logged for the Extension Officer dashboard, and the use case ends without a completed Fair Price Check.

## Special requirements
- The USSD path must complete within a small number of menu screens, since the target users may be paying per session/SMS.
- The disclaimer text (step 10) must always accompany a result — it is not optional or hideable by the farmer.

## Frequency of use
Expected to be the most frequently invoked use case in the system — potentially several times per farmer per selling season, and the direct realisation of Objective 2 in the Project Problem Proposal.

## Open issues
- Exact wording and length limits for the USSD disclaimer text (SMS/USSD character limits may require an abbreviated form of the "indicative guidance" disclaimer).
- Whether the district-widening fallback in A3 should be capped at one level of widening or allowed to escalate further before returning "insufficient data."
