from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PrescriptionsIn(BaseModel):
    patient_id: str
    drug_id: str
    drug_qty: int
    notes: Optional[str] = None

    class Config:
        orm_mode = True


class PrescriptionEntryOut(BaseModel):
    drug_name: str
    quantity: int
    notes: Optional[str] = None


class PrescriptionGroupedOut(BaseModel):
    prescription_id: str
    patient_name: str
    entries: List[PrescriptionEntryOut]
    dates: List[str]


class PrescriptionItemOut(BaseModel):
    item_id: str
    prescription_id: str
    drug_id: str
    drug_qty: int
    notes: Optional[str] = None
    drug: Optional[str] = None

    class Config:
        orm_mode = True


class PrescriptionOut(BaseModel):
    prescription_id: str
    hospital_id: str
    patient_id: str
    date_added: Optional[datetime] = None
    items: Optional[List[PrescriptionItemOut]] = None

    class Config:
        orm_mode = True
