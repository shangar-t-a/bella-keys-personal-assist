"""Generic domain models for sorting."""

from enum import StrEnum


class SortOrder(StrEnum):
    """Sort order for sorting."""

    ASC = "asc"
    DESC = "desc"
