from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API...")
    # Initialize DB tables (for demo purposes, use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API...")
    await engine.dispose()

@app.get("/")
def root():
    return {"message": "Welcome to the LMS Data Visualization API. See /docs for API documentation."}
