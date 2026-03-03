from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db import Base

class Leads(Base):
    __tablename__ = "leads"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    parent_name      = Column(String(255), nullable=False)
    student_name     = Column(String(255), nullable=False)
    mobile_number    = Column(String(20),  nullable=False)
    email            = Column(String(255), nullable=False)
    lead_source      = Column(String(100), nullable=True)
    created_admin_id = Column(Integer,     nullable=True)
    created_date_time = Column(DateTime,   default=datetime.now)
    status           = Column(Integer,     default=1)