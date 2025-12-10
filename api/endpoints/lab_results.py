from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.laboratory import LaboratoryResultsEdit, LaboratoryResultsIn, LaboratoryResultsOut
from database.actions.lab_result import(
    add_lab_result, fetch_lab_results, 
    search_lab_results, edit_lab_result,
    get_specific_result, delete_lab_result
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/lab_results-fetch/", response_model=list[LaboratoryResultsOut])
async def fetch_all_lab_result_data(hospital_id: str, sort_term: str, sort_dir: str):
    lab_results = await fetch_lab_results(hospital_id, sort_term, sort_dir)
    if not lab_results:
        raise_exception(404, "lab_results not found")
    return lab_results

@router.get("/lab_results-search/", response_model=list[LaboratoryResultsOut])
async def search_all_lab_results(hospital_id: str, search_term: str):
    lab_results = await search_lab_results(hospital_id, search_term)
    if not lab_results:
        raise_exception(404, "lab_results not found")
    return lab_results

@router.get("/lab_results-specific/", response_model=LaboratoryResultsOut)
async def fetch_specific_lab_result(hospital_id: str, lab_result_id: str):
    lab_result = await get_specific_result(hospital_id, lab_result_id)
    if not lab_result:
        raise_exception(404, "lab_result not found")
    return lab_result

@router.post("/lab_results-add/", response_model=LaboratoryResultsOut)
async def add_lab_results(hospital_id: str, lab_result: LaboratoryResultsIn):
    lab_result = await add_lab_result(hospital_id, lab_result.model_dump())
    if not lab_result:
        raise_exception(400, "failed to add lab_result")
    return lab_result

@router.put("/lab_results-edit/", response_model=LaboratoryResultsOut)
async def format_lab_result(hospital_id: str, lab_result_id: str, data: LaboratoryResultsEdit):
    lab_result = await edit_lab_result(hospital_id, lab_result_id, data.model_dump())
    if not lab_result:
        raise_exception(400, "failed to edit lab_result")
    return lab_result
    
@router.delete("/lab_results-delete/")
async def remove_lab_result(hospital_id: str, lab_result_id: str):
    try:
        await delete_lab_result(hospital_id, lab_result_id)
        return {'message': 'lab_result deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
