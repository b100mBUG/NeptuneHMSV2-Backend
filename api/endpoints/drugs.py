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
logo_path = os.path.join(BASE_DIR, ".png")

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
async def export_drug_pdf(hospital_id: str, filter):
    drugs = await fetch_drugs(hospital_id, "all", "desc")
    if filter == "total":
        drugs = drugs
    elif filter == "new":
        today = datetime.today().date()
        thirty_days_ago = today - timedelta(days=30)

        drugs = [
            drug for drug in drugs
            if thirty_days_ago <= drug.date_added.date() <= today
        ]
    elif filter == "expired":
        today = datetime.today().date()
        drugs = [drug for drug in drugs if drug.drug_expiry.date() <= today]
    
    elif filter == "safe":
        today = datetime.today().date()
        drugs = [drug for drug in drugs if drug.drug_expiry.date() > today]

    elif filter == "available":
        drugs = [drug for drug in drugs if drug.drug_quantity > 0]
    
    elif filter == "depleted":
        drugs = [drug for drug in drugs if drug.drug_quantity <= 0]
    
    elif filter == "sellable":
        today = datetime.today().date()
        expired_drugs = [drug for drug in drugs if drug.drug_expiry.date() <= today]

        drugs  = [
            drug 
            for drug in drugs
            if drug.drug_quantity > 0 and 
            drug not in expired_drugs
        ]
    
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    
    filename = f"{hospital.hospital_name}_{filter.lower()}_drugs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        alignment=1,
        fontSize=18,
        textColor=colors.HexColor("#2F4F4F"),
        spaceAfter=12
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=14,
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=10,
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        alignment=1,
        fontSize=10,
        textColor=colors.HexColor("#555555"),
    )

    elements = []

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=90, height=90)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 8))

    hospital_info = f"""
    <b>{hospital.hospital_name}</b><br/>
    {hospital.hospital_email} | {hospital.hospital_contact}<br/>
    Date: {datetime.today().strftime("%B %d, %Y")}
    """

    elements.append(Paragraph(hospital_info, header_style))
    elements.append(Spacer(1, 25))

    report_title = f"{filter.capitalize()} Drugs Report"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 14))


    data = [
        ["Drug", "Category", "Quantity", "Price", "Expiry", "Date Added"]
    ]

    for d in drugs:
        data.append([
            Paragraph(d.drug_name or "", table_cell_style),
            Paragraph(d.drug_category or "", table_cell_style),
            Paragraph(str(d.drug_quantity), table_cell_style),
            Paragraph(f"Ksh. {d.drug_price}", table_cell_style),
            Paragraph(str(d.drug_expiry).split(" ")[0], table_cell_style),
            Paragraph(str(d.date_added).split(" ")[0], table_cell_style)
        ])

    col_widths = [3.5*cm, 3.5*cm, 3*cm, 2.5*cm, 3*cm, 3*cm]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2F8F46")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),

        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])

    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 35))


    signature_section = """
    <br/><br/>
    _____________________________<br/>
    <b>Authorized Signature</b><br/>
    Generated by <b>NeptuneHMS Admin</b>
    """

    elements.append(Paragraph(signature_section, styles["Normal"]))
    elements.append(Spacer(1, 40))


    footer_text = "This report was generated electronically and does not require a physical signature."
    elements.append(Paragraph(footer_text, footer_style))

    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
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
