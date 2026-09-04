from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.stream import StreamResponse
from app.schemas.content import StreamContentResponse
from app.services.stream_service import StreamService

router = APIRouter(prefix="/api/v1/streams", tags=["Streams"])
stream_service = StreamService()

@router.get("", response_model=list[StreamResponse])
def get_streams(db: Session = Depends(get_db)):
    return stream_service.get_all_streams(db)

@router.get("/{stream_id}/content", response_model=StreamContentResponse)
def get_stream_content(stream_id: str, db: Session = Depends(get_db)):
    return stream_service.get_stream_content(db, stream_id)

@router.get("/{stream_id}/exercises")
def get_stream_exercises(stream_id: str, db: Session = Depends(get_db)):
    content = stream_service.get_stream_content(db, stream_id)
    return {"items": [e.model_dump() for e in content.exercises]}

@router.get("/{stream_id}/tracks")
def get_stream_tracks(stream_id: str, db: Session = Depends(get_db)):
    content = stream_service.get_stream_content(db, stream_id)
    return {"items": [t.model_dump() for t in content.tracks]}
