from pydantic import BaseModel
from datetime import date
from typing import Optional


class DrugsIn(BaseModel):
    drug_name: Optional[str] = None
    drug_category: Optional[str] = None
    drug_desc: Optional[str] = None
    drug_quantity: Optional[int] = None
    drug_price: Optional[float] = None
    drug_expiry: Optional[date] = None

    class Config:
        form_attributes = True

class DrugsEdit(BaseModel):
    drug_name: Optional[str] = None
    drug_category: Optional[str] = None
    drug_desc: Optional[str] = None
    drug_quantity: Optional[int] = None
    drug_price: Optional[float] = None
    drug_expiry: Optional[date] = None

    class Config:
        form_attributes = True

class DrugsOut(BaseModel):
    drug_id: Optional[str] = None
    hospital_id: Optional[str] = None
    drug_name: Optional[str] = None
    drug_category: Optional[str] = None
    drug_desc: Optional[str] = None
    drug_quantity: Optional[int] = None
    drug_price: Optional[float] = None
    drug_expiry: Optional[date] = None
    
    date_added: Optional[date]

    class Config:
        form_attributes = True
