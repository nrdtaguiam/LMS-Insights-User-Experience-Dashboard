from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class UserSession(Base):
    """
    Records individual user sessions for DAU/MAU and session duration.
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_start = Column(DateTime(timezone=True), nullable=False)
    session_end = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CourseUsage(Base):
    """
    Records course access and content interaction metrics.
    """
    __tablename__ = "course_usage"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    interaction_type = Column(String, nullable=False) # e.g., 'access', 'content_view', 'tool_use'
    tool_name = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemMetric(Base):
    """
    Records Blackboard API latencies, error rates, etc.
    """
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True, nullable=False)
    latency_ms = Column(Float, nullable=False)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
