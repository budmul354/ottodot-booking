from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TrialClassRead(BaseModel):
    id: int
    title: str
    starts_at: datetime
    capacity: int
    confirmed_count: int
    available_seats: int


class BookingCreate(BaseModel):
    student_id: int
    trial_class_id: int


class BookingCreated(BaseModel):
    booking_id: int
    status: str


class PaymentCreate(BaseModel):
    result: str


class PaymentResult(BaseModel):
    payment_status: str
    booking_status: str


class BookingRead(BaseModel):
    id: int
    student_id: int
    trial_class_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class RosterStudent(BaseModel):
    student_id: int
    name: str


class RosterRead(BaseModel):
    class_id: int
    students: list[RosterStudent]
