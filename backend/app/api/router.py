"""API router aggregation."""

from fastapi import APIRouter

from app.api.routes import (
    admin,
    appointments,
    auth,
    chat,
    doctor,
    emergency,
    health,
    medicine,
    symptom,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(chat.router)
api_router.include_router(symptom.router)
api_router.include_router(medicine.router)
api_router.include_router(doctor.router)
api_router.include_router(emergency.router)
api_router.include_router(appointments.router)
api_router.include_router(admin.router)
