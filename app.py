from fastapi import FastAPI
from db import engine, Base

# ── this line MUST be here — imports the model so SQLAlchemy knows about it
from models.LeadsModel import Leads

# ── this line CREATES the table in PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI()

from routes.LeadsRoutes import router as leads_router
app.include_router(leads_router, prefix="/leads", tags=["Leads"])