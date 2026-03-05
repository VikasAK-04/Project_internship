from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from datetime import datetime
from fastapi import Depends
from db import get_db
from models.LeadsModel import Leads


class LeadsClass:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def add_lead(self, parent_name, student_name, mobile_number,
                 email, lead_source, created_admin_id):

        # using ORM model instead of raw SQL for insert
        new_lead = Leads(
            parent_name       = parent_name,
            student_name      = student_name,
            mobile_number     = mobile_number,
            email             = email,
            lead_source       = lead_source,
            created_admin_id  = created_admin_id,
            created_date_time = datetime.now(),
            status            = 1
        )

        self.db.add(new_lead)
        self.db.commit()
        self.db.refresh(new_lead)
        return new_lead.id

    def bulk_add_leads(self, leads_list, created_admin_id):
        inserted_count = 0
        failed_rows    = []

        for index, row in enumerate(leads_list):
            try:
                new_lead = Leads(
                    parent_name       = str(row.get('parent_name', '')).strip(),
                    student_name      = str(row.get('student_name', '')).strip(),
                    mobile_number     = str(row.get('mobile_number', '')).strip(),
                    email             = str(row.get('email', '')).strip(),
                    lead_source       = str(row.get('lead_source', '')).strip(),
                    created_admin_id  = created_admin_id,
                    created_date_time = datetime.now(),
                    status            = 1
                )
                self.db.add(new_lead)
                inserted_count += 1

            except Exception as e:
                failed_rows.append({
                    "row":   index + 2,
                    "error": str(e)
                })

        self.db.commit()
        return inserted_count, failed_rows

    def get_all_leads(self):
        sql = text('''
            SELECT * FROM leads ORDER BY id DESC
        ''')
        responseData = self.db.execute(sql)
        return responseData.mappings().all()

    def get_lead_by_id(self, lead_id):
        data = {'lead_id': lead_id}
        sql = text('''
            SELECT * FROM leads WHERE id = :lead_id
        ''')
        responseData = self.db.execute(sql, data)
        return responseData.mappings().all()

    def check_duplicate_email(self, email):
        data = {'email': email}
        sql = text('''
            SELECT * FROM leads WHERE email = :email
        ''')
        responseData = self.db.execute(sql, data)
        return responseData.mappings().all()

    def update_lead_status(self, lead_id, status):
        data = {'lead_id': lead_id, 'status': status}
        sql = text('''
            UPDATE leads SET status = :status WHERE id = :lead_id
        ''')
        responseData = self.db.execute(sql, data)
        self.db.commit()
        return responseData.rowcount
