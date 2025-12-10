from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from database.actions.billing import(
    show_total_billings, show_total_patient_billings,
    show_total_patient_billings_today
)
from api.schemas.billings import BillingOut

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/billings/show-all/", response_model=list[BillingOut])
async def show_all_billings(hospital_id: str):
    billings = await show_total_billings(hospital_id)
    if not billings:
        raise_exception(404, "Billings not found")
    return billings

@router.get("/billings/show-patient/", response_model=list[BillingOut])
async def show_all_patient_billings(hospital_id: str, patient_id: str):
    billings = await show_total_patient_billings(hospital_id, patient_id)
    if not billings:
        raise_exception(404, "Billings not found")
    return billings

@router.get("/billings/show-patient-today/", response_model=list[BillingOut])
async def show_all_patient_billings_today(hospital_id: str, patient_id: str):
    billings = await show_total_patient_billings_today(hospital_id, patient_id)
    if not billings:
        raise_exception(404, "Billings not found")
    return billings