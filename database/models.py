from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from database.connection import Base


class NotificationType(enum.Enum):
    TEAM_APPLICATION = "team_application"
    APPLICATION_CANCEL = "application_cancel"
    CHAMPIONSHIP_CANCEL = "championship_cancel"
    NEW_MATCH = "new_match"
    MATCH_RESCHEDULE = "match_reschedule"
    PLAYOFF_RESULT = "playoff_result"
    MATCH_REMINDER = "match_reminder"
    NEW_CHAMPIONSHIP = "new_championship"
    COMMITTEE_MESSAGE = "committee_message"
    TEAM_INVITATION = "team_invitation"
    COMMITTEE_INVITATION = "committee_invitation"


class User(Base):
    """Модель пользователя системы"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    telegram_id = Column(String(20), unique=True, nullable=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    notifications = relationship("Notification", back_populates="user")

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"


class Notification(Base):
    """Модель уведомления"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    scheduled_for = Column(DateTime, nullable=True)
    metadata_json = Column(Text, nullable=True)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"