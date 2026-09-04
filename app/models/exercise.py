import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stream_id: Mapped[str] = mapped_column(String(50), ForeignKey("streams.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    steps_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    stream = relationship("Stream", back_populates="exercises")

    __table_args__ = (
        CheckConstraint("steps_per_minute >= 0", name="chk_exercise_steps_per_minute_non_negative"),
        CheckConstraint("sort_order >= 0", name="chk_exercise_sort_order_non_negative"),
        CheckConstraint("duration > 0", name="chk_exercise_duration_positive"),
    )
