from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from api.schemas.patients import PatientsOut

class DiagnosesIn(BaseModel):
    patient_id: Optional[str] = None
    symptoms: Optional[str] = None
    findings: Optional[str] = None
    suggested_diagnosis: Optional[str] = None

    class Config:
        form_attributes = True
    
class DiagnosesEdit(BaseModel):
    symptoms: Optional[str] = None
    findings: Optional[str] = None
    suggested_diagnosis: Optional[str] = None

    class Config:
        form_attributes = True
    

class DiagnosesOut(BaseModel):
    hospital_id: Optional[str] = None
    diagnosis_id: Optional[str] = None
    patient_id: Optional[str] = None

    symptoms: Optional[str] = None
    findings: Optional[str] = None
    suggested_diagnosis: Optional[str] = None
    patient: Optional[PatientsOut] = None
    
    date_added: datetime

    class Config:
        form_attributes = True