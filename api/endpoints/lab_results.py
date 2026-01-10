from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.laboratory import LaboratoryResultsEdit, LaboratoryResultsIn, LaboratoryResultsOut
from database.actions.lab_result import(
    add_lab_result, fetch_lab_results, 
    search_lab_results, edit_lab_result,
    get_specific_result, delete_lab_result
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

@router.get("/lab_results-export-pdf")
async def export_lab_results_pdf(hospital_id: str, start_date: str, end_date: str):
    res = await fetch_lab_results(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        raise HTTPException(status_code=413, detail="Date range too large")

    required_res = [
        re for re in res
        if start <= re.date_added <= end
    ]

    if not required_res:
        raise_exception(404, "Results not found")

    res = required_res
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    
    filename = f"{hospital.hospital_name}_{start_date}_to_{end_date}_lab_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    report_title = f"{start_date} to {end_date} Lab Results Report"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 14))


    data = [
        ["Patient", "Observations", "Conclusion", "Lab Tech", "Date Added"]
    ]

    for r in res:
        data.append([
            Paragraph(r.patient.patient_name or "", table_cell_style),
            Paragraph(r.observations or "", table_cell_style),
            Paragraph(r.conclusion, table_cell_style),
            Paragraph(r.tech.worker_name, table_cell_style),
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

@router.get("/lab_results-export-csv")
async def export_lab_results_csv(
    hospital_id: str,
    start_date: str,
    end_date: str
):
    res = await fetch_lab_results(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        raise HTTPException(status_code=413, detail="Date range too large")

    required_res = [
        r for r in res
        if start <= r.date_added <= end
    ]

    if not required_res:
        raise_exception(404, "Results not found")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{start_date}_to_{end_date}_lab_results_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Patient",
            "Observations",
            "Conclusion",
            "Lab Technician",
            "Date Added"
        ])

        for r in required_res:
            writer.writerow([
                r.patient.patient_name if r.patient else "",
                r.observations or "",
                r.conclusion or "",
                r.tech.worker_name if r.tech else "",
                r.date_added.strftime("%Y-%m-%d")
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )


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
