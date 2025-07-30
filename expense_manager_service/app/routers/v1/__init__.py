"""v1 routers for expense manager service."""

from fastapi import APIRouter

from app.routers.v1.endpoints.accounts import (
    account_router,
    month_year_router,
)
from app.routers.v1.endpoints.spending_account import router as spending_account_router

router = APIRouter(prefix="/v1")

router.include_router(account_router)
router.include_router(month_year_router)
router.include_router(spending_account_router)
