from fastapi import APIRouter, HTTPException
from collections import defaultdict
from typing import List

from api.schemas.prescriptions import PrescriptionsIn, PrescriptionGroupedOut
from database.actions.prescription import (
    add_prescription,
    fetch_prescriptions,
    search_prescriptions,
    get_specific_prescription,
    delete_prescription
)

router = APIRouter()


def raise_exception(status_code: str, detail: str):
    raise HTTPException(status_code=status_code, detail=detail)


def agglomerate_prescriptions(prescriptions):
    grouped = defaultdict(list)
    for presc in prescriptions:
        grouped[presc.patient.patient_name].append(presc)

    output = []
    for patient_name, presc_group in grouped.items():
        entries = []
        for presc in presc_group:
            presc_id = presc.prescription_id
            for item in presc.items:
                entries.append({
                    "drug_name": item.drug.drug_name,
                    "quantity": item.drug_qty,
                    "notes": item.notes
                })

        output.append({
            "prescription_id": presc_id,
            "patient_name": patient_name,
            "entries": entries,
            "dates": sorted({str(p.date_added).split(" ")[0] for p in presc_group}),
        })

    return output


@router.get("/prescriptions-fetch/", response_model=List[PrescriptionGroupedOut])
async def fetch_all_prescription_data(
    hospital_id: str,
    sort_term: str = "all",
    sort_dir: str = "desc"
):
    prescriptions = await fetch_prescriptions(hospital_id, sort_term, sort_dir)
    if not prescriptions:
        raise_exception(404, "prescriptions not found")
    return agglomerate_prescriptions(prescriptions)


@router.get("/prescriptions-search/", response_model=List[PrescriptionGroupedOut])
async def search_all_prescriptions(hospital_id: str, search_term: str):
    prescriptions = await search_prescriptions(hospital_id, search_term)
    if not prescriptions:
        raise_exception(404, "prescriptions not found")
    return agglomerate_prescriptions(prescriptions)


@router.get("/prescriptions-specific/", response_model=List[PrescriptionGroupedOut])
async def fetch_specific_prescription(hospital_id: str, prescription_id: str):
    prescription = await get_specific_prescription(hospital_id, prescription_id)
    if not prescription:
        raise_exception(404, "prescription not found")
    return agglomerate_prescriptions([prescription]) 


@router.post("/prescriptions-add/", response_model=List[PrescriptionGroupedOut])
async def add_prescriptions(hospital_id: str, prescription: PrescriptionsIn):
    new_prescription = await add_prescription(hospital_id, prescription.model_dump())
    if not new_prescription:
        raise_exception(400, "failed to add prescription")
    return agglomerate_prescriptions([new_prescription])  


@router.delete("/prescriptions-delete/")
async def remove_prescription(hospital_id: str, prescription_id: str):
    try:
        await delete_prescription(hospital_id, prescription_id)
        return {'message': 'prescription deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
