import csv
import io
from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from db import get_db
from classes.LeadsClass import LeadsClass
from schemas.LeadsSchema import LeadSingleEntrySchema, LeadUpdateStatusSchema
from pydantic import ValidationError

router = APIRouter()


@router.post("/single-entry")
def addSingleLead(
    db:               Session = Depends(get_db),
    parent_name:      str     = Form(...),
    student_name:     str     = Form(...),
    mobile_number:    str     = Form(...),
    email:            str     = Form(...),
    lead_source:      str     = Form(...),
    created_admin_id: int     = Form(...)
):
    # pydantic validation
    try:
        LeadSingleEntrySchema(
            parent_name      = parent_name,
            student_name     = student_name,
            mobile_number    = mobile_number,
            email            = email,
            lead_source      = lead_source,
            created_admin_id = created_admin_id
        )
    except ValidationError as e:
        return {"errFlag": 1, "message": str(e.errors()[0]['msg'])}

    leads = LeadsClass(db)

    duplicate = leads.check_duplicate_email(email)
    if len(duplicate) > 0:
        return {"errFlag": 1, "message": "Lead with this email already exists"}

    lead_id = leads.add_lead(
        parent_name      = parent_name,
        student_name     = student_name,
        mobile_number    = mobile_number,
        email            = email,
        lead_source      = lead_source,
        created_admin_id = created_admin_id
    )

    if lead_id:
        return {"errFlag": 0, "message": "Lead Added Successfully", "lead_id": lead_id}
    else:
        return {"errFlag": 1, "message": "Failed to Add Lead"}


@router.post("/bulk-upload")
def bulkUploadLeads(
    db:               Session    = Depends(get_db),
    file:             UploadFile = File(...),
    created_admin_id: int        = Form(...)
):
    if not file.filename.endswith('.csv'):
        return {"errFlag": 1, "message": "Only CSV files are allowed"}

    try:
        contents   = file.file.read()
        decoded    = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))

        required_columns = {
            'parent_name', 'student_name',
            'mobile_number', 'email', 'lead_source'
        }
        if not required_columns.issubset(set(csv_reader.fieldnames or [])):
            return {
                "errFlag": 1,
                "message": f"CSV must have these columns: {', '.join(required_columns)}"
            }

        leads_list = list(csv_reader)

    except Exception as e:
        return {"errFlag": 1, "message": f"Failed to read CSV: {str(e)}"}

    if len(leads_list) == 0:
        return {"errFlag": 1, "message": "CSV file is empty"}

    leads = LeadsClass(db)
    inserted_count, failed_rows = leads.bulk_add_leads(leads_list, created_admin_id)

    return {
        "errFlag":      0,
        "message":      f"{inserted_count} leads uploaded successfully",
        "total_rows":   len(leads_list),
        "inserted":     inserted_count,
        "failed_count": len(failed_rows),
        "failed_rows":  failed_rows
    }


@router.get("/all")
def getAllLeads(db: Session = Depends(get_db)):
    leads     = LeadsClass(db)
    all_leads = leads.get_all_leads()
    return [dict(row) for row in all_leads]


@router.get("/get-by-id/{lead_id}")
def getLeadById(lead_id: int, db: Session = Depends(get_db)):
    leads     = LeadsClass(db)
    lead_data = leads.get_lead_by_id(lead_id)

    if len(lead_data) == 0:
        return {"errFlag": 1, "message": "Lead not found"}

    return [dict(row) for row in lead_data]


@router.post("/update-status")
def updateLeadStatus(
    db:      Session = Depends(get_db),
    lead_id: int     = Form(...),
    status:  int     = Form(...)
):
    # pydantic validation
    try:
        LeadUpdateStatusSchema(lead_id=lead_id, status=status)
    except ValidationError as e:
        return {"errFlag": 1, "message": str(e.errors()[0]['msg'])}

    leads         = LeadsClass(db)
    rows_affected = leads.update_lead_status(lead_id, status)

    if rows_affected > 0:
        return {"errFlag": 0, "message": "Status Updated Successfully"}
    else:
        return {"errFlag": 1, "message": "Failed to Update Status"}