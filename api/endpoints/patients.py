from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.patients import PatientsIn, PatientsOut, PatientsEdit
from database.actions.patients import(
    add_patients, edit_patients, delete_patient,
    get_specific_patient, search_patients, 
    fetch_patients
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/patients-fetch/", response_model=list[PatientsOut])
async def fetch_all_patient_data(hospital_id, sort_term: str, sort_dir: str):
    patients = await fetch_patients(hospital_id, sort_term, sort_dir)
    if not patients:
        raise_exception(404, "patients not found")
    return patients

@router.get("/patients-search/", response_model=list[PatientsOut])
async def search_all_patients(hospital_id: int, search_by: str, search_term: str):
    patients = await search_patients(hospital_id, search_by, search_term)
    if not patients:
        raise_exception(404, "patients not found")
    return patients

@router.get("/patients-specific/", response_model=PatientsOut)
async def fetch_specific_patient(hospital_id: int, patient_id: int):
    patient = await get_specific_patient(hospital_id, patient_id)
    if not patient:
        raise_exception(404, "patient not found")
    return patient

@router.post("/patients-add/", response_model=PatientsOut)
async def add_patient(hospital_id: int, patient: PatientsIn):
    patient = await add_patients(hospital_id, patient.model_dump())
    if not patient:
        raise_exception(400, "failed to add patient")
    return patient

@router.put("/patients-edit/", response_model=PatientsOut)
async def format_patient(hospital_id: int, patient_id: int, pat_data: PatientsEdit):
    patient = await edit_patients(hospital_id, patient_id, pat_data.model_dump())
    if not patient:
        raise_exception(400, "failed to edit patient")
    return patient
    
@router.delete("/patients-delete/")
async def remove_patient(hospital_id: int, patient_id: int):
    try:
        await delete_patient(hospital_id, patient_id)
        return {'message': 'patient deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")