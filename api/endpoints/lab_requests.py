from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.laboratory import LaboratoryRequestsOut, LaboratoryRequestsIn
from database.actions.lab_request import(
    add_lab_request, fetch_lab_requests, search_lab_request,
    delete_lab_request, get_specific_lab_request
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/lab_requests-fetch/", response_model=list[LaboratoryRequestsOut])
async def fetch_all_lab_request_data(hospital_id: str, sort_term: str, sort_dir: str):
    lab_requests = await fetch_lab_requests(hospital_id, sort_term, sort_dir)
    if not lab_requests:
        raise_exception(404, "lab_requests not found")
    return lab_requests

@router.get("/lab_requests-search/", response_model=list[LaboratoryRequestsOut])
async def search_all_lab_requests(hospital_id: str, search_term: str):
    lab_requests = await search_lab_request(hospital_id, search_term)
    if not lab_requests:
        raise_exception(404, "lab_requests not found")
    return lab_requests

@router.get("/lab_requests-specific/", response_model=LaboratoryRequestsOut)
async def fetch_specific_lab_request(hospital_id: str, lab_request_id: str):
    lab_request = await get_specific_lab_request(hospital_id, lab_request_id)
    if not lab_request:
        raise_exception(404, "lab_request not found")
    return lab_request

@router.post("/lab_requests-add/", response_model=LaboratoryRequestsOut)
async def add_lab_requests(hospital_id: str, lab_request: LaboratoryRequestsIn):
    lab_request = await add_lab_request(hospital_id, lab_request.model_dump())
    if not lab_request:
        raise_exception(400, "failed to add lab_request")
    return lab_request

    
@router.delete("/lab_requests-delete/")
async def remove_lab_request(hospital_id: str, lab_request_id: str):
    try:
        await delete_lab_request(hospital_id, lab_request_id)
        return {'message': 'lab_request deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
