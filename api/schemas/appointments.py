from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from api.schemas.workers import WorkersOut
from api.schemas.services import ServicesOut
from api.schemas.patients import PatientsOut

class AppointmentsIn(BaseModel):
    consultant_id: Optional[int] = None
    service_id: Optional[int] = None
    patient_id: Optional[int] = None
    appointment_desc: Optional[str] = None
    date_scheduled: Optional[date] = None
    time_scheduled: Optional[time] = None

    class Config:
        orm_mode = True

class AppointmentsEdit(BaseModel):
    appointment_desc: Optional[str] = None
    date_scheduled: Optional[date] = None
    time_scheduled: Optional[time] = None

    class Config:
        orm_mode = True

class AppointmentsOut(BaseModel):
    appointment_id: Optional[int] = None
    hospital_id: Optional[int] = None
    patient_id: Optional[int] = None
    consultant_id: Optional[int] = None
    service_id: Optional[int] = None

    appointment_desc: Optional[str] = None
    date_requested: Optional[date] = None
    time_requested: Optional[time] = None
    
    patient: Optional[PatientsOut] = None
    service: Optional[ServicesOut] = None
    consultant: Optional[WorkersOut] = None
    
    date_added: Optional[date] = None

    class Config:
        orm_mode = True
