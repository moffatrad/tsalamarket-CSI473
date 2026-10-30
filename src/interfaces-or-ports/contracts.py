from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class VerifiedPriceQuery:
    """Criteria for retrieving verified market prices."""

    commodity_id: str
    district_id: str
    window_start: date
    window_end: date
    minimum_entries: int = 5
    minimum_submitters: int = 2


@dataclass(frozen=True, slots=True)
class VerifiedPriceObservation:
    """A verified market-price observation."""

    observation_id: str
    commodity_id: str
    district_id: str
    price_per_kg: Decimal
    submitted_at: datetime
    submitter_id: str


@dataclass(frozen=True, slots=True)
class PriceSubmission:
    """A price submitted by a market vendor."""

    commodity_id: str
    district_id: str
    amount: Decimal
    quantity: Decimal
    unit_code: str
    submitted_at: datetime
    submitter_id: str


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """An event recorded for auditing purposes."""

    actor_id: str
    action: str
    target_type: str
    target_id: str
    occurred_at: datetime
    details: str