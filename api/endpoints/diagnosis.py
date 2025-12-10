from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.diagnoses import DiagnosesEdit, DiagnosesIn, DiagnosesOut
from database.actions.diagnosis import(
    add_diagnosis, fetch_diagnosis, edit_diagnosis,
    search_diagnosis, delete_diagnosis, get_specific_diagnosis
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/diagnosis-fetch/", response_model=list[DiagnosesOut])
async def fetch_all_diagnosis_data(hospital_id: str, sort_term: str, sort_dir: str):
    diagnosiss = await fetch_diagnosis(hospital_id, sort_term, sort_dir)
    if not diagnosiss:
        raise_exception(404, "diagnosiss not found")
    return diagnosiss

@router.get("/diagnosis-search/", response_model=list[DiagnosesOut])
async def search_all_diagnosiss(hospital_id: str, search_term: str):
    diagnosiss = await search_diagnosis(hospital_id, search_term)
    if not diagnosiss:
        raise_exception(404, "diagnosiss not found")
    return diagnosiss

@router.get("/diagnosis-specific/", response_model=DiagnosesOut)
async def fetch_specific_diagnosis(hospital_id: str, diagnosis_id: str):
    diagnosis = await get_specific_diagnosis(hospital_id, diagnosis_id)
    if not diagnosis:
        raise_exception(404, "diagnosis not found")
    return diagnosis

@router.post("/diagnosis-add/", response_model=DiagnosesOut)
async def add_diagnoses(hospital_id: str, diagnoses: DiagnosesIn):
    diagnosis = await add_diagnosis(hospital_id, diagnoses.model_dump())
    if not diagnosis:
        raise_exception(400, "failed to add diagnosis")
    return diagnosis

@router.put("/diagnosis-edit/", response_model=DiagnosesOut)
async def format_diagnosis(hospital_id: str, diagnosis_id: str, data: DiagnosesEdit):
    print("Diagnosis model: ", data.model_dump())
    diagnosis = await edit_diagnosis(hospital_id, diagnosis_id, data.model_dump())
    if not diagnosis:
        raise_exception(400, "failed to edit diagnosis")
    return diagnosis
    
@router.delete("/diagnosis-delete/")
async def remove_diagnosis(hospital_id: str, diagnosis_id: str):
    try:
        await delete_diagnosis(hospital_id, diagnosis_id)
        return {'message': 'diagnosis deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
