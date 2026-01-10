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
logo_path = os.path.join(BASE_DIR, "logo.png")

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
async def export_patient_pdf(
    hospital_id: str,
    filter: str
):
    patients = await fetch_patients(hospital_id, "all", "desc")
    if not patients:
        raise_exception(404, "Patients not found")

    today = datetime.today().date()

    def calculate_age(dob):
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if filter == "all":
        pass

    elif filter == "new":
        thirty_days_ago = today - timedelta(days=30)
        patients = [
            p for p in patients
            if thirty_days_ago <= p.date_added.date() <= today
        ]

    elif filter == "adults":
        patients = [
            p for p in patients
            if calculate_age(p.patient_dob) >= 18
        ]

    elif filter == "children":
        patients = [
            p for p in patients
            if calculate_age(p.patient_dob) < 18
        ]

    elif filter == "male":
        patients = [
            p for p in patients
            if p.patient_gender and p.patient_gender.lower() == "male"
        ]

    elif filter == "female":
        patients = [
            p for p in patients
            if p.patient_gender and p.patient_gender.lower() == "female"
        ]

    else:
        raise HTTPException(status_code=400, detail="Invalid filter")

    if not patients:
        raise_exception(404, "No patients matched the filter")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{filter.lower()}_patients_"
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

    elements.append(Spacer(1, 12))

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=90, height=90)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 20))
    else:
        print("Failed to load:", logo_path)

    elements.append(Paragraph(
        f"{filter.capitalize()} Patients Report",
        styles["Title"]
    ))

    elements.append(Spacer(1, 15))

    data = [[
        "Patient", "Email", "Phone",
        "ID No.", "Gender", "D.O.B", "Date Added"
    ]]

    for p in patients:
        data.append([
            p.patient_name or "",
            p.patient_email or "",
            p.patient_phone or "",
            p.patient_id_number or "",
            p.patient_gender or "",
            p.patient_dob.strftime("%Y-%m-%d"),
            p.date_added.strftime("%Y-%m-%d")
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2F8F46")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elements.append(table)

    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/patients-export-csv")
async def export_patient_csv(
    hospital_id: str,
    filter: str
):
    patients = await fetch_patients(hospital_id, "all", "desc")
    if not patients:
        raise_exception(404, "Patients not found")

    today = datetime.today().date()

    def calculate_age(dob):
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if filter == "new":
        thirty_days_ago = today - timedelta(days=30)
        patients = [
            p for p in patients
            if thirty_days_ago <= p.date_added.date() <= today
        ]

    elif filter == "adults":
        patients = [p for p in patients if calculate_age(p.patient_dob) >= 18]

    elif filter == "children":
        patients = [p for p in patients if calculate_age(p.patient_dob) < 18]

    elif filter == "male":
        patients = [p for p in patients if p.patient_gender and p.patient_gender.lower() == "male"]

    elif filter == "female":
        patients = [p for p in patients if p.patient_gender and p.patient_gender.lower() == "female"]

    elif filter != "all":
        raise HTTPException(status_code=400, detail="Invalid filter")

    if not patients:
        raise_exception(404, "No patients matched the filter")

    hospital = await get_specific_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")

    filename = (
        f"{hospital.hospital_name}_"
        f"{filter.lower()}_patients_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Patient", "Email", "Phone",
            "ID No.", "Gender", "D.O.B", "Date Added"
        ])

        for p in patients:
            writer.writerow([
                p.patient_name or "",
                p.patient_email or "",
                p.patient_phone or "",
                p.patient_id_number or "",
                p.patient_gender or "",
                p.patient_dob.strftime("%Y-%m-%d"),
                p.date_added.strftime("%Y-%m-%d")
            ])

    return FileResponse(
        path,
        media_type="text/csv",
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
