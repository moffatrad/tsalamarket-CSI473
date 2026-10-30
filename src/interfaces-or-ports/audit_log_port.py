from typing import Protocol

from .contracts import AuditEvent


class AuditLogPort(Protocol):
    """
    Interface for recording system audit events.

    Audit events are append-only.
    """

    def append(self, event: AuditEvent) -> None:
        """
        Add a new event to the audit log.

        Existing audit records should not be modified or deleted
        through this interface.
        """
        ...