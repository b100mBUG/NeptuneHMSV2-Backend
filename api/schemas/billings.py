from pydantic import BaseModel
from datetime import date
from typing import Optional

class BillingOut(BaseModel):
    billing_id: Optional[int] = None
    hospital_id: Optional[int] = None
    patient_id: Optional[int] = None
    
    item: Optional[str] = None
    source: Optional[str] = None
    total: Optional[float] = None
    
    created_at: Optional[date] = None