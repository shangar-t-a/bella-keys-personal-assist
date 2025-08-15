"""Base DTO (Data Transfer Object) class for use cases."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseUseCaseDTO(BaseModel):
    """Base DTO class for use cases."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
