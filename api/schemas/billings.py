from pydantic import BaseModel
from datetime import date
from typing import Optional

class BillingOut(BaseModel):
    billing_id: Optional[str] = None
    hospital_id: Optional[str] = None
    patient_id: Optional[str] = None
    
    item: Optional[str] = None
    source: Optional[str] = None
    total: Optional[float] = None
    
    created_at: Optional[date] = None