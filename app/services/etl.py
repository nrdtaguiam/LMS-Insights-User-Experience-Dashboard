import logging
from datetime import datetime, timezone
from app.services.blackboard import bb_client
from app.db.database import AsyncSessionLocal
from app.db.models import UserSession, CourseUsage, SystemMetric

logger = logging.getLogger(__name__)

class ETLPipeline:
    @staticmethod
    def _parse_bb_date(date_str: str) -> datetime:
        """Helper to parse Blackboard ISO8601 dates and handle missing/malformed."""
        if not date_str:
            return datetime.now(timezone.utc)
        try:
            # typical format: 2021-08-01T12:00:00.000Z
            date_str = date_str.replace("Z", "+00:00")
            return datetime.fromisoformat(date_str)
        except ValueError:
            logger.warning(f"Could not parse date: {date_str}")
            return datetime.now(timezone.utc)

    async def fetch_and_load_users(self):
        """Example ETL task for fetching user logins or sessions."""
        # Note: In reality, Blackboard API endpoints for analytics/sessions vary.
        # This is a scaffold showing the ETL pattern.
        endpoint = "/learn/api/public/v1/users"
        data = await bb_client.make_request("GET", endpoint)
        
        results = data.get("results", [])
        
        async with AsyncSessionLocal() as session:
            for item in results:
                # Transform data
                user_id = item.get("uuid") or item.get("id")
                # Load
                # Here we mock session creation as if we fetched session data
                new_session = UserSession(
                    user_id=user_id,
                    session_start=datetime.now(timezone.utc), # Mocked
                    duration_seconds=3600.0 # Mocked
                )
                session.add(new_session)
            await session.commit()
            logger.info(f"Loaded {len(results)} user records into database.")

    async def fetch_and_load_course_usage(self):
        """Example ETL task for fetching course usage."""
        endpoint = "/learn/api/public/v3/courses"
        data = await bb_client.make_request("GET", endpoint)
        
        results = data.get("results", [])
        
        async with AsyncSessionLocal() as session:
            for item in results:
                course_id = item.get("courseId") or item.get("id")
                usage = CourseUsage(
                    course_id=course_id,
                    user_id="system_generated",
                    interaction_type="course_access",
                    timestamp=datetime.now(timezone.utc)
                )
                session.add(usage)
            await session.commit()
            logger.info(f"Loaded {len(results)} course records into database.")

etl_pipeline = ETLPipeline()
