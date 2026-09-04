from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.schemas.track import TrackResponse, TrackCreateRequest, TrackUpdateRequest
from app.services.admin_service import AdminService
from app.services.media_service import MediaService

router = APIRouter(prefix="/api/v1/admin/tracks", tags=["Admin Tracks"], dependencies=[Depends(require_admin)])
admin_service = AdminService()

@router.get("", response_model=list[TrackResponse])
def get_tracks(stream_id: Optional[str] = None, db: Session = Depends(get_db)):
    return admin_service.get_tracks(db, stream_id=stream_id)

@router.post("", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
def create_track(req: TrackCreateRequest, db: Session = Depends(get_db)):
    return admin_service.create_track(db, req)

@router.post("/upload-audio", status_code=status.HTTP_200_OK)
async def upload_track_audio(file: UploadFile = File(...)):
    url_path = await MediaService.save_media_file(file, is_video=False)
    return {"audio_url": url_path}

@router.patch("/{track_id}", response_model=TrackResponse)
def update_track(track_id: str, req: TrackUpdateRequest, db: Session = Depends(get_db)):
    return admin_service.update_track(db, track_id, req)

@router.delete("/{track_id}", status_code=status.HTTP_200_OK)
def delete_track(track_id: str, db: Session = Depends(get_db)):
    admin_service.delete_track(db, track_id)
    return {"message": "Track deleted successfully"}
