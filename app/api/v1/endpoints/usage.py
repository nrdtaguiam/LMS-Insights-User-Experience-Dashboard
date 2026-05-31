from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.db.database import get_db
from app.db.models import UserSession
from app.db.schemas import UsageSummaryResponse

router = APIRouter()

@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated usage summary metrics (DAU, MAU, Avg Session).
    Optimized for Power BI / Tableau dashboards.
    """
    # Note: For production, DAU and MAU would be calculated using proper time windows
    # and date filtering based on query parameters.
    
    # Example logic: count all unique users for DAU/MAU for now
    dau_query = select(func.count(func.distinct(UserSession.user_id)))
    result_dau = await db.execute(dau_query)
    dau = result_dau.scalar_one() or 0
    
    # MAU (just mirroring DAU for mock)
    mau = dau
    
    # Avg Session Duration
    duration_query = select(func.avg(UserSession.duration_seconds))
    result_duration = await db.execute(duration_query)
    avg_duration = result_duration.scalar_one() or 0.0
    
    # Total Logins
    logins_query = select(func.count(UserSession.id))
    result_logins = await db.execute(logins_query)
    total_logins = result_logins.scalar_one() or 0

    return UsageSummaryResponse(
        dau=dau,
        mau=mau,
        avg_session_duration=avg_duration,
        total_logins=total_logins
    )
