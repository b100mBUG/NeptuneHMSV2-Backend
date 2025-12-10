from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.laboratory import LaboratoryTestsEdit, LaboratoryTestsIn, LaboratoryTestsOut
from database.actions.lab_tests import(
    add_lab_tests, fetch_lab_tests, edit_lab_test,
    get_specific_test, delete_lab_test, search_lab_tests
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/lab_tests-fetch/", response_model=list[LaboratoryTestsOut])
async def fetch_all_lab_test_data(hospital_id: str, sort_term: str, sort_dir: str):
    lab_tests = await fetch_lab_tests(hospital_id, sort_term, sort_dir)
    if not lab_tests:
        raise_exception(404, "lab_tests not found")
    return lab_tests

@router.get("/lab_tests-search/", response_model=list[LaboratoryTestsOut])
async def search_all_lab_tests(hospital_id: str, search_term: str):
    lab_tests = await search_lab_tests(hospital_id, search_term)
    if not lab_tests:
        raise_exception(404, "lab_tests not found")
    return lab_tests

@router.get("/lab_tests-specific/", response_model=LaboratoryTestsOut)
async def fetch_specific_lab_test(hospital_id: str, lab_test_id: str):
    lab_test = await get_specific_test(hospital_id, lab_test_id)
    if not lab_test:
        raise_exception(404, "lab_test not found")
    return lab_test

@router.post("/lab_tests-add/", response_model=LaboratoryTestsOut)
async def add_lab_test(hospital_id: str, lab_test: LaboratoryTestsIn):
    lab_test = await add_lab_tests(hospital_id, lab_test.model_dump())
    if not lab_test:
        raise_exception(400, "failed to add lab_test")
    return lab_test

@router.put("/lab_tests-edit/", response_model=LaboratoryTestsOut)
async def format_lab_test(hospital_id: str, lab_test_id: str, data: LaboratoryTestsEdit):
    lab_test = await edit_lab_test(hospital_id, lab_test_id, data.model_dump())
    if not lab_test:
        raise_exception(400, "failed to edit lab_test")
    return lab_test
    
@router.delete("/lab_tests-delete/")
async def remove_lab_test(hospital_id: str, lab_test_id: str):
    try:
        await delete_lab_test(hospital_id, lab_test_id)
        return {'message': 'lab_test deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
