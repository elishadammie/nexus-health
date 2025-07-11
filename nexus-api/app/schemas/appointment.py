import datetime
from pydantic import BaseModel, Field

class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment."""
    doctor_id: str
    start_time: datetime.datetime
    reason_for_visit: str

class AppointmentDetails(BaseModel):
    """Schema for returning appointment details."""
    id: str
    user_id: str
    doctor_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    reason_for_visit: str
    status: str

    class Config:
        # OLD: orm_mode = True
        # NEW:
        from_attributes = True