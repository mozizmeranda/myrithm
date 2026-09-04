import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stream_id: Mapped[str] = mapped_column(String(50), ForeignKey("streams.id", ondelete="RESTRICT"), nullable=False, index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    user = relationship("User")
    stream = relationship("Stream", back_populates="activity_logs")

    __table_args__ = (
        CheckConstraint("duration_seconds > 0 AND duration_seconds <= 60", name="chk_activity_duration_valid"),
        CheckConstraint("estimated_steps >= 0", name="chk_activity_estimated_steps_non_negative"),
    )
