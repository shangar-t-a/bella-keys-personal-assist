"""v1 routers for expense manager service."""

from fastapi import APIRouter

from app.routers.v1.endpoints.account import account_router
from app.routers.v1.endpoints.asset import router as asset_router
from app.routers.v1.endpoints.liability import router as liability_router
from app.routers.v1.endpoints.monthly_planner import router as monthly_planner_router
from app.routers.v1.endpoints.period import period_router
from app.routers.v1.endpoints.savings_bucket import router as savings_bucket_router
from app.routers.v1.endpoints.spending_entry import router as spending_account_router

router = APIRouter(prefix="/v1")

router.include_router(account_router)
router.include_router(period_router)
router.include_router(spending_account_router)
router.include_router(monthly_planner_router)
router.include_router(savings_bucket_router)
router.include_router(asset_router)
router.include_router(liability_router)
