from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.laboratory import LaboratoryRequestsOut, LaboratoryRequestsIn
from database.actions.lab_request import(
    add_lab_request, fetch_lab_requests, search_lab_request,
    delete_lab_request, get_specific_lab_request
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

@router.get("/lab_requests-export-pdf")
async def export_lab_request_pdf(hospital_id: str, start_date: str, end_date: str):
    reqs = await fetch_lab_requests(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        return

    required_reqs = [
        req for req in reqs
        if start <= req.date_added <= end
    ]

    if not required_reqs:
        raise_exception(404, "Requests not found")

    reqs = required_reqs
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    
    filename = f"{hospital.hospital_name}_{start_date}_to_{end_date}_lab_requests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    report_title = f"{start_date} to {end_date} Lab Requests Report"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 14))


    data = [
        ["Patient", "Test", "Requested By", "Price", "Date Added"]
    ]

    for r in reqs:
        data.append([
            Paragraph(r.patient.patient_name or "", table_cell_style),
            Paragraph(r.test.test_name or "", table_cell_style),
            Paragraph(r.doctor.worker_name, table_cell_style),
            Paragraph(str(r.test.test_price), table_cell_style),
            Paragraph(str(r.date_added).split(" ")[0], table_cell_style)
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

@router.get("/lab_requests-export-csv")
async def export_lab_requests_csv(
    hospital_id: str,
    start_date: str,
    end_date: str
):
    reqs = await fetch_lab_requests(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        raise HTTPException(status_code=413, detail="Date range too large")

    required_reqs = [
        req for req in reqs
        if start <= req.date_added <= end
    ]

    if not required_reqs:
        raise_exception(404, "Requests not found")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{start_date}_to_{end_date}_lab_requests_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Patient",
            "Test",
            "Requested By",
            "Price",
            "Date Added"
        ])

        for r in required_reqs:
            writer.writerow([
                r.patient.patient_name if r.patient else "",
                r.test.test_name if r.test else "",
                r.doctor.worker_name if r.doctor else "",
                r.test.test_price if r.test else "",
                r.date_added.strftime("%Y-%m-%d")
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )

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
