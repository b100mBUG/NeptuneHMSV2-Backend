from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from api.schemas.patients import PatientsIn, PatientsOut, PatientsEdit
from database.actions.patients import(
    add_patients, edit_patients, delete_patient,
    get_specific_patient, search_patients, 
    fetch_patients
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

@router.get("/patients-fetch/", response_model=list[PatientsOut])
async def fetch_all_patient_data(hospital_id: str, sort_term: str, sort_dir: str):
    patients = await fetch_patients(hospital_id, sort_term, sort_dir)
    if not patients:
        raise_exception(404, "patients not found")
    return patients

@router.get("/patients-search/", response_model=list[PatientsOut])
async def search_all_patients(hospital_id: str, search_by: str, search_term: str):
    patients = await search_patients(hospital_id, search_by, search_term)
    if not patients:
        raise_exception(404, "patients not found")
    return patients

@router.get("/patients-specific/", response_model=PatientsOut)
async def fetch_specific_patient(hospital_id: str, patient_id: str):
    patient = await get_specific_patient(hospital_id, patient_id)
    if not patient:
        raise_exception(404, "patient not found")
    return patient

@router.get("/patients-export-pdf")
async def export_patient_pdf(hospital_id: str, filter):
    patients = await fetch_patients(hospital_id, "all", "desc")
    if not patients:
        raise_exception(404, "Patients not found")
        return
    if filter == "all":
        patients = patients
    elif filter == "new":
        today = datetime.today().date()
        thirty_days_ago = today - timedelta(days=30)

        patients = [
            pat for pat in patients
            if thirty_days_ago <= pat.date_added.date() <= today
        ]

    elif filter == "adults":
        today = datetime.today().date()
        adult_pats = []

        for pat in patients:
            dob = pat.patient_dob
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age >= 18:
                adult_pats.append(pat)
        
        patients = adult_pats
    
    elif filter == "children":
        today = datetime.today().date()
        child_pats = []
        print(patients)
        for pat in patients:
            dob = pat.patient_dob
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 18:
                child_pats.append(pat)
        
        patients = child_pats
    
    elif filter == "male":
        patients = [pat for pat in patients if pat.patient_gender.lower() == "male"]
    
    elif filter == "female":
        patients = [pat for pat in patients if pat.patient_gender.lower() == "female"]
    
    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    
    filename = f"{hospital.hospital_name}_{filter.lower()}_patients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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

    report_title = f"{filter.capitalize()} Patients Report"
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 14))


    data = [
        ["Patient", "Email", "Phone", "ID No.", "Gender", "D.O.B", "Date Added"]
    ]

    for p in patients:
        data.append([
            Paragraph(p.patient_name or "", table_cell_style),
            Paragraph(p.patient_email or "", table_cell_style),
            Paragraph(p.patient_phone or "", table_cell_style),
            Paragraph(p.patient_id_number or "", table_cell_style),
            Paragraph(p.patient_gender or "", table_cell_style),
            Paragraph(str(p.patient_dob).split(" ")[0], table_cell_style),
            Paragraph(str(p.date_added).split(" ")[0], table_cell_style)
        ])

    col_widths = [
        3.0*cm, 4.0*cm,3.0*cm,
        2.2*cm, 1.8*cm, 2.2*cm, 
        2.3*cm  
    ]

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


@router.post("/patients-add/", response_model=PatientsOut)
async def add_patient(hospital_id: str, patient: PatientsIn):
    patient = await add_patients(hospital_id, patient.model_dump())
    if not patient:
        raise_exception(400, "failed to add patient")
    return patient

@router.put("/patients-edit/", response_model=PatientsOut)
async def format_patient(hospital_id: str, patient_id: str, pat_data: PatientsEdit):
    patient = await edit_patients(hospital_id, patient_id, pat_data.model_dump())
    if not patient:
        raise_exception(400, "failed to edit patient")
    return patient
    
@router.delete("/patients-delete/")
async def remove_patient(hospital_id: str, patient_id: str):
    try:
        await delete_patient(hospital_id, patient_id)
        return {'message': 'patient deleted successfully'}
    except Exception as e:
        raise HTTPException(500, f"An error occurred: {e}")
