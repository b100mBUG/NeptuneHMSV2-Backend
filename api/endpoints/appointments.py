from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.appointments import AppointmentsEdit, AppointmentsIn, AppointmentsOut
from database.actions.appointment import(
    add_appointment, fetch_appointments, 
    search_appointments, edit_appointment,
    delete_appointment, get_specific_appointment
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/appointments-fetch/", response_model=list[AppointmentsOut])
async def fetch_all_appointment_data(hospital_id: str, sort_term: str, sort_dir: str):
    appointments = await fetch_appointments(hospital_id, sort_term, sort_dir)
    if not appointments:
        raise_exception(404, "appointments not found")
    return appointments

@router.get("/appointments-search/", response_model=list[AppointmentsOut])
async def search_all_appointments(hospital_id: str, search_term: str):
    appointments = await search_appointments(hospital_id, search_term)
    if not appointments:
        raise_exception(404, "appointments not found")
    return appointments

@router.get("/appointments-specific/", response_model=AppointmentsOut)
async def fetch_specific_appointment(hospital_id: str, appointment_id: str):
    appointment = await get_specific_appointment(hospital_id, appointment_id)
    if not appointment:
        raise_exception(404, "appointment not found")
    return appointment

@router.post("/appointments-add/", response_model=AppointmentsOut)
async def add_appointments(hospital_id: str, appointment: AppointmentsIn):
    appointment = await add_appointment(hospital_id, appointment.model_dump())
    if not appointment:
        raise_exception(400, "failed to add appointment")
    return appointment

@router.put("/appointments-edit/", response_model=AppointmentsOut)
async def format_appointment(hospital_id: str, appointment_id: str, data: AppointmentsEdit):
    appointment = await edit_appointment(hospital_id, appointment_id, data.model_dump())
    if not appointment:
        raise_exception(400, "failed to edit appointment")
    return appointment
    
@router.delete("/appointments-delete/")
async def remove_appointment(hospital_id: str, appointment_id: str):
    try:
        await delete_appointment(hospital_id, appointment_id)
        return {'message': 'appointment deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
