import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stream_id: Mapped[str] = mapped_column(String(50), ForeignKey("streams.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=180)
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

    stream = relationship("Stream", back_populates="tracks")

    __table_args__ = (
        CheckConstraint("sort_order >= 0", name="chk_track_sort_order_non_negative"),
        CheckConstraint("duration > 0", name="chk_track_duration_positive"),
    )
