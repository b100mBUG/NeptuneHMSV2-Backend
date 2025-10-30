from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.drugs import DrugsEdit, DrugsIn, DrugsOut
from database.actions.drugs import(
    add_drugs, edit_drug, search_drugs, 
    fetch_drugs, delete_drug, get_specific_drug,
    sale_drug
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/drugs-fetch/", response_model=list[DrugsOut])
async def fetch_all_drug_data(hospital_id: int, sort_term: str, sort_dir: str):
    drugs = await fetch_drugs(hospital_id, sort_term, sort_dir)
    if not drugs:
        raise_exception(404, "drugs not found")
    return drugs

@router.get("/drugs-search/", response_model=list[DrugsOut])
async def search_all_drugs(hospital_id: int, search_term: str):
    drugs = await search_drugs(hospital_id, search_term)
    if not drugs:
        raise_exception(404, "drugs not found")
    return drugs

@router.get("/drugs-specific/", response_model=DrugsOut)
async def fetch_specific_drug(hospital_id: int, drug_id: int):
    drug = await get_specific_drug(hospital_id, drug_id)
    if not drug:
        raise_exception(404, "drug not found")
    return drug

@router.post("/drugs-add/", response_model=DrugsOut)
async def add_drug(hospital_id: int, drug: DrugsIn):
    drug = await add_drugs(hospital_id, drug.model_dump())
    if not drug:
        raise_exception(400, "failed to add drug")
    return drug

@router.put("/drugs-edit/", response_model=DrugsOut)
async def format_drug(hospital_id: int, drug_id: int, data: DrugsEdit):
    drug = await edit_drug(hospital_id, drug_id, data.model_dump())
    if not drug:
        raise_exception(400, "failed to edit drug")
    return drug

@router.put("/drugs/drug-sale")
async def sale_drugs(hospital_id: int, drug_id: int, drug_qty: int):
    try:
        drug = await sale_drug(hospital_id, drug_id, drug_qty)
        if not drug:
            raise_exception(400, "Failed to sale drug")
    except Exception as e:
        raise_exception(500, f"An error occurred: {e}")

@router.delete("/drugs-delete/")
async def remove_drug(hospital_id: int, drug_id: int):
    try:
        await delete_drug(hospital_id, drug_id)
        return {'message': 'drug deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
