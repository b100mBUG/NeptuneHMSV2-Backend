from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PrescriptionsIn(BaseModel):
    patient_id: int
    drug_id: int
    drug_qty: int
    notes: Optional[str] = None

    class Config:
        orm_mode = True


class PrescriptionEntryOut(BaseModel):
    drug_name: str
    quantity: int
    notes: Optional[str] = None


class PrescriptionGroupedOut(BaseModel):
    prescription_id: int
    patient_name: str
    entries: List[PrescriptionEntryOut]
    dates: List[str]


class PrescriptionItemOut(BaseModel):
    item_id: int
    prescription_id: int
    drug_id: int
    drug_qty: int
    notes: Optional[str] = None
    drug: Optional[str] = None

    class Config:
        orm_mode = True


class PrescriptionOut(BaseModel):
    prescription_id: int
    hospital_id: int
    patient_id: int
    date_added: Optional[datetime] = None
    items: Optional[List[PrescriptionItemOut]] = None

    class Config:
        orm_mode = True
