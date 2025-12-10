from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.workers import (
    WorkersEdit, WorkersIn, WorkersOut,
    Signin, PasswordChange
)
from database.actions.workers import(
    add_worker, fetch_workers, search_workers,
    edit_workers, signin, change_password,
    delete_worker, get_specific_worker
)

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/workers-fetch/", response_model=list[WorkersOut])
async def fetch_all_worker_data(hospital_id: str, sort_term: str, sort_dir: str):
    workers = await fetch_workers(hospital_id, sort_term, sort_dir)
    if not workers:
        raise_exception(404, "workers not found")
    return workers

@router.get("/workers-search/", response_model=list[WorkersOut])
async def search_all_workers(hospital_id: str, search_by: str, search_term: str):
    workers = await search_workers(hospital_id, search_by, search_term)
    if not workers:
        raise_exception(404, "workers not found")
    return workers

@router.get("/workers-specific/", response_model=WorkersOut)
async def fetch_specific_worker(hospital_id: str, worker_id: str):
    worker = await get_specific_worker(hospital_id, worker_id)
    if not worker:
        raise_exception(404, "worker not found")
    return worker

@router.post("/workers-add/", response_model=WorkersOut)
async def add_workers(hospital_id: str, worker: WorkersIn):
    worker = await add_worker(hospital_id, worker.model_dump())
    if not worker:
        raise_exception(400, "failed to add worker")
    return worker

@router.post("/workers-signin/", response_model=WorkersOut)
async def worker_login(hospital_id: str, worker_detail: Signin):
    worker = await signin(hospital_id, worker_detail.model_dump())
    if not worker:
        raise_exception(404, "worker not found")
    return worker

@router.put("/workers-edit/", response_model=WorkersOut)
async def format_worker(hospital_id: str, worker_id: str, data: WorkersEdit):
    worker = await edit_workers(hospital_id, worker_id, data.model_dump())
    if not worker:
        raise_exception(400, "failed to edit worker")
    return worker

@router.put("/workers-change-password/", response_model=WorkersOut)
async def change_worker_password(hospital_id: str, worker_id: str, password_detail: PasswordChange):
    worker = await change_password(hospital_id, worker_id, password_detail.model_dump())
    if not worker:
        raise_exception(400, "failed to change password")
    return worker
    
@router.delete("/workers-delete/")
async def remove_worker(hospital_id: str, worker_id: str):
    try:
        await delete_worker(hospital_id, worker_id)
        return {'message': 'worker deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
