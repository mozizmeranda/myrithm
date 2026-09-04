from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.schemas.stream import StreamResponse, StreamCreateRequest, StreamUpdateRequest
from app.services.stream_service import StreamService

router = APIRouter(prefix="/api/v1/admin/streams", tags=["Admin Streams"], dependencies=[Depends(require_admin)])
stream_service = StreamService()

@router.get("", response_model=list[StreamResponse])
def get_streams(db: Session = Depends(get_db)):
    return stream_service.get_all_streams(db)

@router.post("", response_model=StreamResponse, status_code=status.HTTP_201_CREATED)
def create_stream(req: StreamCreateRequest, db: Session = Depends(get_db)):
    return stream_service.create_stream(db, req)

@router.patch("/{stream_id}", response_model=StreamResponse)
def update_stream(stream_id: str, req: StreamUpdateRequest, db: Session = Depends(get_db)):
    return stream_service.update_stream(db, stream_id, req)

@router.delete("/{stream_id}")
def delete_stream(stream_id: str, db: Session = Depends(get_db)):
    return stream_service.delete_stream(db, stream_id)
