"""v1 routers for expense manager service."""

from fastapi import APIRouter
from utilities.scope_guard import require_scope

from app.routers.v1.endpoints.account import account_router
from app.routers.v1.endpoints.asset import router as asset_router
from app.routers.v1.endpoints.liability import router as liability_router
from app.routers.v1.endpoints.monthly_planner import router as monthly_planner_router
from app.routers.v1.endpoints.period import period_router
from app.routers.v1.endpoints.savings_bucket import router as savings_bucket_router
from app.routers.v1.endpoints.spending_entry import router as spending_account_router
from app.routers.v1.endpoints.wealth import router as wealth_router

router = APIRouter(prefix="/v1")

# Read scope guard applied to all sub-routers.
# Any token without bella-ems:read is rejected before reaching a route handler.
# bella-ems:write is validated at token issuance time (the client must request it),
# and is available in request.state.user["scope"] for future per-route write enforcement.
_read = require_scope("bella-ems:read")

router.include_router(account_router, dependencies=[_read])
router.include_router(period_router, dependencies=[_read])
router.include_router(spending_account_router, dependencies=[_read])
router.include_router(monthly_planner_router, dependencies=[_read])
router.include_router(savings_bucket_router, dependencies=[_read])
router.include_router(asset_router, dependencies=[_read])
router.include_router(liability_router, dependencies=[_read])
router.include_router(wealth_router, dependencies=[_read])
