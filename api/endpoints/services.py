from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.services import ServicesEdit, ServicesIn, ServicesOut
from database.actions.service import(
    add_services, fetch_services, search_services,
    get_specific_service, edit_service, delete_service
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/services-fetch/", response_model=list[ServicesOut])
async def fetch_all_service_data(hospital_id: str, sort_term: str, sort_dir: str):
    services = await fetch_services(hospital_id, sort_term, sort_dir)
    if not services:
        raise_exception(404, "services not found")
    return services

@router.get("/services-search/", response_model=list[ServicesOut])
async def search_all_services(hospital_id: str, search_term: str):
    services = await search_services(hospital_id, search_term)
    if not services:
        raise_exception(404, "services not found")
    return services

@router.get("/services-specific/", response_model=ServicesOut)
async def fetch_specific_service(hospital_id: str, service_id: str):
    service = await get_specific_service(hospital_id, service_id)
    if not service:
        raise_exception(404, "service not found")
    return service

@router.post("/services-add/", response_model=ServicesOut)
async def add_service(hospital_id: str, service: ServicesIn):
    service = await add_services(hospital_id, service.model_dump())
    if not service:
        raise_exception(400, "failed to add service")
    return service

@router.put("/services-edit/", response_model=ServicesOut)
async def format_service(hospital_id: str, service_id: str, data: ServicesEdit):
    service = await edit_service(hospital_id, service_id, data.model_dump())
    if not service:
        raise_exception(400, "failed to edit service")
    return service
    
@router.delete("/services-delete/")
async def remove_service(hospital_id: str, service_id: str):
    try:
        await delete_service(hospital_id, service_id)
        return {'message': 'service deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
