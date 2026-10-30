from typing import Protocol

from .contracts import PriceSubmission


class PriceSubmissionWritePort(Protocol):
    """
    Interface for saving market-price submissions.
    """

    def save_submission(
        self,
        submission: PriceSubmission
    ) -> str:
        """
        Save a vendor price submission.

        Returns:
            The unique identifier assigned to the submission.

        Note:
            Saving a submission does not mean it has been verified.
        """
        ...