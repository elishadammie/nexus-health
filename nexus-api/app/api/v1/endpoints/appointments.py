import datetime
import uuid
from fastapi import APIRouter
from app.schemas.appointment import AppointmentCreate, AppointmentDetails

router = APIRouter()

@router.post("/", response_model=AppointmentDetails, status_code=201)
def create_appointment(appointment: AppointmentCreate):
    """
    Creates a new appointment.
    (This is a placeholder and does not save to the database yet)
    """
    # For now, return a hardcoded response for testing purposes
    return AppointmentDetails(
        id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()), # Placeholder
        doctor_id=appointment.doctor_id,
        start_time=appointment.start_time,
        end_time=appointment.start_time + datetime.timedelta(minutes=30),
        reason_for_visit=appointment.reason_for_visit,
        status="Scheduled"
    )