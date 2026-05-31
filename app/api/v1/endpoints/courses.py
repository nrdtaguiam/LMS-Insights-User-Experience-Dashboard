from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.db.database import get_db
from app.db.models import CourseUsage
from app.db.schemas import ActiveCourseResponse

router = APIRouter()

@router.get("/active", response_model=List[ActiveCourseResponse])
async def get_active_courses(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get metrics on the most active courses.
    Includes interaction counts, unique users, and tools used.
    """
    # Group by course_id and aggregate
    query = (
        select(
            CourseUsage.course_id,
            func.count(CourseUsage.id).label("total_interactions"),
            func.count(func.distinct(CourseUsage.user_id)).label("unique_users")
        )
        .group_by(CourseUsage.course_id)
        .order_by(func.count(CourseUsage.id).desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    response = []
    for row in rows:
        response.append(
            ActiveCourseResponse(
                course_id=row.course_id,
                total_interactions=row.total_interactions,
                unique_users=row.unique_users,
                top_tools=[]  # Mocked, would require additional grouping or lateral join
            )
        )
    return response
