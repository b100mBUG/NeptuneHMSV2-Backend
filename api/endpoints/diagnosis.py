from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.diagnoses import DiagnosesEdit, DiagnosesIn, DiagnosesOut
from database.actions.diagnosis import(
    add_diagnosis, fetch_diagnosis, edit_diagnosis,
    search_diagnosis, delete_diagnosis, get_specific_diagnosis
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

@router.get("/diagnosis-fetch/", response_model=list[DiagnosesOut])
async def fetch_all_diagnosis_data(hospital_id: str, sort_term: str, sort_dir: str):
    diagnosiss = await fetch_diagnosis(hospital_id, sort_term, sort_dir)
    if not diagnosiss:
        raise_exception(404, "diagnosiss not found")
    return diagnosiss

@router.get("/diagnosis-search/", response_model=list[DiagnosesOut])
async def search_all_diagnosiss(hospital_id: str, search_term: str):
    diagnosiss = await search_diagnosis(hospital_id, search_term)
    if not diagnosiss:
        raise_exception(404, "diagnosiss not found")
    return diagnosiss

@router.get("/diagnosis-export-pdf")
async def export_diagnosis_pdf(hospital_id: str, start_date: str, end_date: str):
    diags = await fetch_diagnosis(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        return

    required_diags = [
        diag for diag in diags
        if start <= diag.date_added <= end
    ]

    if not required_diags:
        raise_exception(404, "Diagnosis not found")

    diags = required_diags
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    
    filename = f"{hospital.hospital_name}_{start_date}_to_{end_date}_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    hospital_info = f"""
    <b>{hospital.hospital_name}</b><br/>
    {hospital.hospital_email} | {hospital.hospital_contact}<br/>
    Date: {datetime.today().strftime("%B %d, %Y")}
    """

    elements.append(Paragraph(hospital_info, header_style))
    elements.append(Spacer(1, 25))

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=90, height=90)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 8))

    report_title = f"{start_date} to {end_date} Diagnoses Report"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 14))


    data = [
        ["Patient", "Symptoms", "Findings", "Suggested Diag", "Date Added"]
    ]

    for d in diags:
        data.append([
            Paragraph(d.patient.patient_name or "", table_cell_style),
            Paragraph(d.symptoms or "", table_cell_style),
            Paragraph(d.findings, table_cell_style),
            Paragraph(d.suggested_diagnosis, table_cell_style),
            Paragraph(str(d.date_added).split(" ")[0], table_cell_style)
        ])

    col_widths = [3.5*cm, 3.5*cm, 3*cm, 3*cm, 3*cm]

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

@router.get("/diagnosis-export-csv")
async def export_diagnosis_csv(
    hospital_id: str,
    start_date: str,
    end_date: str
):
    diags = await fetch_diagnosis(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        raise HTTPException(status_code=413, detail="Date range too large")

    required_diags = [
        d for d in diags
        if start <= d.date_added <= end
    ]

    if not required_diags:
        raise_exception(404, "Diagnosis not found")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{start_date}_to_{end_date}_diagnosis_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Patient",
            "Symptoms",
            "Findings",
            "Suggested Diagnosis",
            "Date Added"
        ])

        for d in required_diags:
            writer.writerow([
                d.patient.patient_name if d.patient else "",
                d.symptoms or "",
                d.findings or "",
                d.suggested_diagnosis or "",
                d.date_added.strftime("%Y-%m-%d")
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )

@router.get("/diagnosis-specific/", response_model=DiagnosesOut)
async def fetch_specific_diagnosis(hospital_id: str, diagnosis_id: str):
    diagnosis = await get_specific_diagnosis(hospital_id, diagnosis_id)
    if not diagnosis:
        raise_exception(404, "diagnosis not found")
    return diagnosis

@router.post("/diagnosis-add/", response_model=DiagnosesOut)
async def add_diagnoses(hospital_id: str, diagnoses: DiagnosesIn):
    diagnosis = await add_diagnosis(hospital_id, diagnoses.model_dump())
    if not diagnosis:
        raise_exception(400, "failed to add diagnosis")
    return diagnosis

@router.put("/diagnosis-edit/", response_model=DiagnosesOut)
async def format_diagnosis(hospital_id: str, diagnosis_id: str, data: DiagnosesEdit):
    print("Diagnosis model: ", data.model_dump())
    diagnosis = await edit_diagnosis(hospital_id, diagnosis_id, data.model_dump())
    if not diagnosis:
        raise_exception(400, "failed to edit diagnosis")
    return diagnosis
    
@router.delete("/diagnosis-delete/")
async def remove_diagnosis(hospital_id: str, diagnosis_id: str):
    try:
        await delete_diagnosis(hospital_id, diagnosis_id)
        return {'message': 'diagnosis deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
