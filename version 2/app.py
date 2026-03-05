from fastapi import FastAPI
from db import engine, Base
from sqlalchemy import text



# ── this creates the table in PostgreSQL using a raw SQL query
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            parent_name VARCHAR(255) NOT NULL,
            student_name VARCHAR(255) NOT NULL,
            mobile_number VARCHAR(20) NOT NULL,
            email VARCHAR(255) NOT NULL,
            lead_source VARCHAR(100),
            created_admin_id INTEGER,
            created_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 1
        );
    """))

app = FastAPI()

from routes.LeadsRoutes import router as leads_router
app.include_router(leads_router, prefix="/leads", tags=["Leads"])