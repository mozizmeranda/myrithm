from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.schemas.exercise import ExerciseResponse, ExerciseCreateRequest, ExerciseUpdateRequest
from app.services.admin_service import AdminService
from app.services.media_service import MediaService

router = APIRouter(prefix="/api/v1/admin/exercises", tags=["Admin Exercises"], dependencies=[Depends(require_admin)])
admin_service = AdminService()

@router.get("", response_model=list[ExerciseResponse])
def get_exercises(stream_id: Optional[str] = None, db: Session = Depends(get_db)):
    return admin_service.get_exercises(db, stream_id=stream_id)

@router.post("", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(req: ExerciseCreateRequest, db: Session = Depends(get_db)):
    return admin_service.create_exercise(db, req)

@router.post("/upload-video", status_code=status.HTTP_200_OK)
async def upload_exercise_video(file: UploadFile = File(...)):
    url_path = await MediaService.save_media_file(file, is_video=True)
    return {"video_url": url_path}

@router.patch("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(exercise_id: str, req: ExerciseUpdateRequest, db: Session = Depends(get_db)):
    return admin_service.update_exercise(db, exercise_id, req)

@router.delete("/{exercise_id}", status_code=status.HTTP_200_OK)
def delete_exercise(exercise_id: str, db: Session = Depends(get_db)):
    admin_service.delete_exercise(db, exercise_id)
    return {"message": "Exercise deleted successfully"}
