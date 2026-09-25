# Acceptance Criteria — UC-01: Check Fair Price

Traces to: `UC-01-check-fair-price.md` (main success scenario + alternative flows A1–A4) · `requirements.md` FR-01, FR-02, FR-03, FR-05, FR-08–FR-13

Each criterion below is testable against the running system: a tester can set up the "Given" state, perform the "When" action, and check the "Then" outcome without ambiguity.


### AC-01 — Fair offer returns a "Fair" flag with the correct reference price
*Covers: main success scenario, steps 4–10; FR-08, FR-09, FR-11*

**Given** a Verified market average of P8.00/kg exists for Tomatoes, Grade B, Farm-gate, in Kweneng district, built from at least 5 Verified entries from at least 2 submitters within the last 30 days
**When** a farmer submits a Fair Price Check for Tomatoes, Grade B, Kweneng, with an offered price equivalent to P7.60/kg
**Then** the system returns a "Fair" flag (offer is within ±10% of the reference median), displays the P8.00/kg reference price used, and shows the "indicative guidance, not a guarantee" disclaimer

### AC-02 — Underpaid offer returns "Significantly Underpaid" with the right threshold boundary
*Covers: main success scenario, step 8; FR-11*

**Given** the same Verified reference average of P8.00/kg for Tomatoes, Grade B, Kweneng
**When** a farmer submits an offered price equivalent to P5.60/kg (30% below the reference median)
**Then** the system returns a "Significantly Underpaid" flag, since the deviation exceeds the 25%-below threshold, and displays both the reference price and the calculated percentage deviation to the farmer

### AC-03 — Insufficient verified data triggers the fallback, not a fabricated result
*Covers: Alternative Flow A3; FR-09*

**Given** the Farm-gate bucket for Butternut, Grade A, in Ngamiland district contains only 3 Verified entries from a single submitter (below the 5-entry/2-submitter minimum)
**When** a farmer submits a Fair Price Check for Butternut, Grade A, Ngamiland
**Then** the system does not calculate a fairness flag from that bucket; it instead widens the lookup to the nearest neighbouring district or a broader regional bucket, and if a qualifying bucket is found, returns a result explicitly labelled "Low" confidence and states it is based on a wider area than the farmer's own district — or, if no bucket anywhere qualifies, tells the farmer that insufficient verified data is available and returns no fairness flag at all

### AC-04 — Unrecognised unit is rejected at entry, not silently converted
*Covers: Alternative Flow A2; FR-03*

**Given** a farmer is entering the price they were offered for Cabbage
**When** the farmer enters a price using a unit that is not present in the commodity's conversion-factor table (e.g., an unsupported local measure)
**Then** the system rejects the submission before any calculation occurs, tells the farmer which units are supported for Cabbage, and returns them to the price-entry step without recording a converted or guessed value

### AC-05 — Ungraded lookup defaults to Grade B and says so
*Covers: Alternative Flow A1; FR-05*

**Given** a farmer does not know or does not select a quality grade for their produce during a Fair Price Check
**When** the farmer proceeds without selecting a grade
**Then** the system performs the lookup against the Grade B bucket for that commodity and district, and the result screen states that the comparison assumed standard/Grade B quality

### AC-06 — Confidence label reflects sample size, submitter diversity and recency
*Covers: main success scenario, step 9; FR-12*

**Given** a Farm-gate bucket for Onions, Grade B, in Central district contains 12 Verified entries from 4 different submitters, all logged within the last 5 days
**When** a farmer runs a Fair Price Check for Onions, Grade B, Central
**Then** the system labels the result "High" confidence (≥10 Verified entries, ≥3 submitters, all within 7 days) alongside the fairness flag

### AC-07 — Every result carries the indicative-guidance disclaimer, without exception
*Covers: main success scenario, step 10; FR-13; Special Requirement in UC-01*

**Given** any Fair Price Check that successfully returns a fairness flag, regardless of which flag or confidence level is assigned
**When** the result is displayed to the farmer on USSD/SMS or the web dashboard
**Then** the disclaimer stating the result is "indicative guidance based on recent aggregated verified submissions, not a guaranteed, audited, or binding price" is shown alongside it, and cannot be dismissed or hidden by the farmer before viewing the result
