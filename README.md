# LMS Data Visualization and UX Improvement API

This project serves as a backend middleware designed to extract data from the Blackboard Learn REST API, transform it, and load it into a PostgreSQL database. It exposes clean endpoints tailored for downstream visualization tools like Power BI or Tableau.

## 🚀 Tech Stack

* **Backend Framework:** FastAPI (Python 3.9+)
* **Database:** PostgreSQL (with SQLAlchemy Async)
* **Task Queue:** Celery with Redis broker
* **HTTP Client:** HTTPX for async REST requests

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.9+** 
2. **PostgreSQL** (running locally or via Docker)
3. **Redis** (running locally or via Docker, required for Celery task queuing)

---

## ⚙️ Setup Instructions

### 1. Clone or Open the Project
Navigate to the project directory:
```bash
cd blackboard_powerbi_integration
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies:
```bash
python -m venv venv
```
Activate the environment:
* **Windows:** `venv\Scripts\activate`
* **Mac/Linux:** `source venv/bin/activate`

### 3. Install Dependencies
Install the required Python packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and update it with your actual credentials.
```bash
cp .env.example .env
```
Open `.env` and fill in:
* **Blackboard Credentials:** `BLACKBOARD_API_URL`, `BLACKBOARD_CLIENT_ID`, `BLACKBOARD_CLIENT_SECRET` (Do not commit your real `.env` file to version control).
* **Database Credentials:** Update `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` to match your local PostgreSQL instance.
* **Celery:** Verify that `CELERY_BROKER_URL` points to your active Redis instance.

### 5. Setup Database
Create the empty database in your PostgreSQL instance:
```sql
CREATE DATABASE lms_data;
```
*(Note: Upon startup, the FastAPI application currently uses SQLAlchemy's `create_all` to automatically create the tables for you. For production, consider using Alembic migrations).*

---

## ▶️ Running the Application

To run the full stack, you will need two separate terminal windows (one for the API, one for the Celery worker). 
**Make sure your virtual environment is activated in both.**

### 1. Start the FastAPI Server
Run the API using `uvicorn`:
```bash
uvicorn main:app --reload
```
The API will be available at: http://127.0.0.1:8000
Interactive API Documentation (Swagger UI): http://127.0.0.1:8000/docs

### 2. Start the Celery Worker
In a new terminal window, start the Celery worker to process background ETL tasks:
```bash
# On Windows, use the 'solo' pool to avoid fork issues:
celery -A app.worker.celery_app worker --pool=solo --loglevel=info

# On Mac/Linux:
celery -A app.worker.celery_app worker --loglevel=info
```

*(Optional)* To run scheduled cron jobs, you would also start the celery beat scheduler:
```bash
celery -A app.worker.celery_app beat --loglevel=info
```

---

## 📡 API Endpoints Overview

The API provides the following core endpoints (prefixed with `/api/v1`):

* **`GET /api/v1/usage/summary`**: Returns aggregated usage metrics like DAU (Daily Active Users), MAU, and average session durations. Optimized for Power BI.
* **`GET /api/v1/courses/active`**: Returns an aggregated list of the most active courses alongside interaction counts and unique user views.
* **`POST /api/v1/webhooks/blackboard`**: Endpoint ready to receive real-time delta updates directly from Blackboard.

---

## 📝 ETL Pipeline Details
The core ETL logic resides in `app/services/etl.py`. It uses the asynchronous `BlackboardClient` (`app/services/blackboard.py`) to authenticate using OAuth 2.0 Client Credentials and manages strict rate limiting via internal Semaphores. 
