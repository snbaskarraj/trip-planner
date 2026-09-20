"""Pure business rules. Kept importable by unit tests and by the routers."""

from datetime import date, time


class DomainError(ValueError):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.code = code
        self.message = message


def assert_time_order(start: time | None, end: time | None) -> None:
    """A Day/Activity cannot be saved with an end time before its start time."""
    if start is not None and end is not None and end < start:
        raise DomainError(
            "end_time must not be before start_time",
            code="END_BEFORE_START",
        )


def assert_date_order(start: date | None, end: date | None) -> None:
    if start is not None and end is not None and end < start:
        raise DomainError(
            "end_date must not be before start_date",
            code="END_BEFORE_START",
        )
