from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- User Session Schemas ---
class UserSessionBase(BaseModel):
    user_id: str
    session_start: datetime
    session_end: Optional[datetime] = None
    duration_seconds: Optional[float] = None

class UserSessionCreate(UserSessionBase):
    pass

class UserSessionResponse(UserSessionBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Course Usage Schemas ---
class CourseUsageBase(BaseModel):
    course_id: str
    user_id: str
    interaction_type: str
    tool_name: Optional[str] = None
    timestamp: datetime

class CourseUsageCreate(CourseUsageBase):
    pass

class CourseUsageResponse(CourseUsageBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Summary Schemas for Visualizations ---
class UsageSummaryResponse(BaseModel):
    dau: int
    mau: int
    avg_session_duration: float
    total_logins: int

class ActiveCourseResponse(BaseModel):
    course_id: str
    total_interactions: int
    unique_users: int
    top_tools: List[str]
