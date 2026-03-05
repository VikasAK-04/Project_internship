from pydantic import BaseModel, EmailStr


class LeadSingleEntrySchema(BaseModel):
    parent_name:      str
    student_name:     str
    mobile_number:    str
    email:            EmailStr   
    lead_source:      str  
    created_admin_id: int


class LeadUpdateStatusSchema(BaseModel):
    lead_id: int
    status:  int