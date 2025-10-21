"""Base model for the Expense Manager Service Use Case Models."""

import uuid

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseEntity(BaseModel):
    """Base model for all use case models.

    This model provides common fields, settings and validation for all models.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
