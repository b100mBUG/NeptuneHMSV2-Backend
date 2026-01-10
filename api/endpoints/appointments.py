from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.appointments import AppointmentsEdit, AppointmentsIn, AppointmentsOut
from database.actions.appointment import(
    add_appointment, fetch_appointments, 
    search_appointments, edit_appointment,
    delete_appointment, get_specific_appointment
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

@router.get("/appointments-fetch/", response_model=list[AppointmentsOut])
async def fetch_all_appointment_data(hospital_id: str, sort_term: str, sort_dir: str):
    appointments = await fetch_appointments(hospital_id, sort_term, sort_dir)
    if not appointments:
        raise_exception(404, "appointments not found")
    return appointments

@router.get("/appointments-search/", response_model=list[AppointmentsOut])
async def search_all_appointments(hospital_id: str, search_term: str):
    appointments = await search_appointments(hospital_id, search_term)
    if not appointments:
        raise_exception(404, "appointments not found")
    return appointments

@router.get("/appointments-export-pdf")
async def export_appointments_pdf(hospital_id: str, start_date: str, end_date: str):
    apps = await fetch_appointments(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if end - start > timedelta(days=90):
        return

    required_apps = [
        app for app in apps
        if start <= app.date_added <= end
    ]

    if not required_apps:
        raise_exception(404, "Appointments not found")

    apps = required_apps
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    
    filename = f"{hospital.hospital_name}_{start_date}_to_{end_date}_appointments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    report_title = f"{start_date} to {end_date} Appointments Report"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 14))


    data = [
        ["Patient", "About", "Start On", "Time", "Date Added"]
    ]

    for a in apps:
        data.append([
            Paragraph(a.patient.patient_name or "", table_cell_style),
            Paragraph(a.appointment_desc or "", table_cell_style),
            Paragraph(str(a.date_requested), table_cell_style),
            Paragraph(str(a.time_requested), table_cell_style),
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

@router.get("/appointments-export-csv")
async def export_appointments_csv(
    hospital_id: str,
    start_date: str,
    end_date: str
):
    apps = await fetch_appointments(hospital_id, "all", "desc")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # DoS / abuse guard
    if end - start > timedelta(days=90):
        raise HTTPException(status_code=413, detail="Date range too large")

    required_apps = [
        app for app in apps
        if start <= app.date_added <= end
    ]

    if not required_apps:
        raise_exception(404, "Appointments not found")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{start_date}_to_{end_date}_appointments_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Patient",
            "About",
            "Start On",
            "Time",
            "Date Added"
        ])

        for a in required_apps:
            writer.writerow([
                a.patient.patient_name if a.patient else "",
                a.appointment_desc or "",
                str(a.date_requested),
                str(a.time_requested),
                a.date_added.strftime("%Y-%m-%d")
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )

@router.get("/appointments-specific/", response_model=AppointmentsOut)
async def fetch_specific_appointment(hospital_id: str, appointment_id: str):
    appointment = await get_specific_appointment(hospital_id, appointment_id)
    if not appointment:
        raise_exception(404, "appointment not found")
    return appointment

@router.post("/appointments-add/", response_model=AppointmentsOut)
async def add_appointments(hospital_id: str, appointment: AppointmentsIn):
    appointment = await add_appointment(hospital_id, appointment.model_dump())
    if not appointment:
        raise_exception(400, "failed to add appointment")
    return appointment

@router.put("/appointments-edit/", response_model=AppointmentsOut)
async def format_appointment(hospital_id: str, appointment_id: str, data: AppointmentsEdit):
    appointment = await edit_appointment(hospital_id, appointment_id, data.model_dump())
    if not appointment:
        raise_exception(400, "failed to edit appointment")
    return appointment
    
@router.delete("/appointments-delete/")
async def remove_appointment(hospital_id: str, appointment_id: str):
    try:
        await delete_appointment(hospital_id, appointment_id)
        return {'message': 'appointment deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
