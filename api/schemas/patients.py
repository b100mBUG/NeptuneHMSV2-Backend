from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional

class PatientsIn(BaseModel):
    patient_name: Optional[str] = None
    patient_gender: Optional[str] = None
    patient_dob: Optional[date] = None
    patient_email: Optional[EmailStr] = None
    patient_phone: Optional[str] = None
    patient_id_number: Optional[str] = None
    patient_address: Optional[str] = None
    patient_weight: Optional[float] = None
    patient_avg_pulse: Optional[float] = None
    patient_bp: Optional[float] = None
    patient_chronic_condition: Optional[str] = None
    patient_allergy: Optional[str] = None
    patient_blood_type: Optional[str] = None

    class Config:
        form_attributes = True

class PatientsEdit(BaseModel):
    patient_name: Optional[str] = None
    patient_gender: Optional[str] = None
    patient_dob: Optional[date] = None
    patient_email: Optional[EmailStr] = None
    patient_phone: Optional[str] = None
    patient_id_number: Optional[str] = None
    patient_address: Optional[str] = None
    patient_weight: Optional[float] = None
    patient_avg_pulse: Optional[float] = None
    patient_bp: Optional[float] = None
    patient_chronic_condition: Optional[str] = None
    patient_allergy: Optional[str] = None
    patient_blood_type: Optional[str] = None

    class Config:
        form_attributes = True

class PatientsOut(BaseModel):
    patient_id: str
    hospital_id: str
    patient_name: Optional[str] = None
    patient_gender: Optional[str] = None
    patient_dob: Optional[date] = None
    patient_email: Optional[EmailStr] = None
    patient_phone: Optional[str] = None
    patient_id_number: Optional[str] = None
    patient_address: Optional[str] = None
    patient_weight: Optional[float] = None
    patient_avg_pulse: Optional[float] = None
    patient_bp: Optional[float] = None
    patient_chronic_condition: Optional[str] = None
    patient_allergy: Optional[str] = None
    patient_blood_type: Optional[str] = None
    
    date_added: Optional[date] = None
    

    class Config:
        form_attributes = True