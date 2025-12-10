from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.hospitals import (
    HospitalsEdit, HospitalsIn, HospitalsOut,
    Signin, PasswordChange
)
from database.actions.hospital import(
    add_hospital, fetch_hospitals, search_hospitals,
    edit_hospital, get_specific_hospital, signin,
    change_password, delete_hospital, renew_hospital_plan
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/hospitals-fetch/", response_model=list[HospitalsOut])
async def fetch_all_hospital_data(sort_term: str, sort_dir: str):
    hospitals = await fetch_hospitals(sort_term, sort_dir)
    if not hospitals:
        raise_exception(404, "hospitals not found")
    return hospitals

@router.get("/hospitals-search/", response_model=list[HospitalsOut])
async def search_all_hospitals(search_by: str, search_term: str):
    hospitals = await search_hospitals(search_by, search_term)
    if not hospitals:
        raise_exception(404, "hospitals not found")
    return hospitals

@router.get("/hospitals-specific/", response_model=HospitalsOut)
async def fetch_specific_hospital(hospital_id: str):
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise_exception(404, "hospital not found")
    return hospital

@router.post("/hospitals-add/", response_model=HospitalsOut)
async def add_hospitals(hospital: HospitalsIn):
    hospital = await add_hospital(hospital.model_dump())
    if not hospital:
        raise_exception(400, "failed to add hospital")
    return hospital

@router.post("/hospitals-signin/", response_model=HospitalsOut)
async def hospital_login(hospital_detail: Signin):
    hospital = await signin(hospital_detail.model_dump())
    if not hospital:
        raise_exception(404, "hospital not found")
    return hospital

@router.put("/hospitals-edit/", response_model=HospitalsOut)
async def format_hospital(hospital_id: str, data: HospitalsEdit):
    hospital = await edit_hospital(hospital_id, data.model_dump())
    if not hospital:
        raise_exception(400, "failed to edit hospital")
    return hospital

@router.put("/hospitals-change-password/", response_model=HospitalsOut)
async def change_hospital_password(hospital_id: str, password_detail: PasswordChange):
    hospital = await change_password(hospital_id, password_detail.model_dump())
    if not hospital:
        raise_exception(400, "failed to change password")
    return hospital

@router.put("/renew-activation/")
async def renew_plan(hospital_id: str, activation_key: str):
    resp = await renew_hospital_plan(hospital_id, activation_key)
    return resp
    
@router.delete("/hospitals-delete/")
async def remove_hospital(hospital_id: str):
    try:
        await delete_hospital(hospital_id)
        return {'message': 'hospital deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")