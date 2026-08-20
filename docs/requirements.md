# Functional Requirements — Tsala Market

Traceability: Each requirement below traces back to the Goal/Objectives (Proposal), Stakeholders, and Price Normalisation, Verification, Aggregation and Classification Methodology.

Requirements use stable identifiers (`FR-XX`) so later use cases, acceptance criteria and quality scenarios can reference them directly. Each statement describes verifiable system behaviour — not a UI instructio.


## Price submission and normalisation

FR-01
The system shall allow a Smallholder Horticulture Farmer to submit a Fair Price Check request specifying commodity, district, quality grade, and the price they were offered by a buyer.

FR-02
The system shall convert every submitted price into Pula per kilogram (P/kg) using a commodity-specific conversion-factor table before the price is stored, aggregated, or displayed.

FR-03
The system shall reject, at the point of entry, any price submission expressed in a unit that is not present in the conversion-factor table, and shall return the reason for rejection to the submitter rather than discarding or guessing the value.

FR-04
The system shall allow a Verified Buyer, Market Vendor, or Cooperative Lead to submit a price entry tagged with commodity, district, quality grade (A/B/C), and market level (Farm-gate, Wholesale/municipal market, or Retail).

FR-05
The system shall default any price entry submitted without a declared quality grade to Grade B, and shall flag that entry as "ungraded" in the System Admin view for correction.

## Verification

FR-06
The system shall classify every new price entry as "Community-reported" by default, and shall promote an entry to "Verified" status only when at least one of the following is true: (a) it originates from a registered Verified Buyer, Market Vendor, or Cooperative Lead account; (b) it is corroborated by a second independent submission for the same commodity/district/grade/market-level combination within 72 hours and within 15% of the original price; or (c) a System Admin manually confirms it.

FR-07
The system shall exclude all "Community-reported" (unverified) entries from Fair Price Check calculations while continuing to display them for general trend context.

## Aggregation and Fair Price Check

FR-08
The system shall calculate a Fair Price Check reference value as the median of Verified price entries for the matching commodity, district, quality grade, and Farm-gate market level, pooled over the trailing 30 days.

FR-09
The system shall require a minimum of 5 independent Verified entries from at least 2 different submitters within a commodity/district/grade/market-level bucket before using that bucket to generate a Fair Price Check result; if this threshold is not met, the system shall apply the fallback rule (nearest district or a broader regional bucket) and mark the result "Low Data".

FR-10
The system shall exclude, before calculating the reference median, any entry more than 1.5× the interquartile range (IQR) outside the bucket's Q1–Q3 range, and shall log each excluded entry for System Admin review.

FR-11
The system shall assign a fairness flag to each Fair Price Check result based on the offered price's percentage deviation below the reference median: Fair (within ±10%), Below Average (10–25% below), or Significantly Underpaid (more than 25% below).

FR-12
The system shall assign a confidence label — High, Medium, or Low — to each Fair Price Check result, based on the number of Verified entries used, the number of distinct submitters, and the recency of the underlying data.

FR-13
The system shall display an explicit disclaimer alongside every Fair Price Check result stating that the result is indicative guidance based on recent aggregated verified submissions, not a guaranteed, audited, or binding price.

## Access, roles and reporting

FR-14
The system shall allow a Farmer to look up current prices and historical price trends by commodity and district through both a web dashboard and a USSD/SMS interface.

FR-15
The system shall allow an Extension Officer to view an aggregated, anonymised dashboard of Fair Price Check queries and underpayment flags by district, without exposing farmer-identifiable data.

## Administration

FR-16
The system shall allow a System Admin to manually verify, reject, or correct the grade or market-level tag of any price entry, and shall record each such action in an audit log with admin identity and timestamp.

FR-17
The system shall allow a System Admin to configure the classification thresholds, the 30-day aggregation window, the 72-hour corroboration window, and the 5-entry minimum sample size as adjustable parameters, without requiring a code change.

