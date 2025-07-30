"""Mappers for accounts."""

from app.entities.models.accounts import AccountName, MonthYear
from app.use_cases.dto.accounts import AccountNameDTO, MonthYearDTO


class AccountNameMapper:
    """Mapper for AccountName entity and AccountNameDTO."""

    @staticmethod
    def to_entity(dto: AccountNameDTO) -> AccountName:
        """Convert AccountNameDTO to AccountName entity."""
        return AccountName(account_name=dto.account_name, id=dto.id)

    @staticmethod
    def to_dto(entity: AccountName) -> AccountNameDTO:
        """Convert AccountName entity to AccountNameDTO."""
        return AccountNameDTO(account_name=entity.account_name, id=entity.id)


class MonthYearMapper:
    """Mapper for MonthYear entity and MonthYearDTO."""

    @staticmethod
    def to_entity(dto: MonthYearDTO) -> MonthYear:
        """Convert MonthYearDTO to MonthYear entity."""
        return MonthYear(month=dto.month, year=dto.year, id=dto.id)

    @staticmethod
    def to_dto(entity: MonthYear) -> MonthYearDTO:
        """Convert MonthYear entity to MonthYearDTO."""
        return MonthYearDTO(month=entity.month, year=entity.year, id=entity.id)
