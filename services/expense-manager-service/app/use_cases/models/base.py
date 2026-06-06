"""Base model for the Expense Manager Service Use Case Models."""

import uuid

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseInput(BaseModel):
    """Base for write-side (input) models.

    No auto-generated id. Frozen and strict but without the inherited id field.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        alias_generator=to_camel,
    )


class BaseEntity(BaseInput):
    """Base model for all entities.

    Inherits standard config and adds default auto-generated id field.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
