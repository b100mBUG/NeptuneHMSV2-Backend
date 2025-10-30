from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional


class ServicesIn(BaseModel):
    service_name: str
    service_desc: str
    service_price: float

    class Config:
        form_attributes = True

class ServicesEdit(BaseModel):
    service_name: str
    service_desc: str
    service_price: float

    class Config:
        form_attributes = True

class ServicesOut(BaseModel):
    service_id: int
    hospital_id: int
    service_name: str
    service_desc: str
    service_price: float
    
    date_added: Optional[date] = None

    class Config:
        form_attributes = True