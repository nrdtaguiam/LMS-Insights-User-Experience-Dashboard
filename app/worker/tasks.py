import asyncio
from app.worker.celery_app import celery_app
from app.services.etl import etl_pipeline

def run_async(coro):
    """Helper to run async code inside a synchronous celery task."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(name="app.worker.tasks.task_fetch_users")
def task_fetch_users():
    run_async(etl_pipeline.fetch_and_load_users())
    return "Users fetch completed"

@celery_app.task(name="app.worker.tasks.task_fetch_courses")
def task_fetch_courses():
    run_async(etl_pipeline.fetch_and_load_course_usage())
    return "Courses fetch completed"
