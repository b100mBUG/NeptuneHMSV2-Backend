from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class WorkersIn(BaseModel):
    worker_name: Optional[str] = None
    worker_email: Optional[EmailStr] = None
    worker_phone: Optional[str] = None
    worker_role: Optional[str] = None
    worker_password: Optional[str] = None

    class Config:
        form_attributes = True

class WorkersEdit(BaseModel):
    worker_name: Optional[str] = None
    worker_email: Optional[EmailStr] = None
    worker_phone: Optional[str] = None
    worker_role: Optional[str] = None
    

    class Config:
        form_attributes = True

class Signin(BaseModel):
    worker_email: Optional[str] = None
    worker_password: Optional[str] = None
    
    class Config:
        form_attributes = True

class PasswordChange(BaseModel):
    former_password: Optional[str] = None
    new_password: Optional[str] = None
    
    class Config:
        form_attributes = True

class WorkersOut(BaseModel):
    worker_id: str
    hospital_id: str
    worker_name: Optional[str] = None
    worker_email: Optional[EmailStr] = None
    worker_phone: Optional[str] = None
    worker_role: Optional[str] = None
    
    date_added: Optional[date] = None

    class Config:
        form_attributes = True