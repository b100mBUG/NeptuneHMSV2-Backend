from fastapi import FastAPI
from api.endpoints.patients import router as patients_router
from api.endpoints.workers import router as workers_router
from api.endpoints.drugs import router as drugs_router
from api.endpoints.services import router as services_router
from api.endpoints.diagnosis import router as diagnosis_router
from api.endpoints.lab_tests import router as lab_tests_router
from api.endpoints.lab_requests import router as lab_requests_router
from api.endpoints.lab_results import router as lab_results_router
from api.endpoints.appointments import router as appointments_router
from api.endpoints.prescription import router as prescription_router
from api.endpoints.hospitals import router as hospitals_router
from api.endpoints.billing import router as billings_router

app = FastAPI()

app.include_router(hospitals_router, prefix="/hospitals", tags=["hospitals"])
app.include_router(billings_router, prefix="/billings", tags=["billings"])
app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(workers_router, prefix="/workers", tags=["workers"])
app.include_router(drugs_router, prefix="/drugs", tags=["drugs"])
app.include_router(diagnosis_router, prefix="/diagnosis", tags=["diagnosis"])
app.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
app.include_router(prescription_router, prefix="/prescription", tags=["prescription"])
app.include_router(services_router, prefix="/services", tags=["services"])
app.include_router(lab_tests_router, prefix="/lab_tests", tags=["lab_tests"])
app.include_router(lab_results_router, prefix="/lab_results", tags=["lab_results"])
app.include_router(lab_requests_router, prefix="/lab_requests", tags=["lab_requests"])

