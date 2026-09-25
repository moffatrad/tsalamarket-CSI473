# Glossary — Tsala Market

Terms used across the proposal, system context diagram, and decision
records for Team 16's Tsala Market project.

## Domain terms

**BAMB (Botswana Agricultural Marketing Board)**
The government body that sets official monthly producer prices for grains
and pulses, benchmarked against SAFEX, and operates through 11 physical
branches. Access is structurally limited to large commercial farms in the
north; smallholders in other districts are largely excluded. Modelled as an
external system in the system context diagram.

**Fair Price Check**
The system's core differentiator feature. A farmer submits the price a
buyer has just offered them for a commodity/district combination; the
system compares it against the verified market average and returns a
fairness flag. See *fairness flag*.

**Fairness flag**
The three-state result returned by the Fair Price Check: Fair, Below
Average, or Significantly Underpaid. Calculated from the percentage
deviation between the farmer's offered price and the verified market
average.

**Farm-gate price**
The price a farmer actually receives for produce at the point of sale,
before any markup by middlemen or transport to market. Central to the
problem statement: farm-gate prices are often disconnected from real urban
market demand, especially for horticulture.

**Middleman**
An informal buyer who purchases produce directly from farmers, typically
at prices below the going market rate, exploiting the farmer's lack of
reference information. The primary channel for horticulture, which has no
formal pricing board.

**Smallholder farmer**
A farmer operating at small scale (as opposed to large commercial
operations), typically excluded from BAMB's effective reach and lacking
bulk volume to meet purchase thresholds. The primary user and stakeholder
the system is designed to serve.

**Verified price / Community-reported price**
The two-tier tagging system for price data entering Tsala Market.
Verified prices come from confirmed sources (BAMB, registered buyers,
market vendors) and are eligible for the Fair Price Check average.
Community-reported prices are crowd-sourced and displayed but excluded
from fairness calculations unless/until verified.

## System and roles

**Cooperative Aggregation**
A Tier 2 feature allowing smallholders in the same ward/district to pool
small quantities into a single "virtual lot" to meet buyer minimum-volume
thresholds (such as BAMB's roughly 200-bag requirement).

**Extension Officer**
A Ministry of Agriculture stakeholder who uses an aggregate, anonymised
dashboard to monitor regional price trends and underpayment incidents.
Modelled as an actor outside the system boundary.

**Market Vendor / Cooperative Lead**
A stakeholder who coordinates group sales for a ward/district and submits
or views price data on behalf of that group.

**System Admin**
The role responsible for managing user accounts, verifying data sources,
and maintaining overall data integrity. Modelled as a person operating the
system through an interface, not as internal system logic (see D-001).

**System context diagram**
A diagram showing one proposed system boundary, with all people and
external systems kept outside it, and every connector between them
labelled. Used to fix the scope of Tsala Market before designing internal
architecture.

**Tsala Market**
The working name for the project (Setswana for "friend/companion"). A
crop and livestock price transparency platform for Botswana's smallholder
farmers, delivered as a multi-channel system (web dashboard, USSD, SMS).

**USSD (Unstructured Supplementary Service Data)**
A protocol used by feature phones to access menu-driven services without
a data connection. The primary access channel for farmers without
smartphones or reliable mobile data; modelled as an external system
(telecom gateway) in the system context diagram, mocked for the semester
build.

**Verified Buyer**
A stakeholder role representing a BAMB representative or other registered
trader who posts demand and pricing to relevant districts and reaches
organised supply through the platform.

## Project process terms

**ADR (Architecture/design decision record)**
A short, numbered document (e.g. `D-001.md`) capturing a single design
decision: its context, the decision made, its consequences, and
alternatives considered. Used to keep an auditable log of design choices
over the semester.

**Vertical slice**
A thin end-to-end implementation of one primary workflow (in this case,
the Fair Price Check) touching all relevant layers of the system, used as
the feasible semester-sized deliverable in place of the full multi-tier
feature set from the original concept.
