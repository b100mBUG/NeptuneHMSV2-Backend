from database.models import Billing, Patient
from config import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, date, time

async def show_total_billings(hospital_id: str):
    async with async_session() as session:
        stmt = select(Billing).where(
            Billing.hospital_id == hospital_id
        ).options(selectinload(Billing.patient))
        result = await session.execute(stmt)
        billings = result.scalars().all()
        return billings or []

async def show_total_patient_billings(hospital_id: str, patient_id: str):
    async with async_session() as session:
        stmt = select(Billing).where(
            (Billing.hospital_id == hospital_id) &
            (Billing.patient_id == patient_id)
        ).options(selectinload(Billing.patient))
        result = await session.execute(stmt)
        billings = result.scalars().all()
        return billings or []

async def show_total_patient_billings_today(hospital_id: str, patient_id: str):
    async with async_session() as session:
        today_start = datetime.combine(date.today(), time.min)
        today_end = datetime.combine(date.today(), time.max)

        stmt = (
            select(Billing)
            .where(
                (Billing.hospital_id == hospital_id) &
                (Billing.patient_id == patient_id) &
                (Billing.created_at >= today_start) &
                (Billing.created_at <= today_end)
            )
            .options(selectinload(Billing.patient))
        )

        result = await session.execute(stmt)
        billings = result.scalars().all()

        return billings or []

async def search_billings(hospital_id: str, search_term: str):
    async with async_session() as session:
        stmt = (
            select(Billing)
            .join(Patient)
            .where(
                (Billing.hospital_id == hospital_id) &
                (Patient.patient_name.ilike(f"%{search_term}%"))
            )
            .options(selectinload(Billing.patient))
        )
        result = await session.execute(stmt)
        billings = result.scalars().all()
        return billings or []
