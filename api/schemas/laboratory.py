from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional
from api.schemas.patients import PatientsOut

class LaboratoryTestsIn(BaseModel):
    test_name: Optional[str] = None
    test_desc: Optional[str] = None
    test_price: float

    class Config:
        form_attributes = True
    
class LaboratoryTestsEdit(BaseModel):
    test_name: Optional[str] = None
    test_desc: Optional[str] = None
    test_price: float

    class Config:
        form_attributes = True

class LaboratoryTestsOut(BaseModel):
    test_id: Optional[int] = None
    hospital_id: Optional[int] = None
    test_name: Optional[str] = None
    test_desc: Optional[str] = None
    test_price: Optional[float] = None
    
    date_added: Optional[date] = None

    class Config:
        form_attributes = True
class LaboratoryRequestsIn(BaseModel):
    patient_id: Optional[int] = None
    test_id: Optional[int] = None

    class Config:
        form_attributes = True

class LaboratoryRequestsOut(BaseModel):
    hospital_id: Optional[int] = None
    request_id: Optional[int] = None
    
    test: Optional[LaboratoryTestsOut] = None
    patient: Optional[PatientsOut] = None
    date_added: Optional[date] = None
    
    class Config:
        form_attributes = True

class LaboratoryResultsIn(BaseModel):
    patient_id: Optional[int] = None
    observations: Optional[str] = None
    conclusion: Optional[str] = None

    class Config:
        form_attributes = True

class LaboratoryResultsEdit(BaseModel):
    observations: Optional[str] = None
    conclusion: Optional[str] = None

    class Config:
        form_attributes = True

class LaboratoryResultsOut(BaseModel):
    hospital_id: Optional[int] = None
    result_id: Optional[int] = None

    observations: Optional[str] = None
    conclusion: Optional[str] = None
    
    patient: Optional[PatientsOut] = None
    
    date_added: Optional[date] = None

    class Config:
        form_attributes = True

