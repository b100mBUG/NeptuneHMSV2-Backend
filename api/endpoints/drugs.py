from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.drugs import DrugsEdit, DrugsIn, DrugsOut
from database.actions.drugs import(
    add_drugs, edit_drug, search_drugs, 
    fetch_drugs, delete_drug, get_specific_drug,
    sale_drug
)
from database.actions.hospital import get_specific_hospital

from fastapi.responses import FileResponse
from datetime import datetime, timedelta
import csv
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, Image,
)
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

router = APIRouter()

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
logo_path = os.path.join(BASE_DIR, "logo.png")

router = APIRouter()

def raise_exception(status_code, detail):
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/drugs-fetch/", response_model=list[DrugsOut])
async def fetch_all_drug_data(hospital_id: str, sort_term: str, sort_dir: str):
    drugs = await fetch_drugs(hospital_id, sort_term, sort_dir)
    if not drugs:
        raise_exception(404, "drugs not found")
    return drugs

@router.get("/drugs-search/", response_model=list[DrugsOut])
async def search_all_drugs(hospital_id: str, search_term: str):
    drugs = await search_drugs(hospital_id, search_term)
    if not drugs:
        raise_exception(404, "drugs not found")
    return drugs

@router.get("/drugs-specific/", response_model=DrugsOut)
async def fetch_specific_drug(hospital_id: str, drug_id: str):
    drug = await get_specific_drug(hospital_id, drug_id)
    if not drug:
        raise_exception(404, "drug not found")
    return drug

@router.get("/drugs-export-pdf")
async def export_drug_pdf(
    hospital_id: str,
    filter: str
):
    drugs = await fetch_drugs(hospital_id, "all", "desc")
    if not drugs:
        raise_exception(404, "Drugs not found")

    today = datetime.today().date()

    if filter == "total":
        pass

    elif filter == "new":
        thirty_days_ago = today - timedelta(days=30)
        drugs = [
            d for d in drugs
            if thirty_days_ago <= d.date_added.date() <= today
        ]

    elif filter == "expired":
        drugs = [
            d for d in drugs
            if d.drug_expiry and d.drug_expiry.date() <= today
        ]

    elif filter == "safe":
        drugs = [
            d for d in drugs
            if d.drug_expiry and d.drug_expiry.date() > today
        ]

    elif filter == "available":
        drugs = [d for d in drugs if d.drug_quantity > 0]

    elif filter == "depleted":
        drugs = [d for d in drugs if d.drug_quantity <= 0]

    elif filter == "sellable":
        drugs = [
            d for d in drugs
            if d.drug_quantity > 0
            and d.drug_expiry
            and d.drug_expiry.date() > today
        ]

    else:
        raise HTTPException(status_code=400, detail="Invalid filter")

    if not drugs:
        raise_exception(404, "No drugs matched the filter")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{filter.lower()}_drugs_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=50,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        f"<b>{hospital.hospital_name}</b><br/>"
        f"{hospital.hospital_email} | {hospital.hospital_contact}<br/>"
        f"Date: {today.strftime('%B %d, %Y')}",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 20))

    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=90, height=90))
        elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        f"{filter.capitalize()} Drugs Report",
        styles["Title"]
    ))

    data = [[
        "Drug", "Category", "Quantity",
        "Price", "Expiry", "Date Added"
    ]]

    for d in drugs:
        data.append([
            d.drug_name or "",
            d.drug_category or "",
            str(d.drug_quantity),
            f"Ksh. {d.drug_price}",
            d.drug_expiry.strftime("%Y-%m-%d") if d.drug_expiry else "",
            d.date_added.strftime("%Y-%m-%d")
        ])

    table = Table(
        data,
        colWidths=[3.5*cm, 3.5*cm, 3*cm, 2.5*cm, 3*cm, 3*cm],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2F8F46")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    elements.append(Spacer(1, 15))
    elements.append(table)

    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )

@router.get("/drugs-export-csv")
async def export_drug_csv(
    hospital_id: str,
    filter: str
):
    drugs = await fetch_drugs(hospital_id, "all", "desc")
    if not drugs:
        raise_exception(404, "Drugs not found")

    today = datetime.today().date()

    if filter == "total":
        pass

    elif filter == "new":
        thirty_days_ago = today - timedelta(days=30)
        drugs = [
            d for d in drugs
            if thirty_days_ago <= d.date_added.date() <= today
        ]

    elif filter == "expired":
        drugs = [
            d for d in drugs
            if d.drug_expiry and d.drug_expiry.date() <= today
        ]

    elif filter == "safe":
        drugs = [
            d for d in drugs
            if d.drug_expiry and d.drug_expiry.date() > today
        ]

    elif filter == "available":
        drugs = [d for d in drugs if d.drug_quantity > 0]

    elif filter == "depleted":
        drugs = [d for d in drugs if d.drug_quantity <= 0]

    elif filter == "sellable":
        drugs = [
            d for d in drugs
            if d.drug_quantity > 0
            and d.drug_expiry
            and d.drug_expiry.date() > today
        ]

    else:
        raise HTTPException(status_code=400, detail="Invalid filter")

    if not drugs:
        raise_exception(404, "No drugs matched the filter")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{filter.lower()}_drugs_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Drug",
            "Category",
            "Quantity",
            "Price (Ksh)",
            "Expiry Date",
            "Date Added"
        ])

        for d in drugs:
            writer.writerow([
                d.drug_name or "",
                d.drug_category or "",
                d.drug_quantity,
                d.drug_price,
                d.drug_expiry.strftime("%Y-%m-%d") if d.drug_expiry else "",
                d.date_added.strftime("%Y-%m-%d")
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )


@router.post("/drugs-add/", response_model=DrugsOut)
async def add_drug(hospital_id: str, drug: DrugsIn):
    drug = await add_drugs(hospital_id, drug.model_dump())
    if not drug:
        raise_exception(400, "failed to add drug")
    return drug

@router.put("/drugs-edit/", response_model=DrugsOut)
async def format_drug(hospital_id: str, drug_id: str, data: DrugsEdit):
    drug = await edit_drug(hospital_id, drug_id, data.model_dump())
    if not drug:
        raise_exception(400, "failed to edit drug")
    return drug

@router.put("/drugs/drug-sale")
async def sale_drugs(hospital_id: str, drug_id: str, drug_qty: int):
    try:
        drug = await sale_drug(hospital_id, drug_id, drug_qty)
        if not drug:
            raise_exception(400, "Failed to sale drug")
    except Exception as e:
        raise_exception(500, f"An error occurred: {e}")

@router.delete("/drugs-delete/")
async def remove_drug(hospital_id: str, drug_id: str):
    try:
        await delete_drug(hospital_id, drug_id)
        return {'message': 'drug deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
