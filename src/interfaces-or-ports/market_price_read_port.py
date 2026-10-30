from typing import Protocol, Sequence

from .contracts import (
    VerifiedPriceObservation,
    VerifiedPriceQuery,
)


class MarketPriceReadPort(Protocol):
    """
    Interface for retrieving verified market-price observations.

    Used by the Check My Offer (UC-01) workflow.
    """

    def find_verified_prices(
        self,
        query: VerifiedPriceQuery
    ) -> Sequence[VerifiedPriceObservation]:
        """
        Retrieve verified prices matching the query.

        Pending and rejected submissions must not be returned.
        """
        ...