"""ORM model registry. Importing this package registers every model on Base."""

from app.models.user import MedicalHistory, User
from app.models.chat import Chat, Message
from app.models.appointment import Appointment
from app.models.medicine import Medicine, SavedMedicine
from app.models.saved_search import SavedSearch
from app.models.session import Session
from app.models.system_log import SystemLog
from app.models.model_usage import ModelUsage
from app.models.prompt_history import PromptHistory

__all__ = [
    "User",
    "MedicalHistory",
    "Chat",
    "Message",
    "Appointment",
    "Medicine",
    "SavedMedicine",
    "SavedSearch",
    "Session",
    "SystemLog",
    "ModelUsage",
    "PromptHistory",
]
