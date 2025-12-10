from pydantic import BaseModel, EmailStr
from datetime import datetime

class HospitalsIn(BaseModel):
    hospital_name: str
    hospital_email: EmailStr
    hospital_contact: str
    hospital_password: str
    diagnosis_fee: float

    class Config:
        form_attributes = True

class HospitalsEdit(BaseModel):
    hospital_name: str
    hospital_email: EmailStr
    hospital_contact: str
    diagnosis_fee: float

    class Config:
        form_attributes = True

class Signin(BaseModel):
    hospital_email: str
    hospital_password: str
    
    class Config:
        form_attributes = True

class PasswordChange(BaseModel):
    former_password: str
    new_password: str
    
    class Config:
        form_attributes = True

class HospitalsOut(BaseModel):
    hospital_id: str
    hospital_name: str
    hospital_email: EmailStr
    hospital_contact: str
    diagnosis_fee: float
    expiry_date: datetime

    class Config:
        form_attributes = True