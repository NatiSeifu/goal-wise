"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.calculation_snapshots import router as calculation_snapshots_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.financial_inputs import expense_router, income_router, profile_router
from app.api.v1.goals import router as goals_router
from app.api.v1.planning_import import router as planning_import_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(calculation_snapshots_router)
api_router.include_router(dashboard_router)
api_router.include_router(goals_router)
api_router.include_router(planning_import_router)
api_router.include_router(profile_router)
api_router.include_router(income_router)
api_router.include_router(expense_router)
