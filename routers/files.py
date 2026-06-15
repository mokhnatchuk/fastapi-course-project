import logging
import os
import shutil
from fastapi import APIRouter, File, HTTPException, UploadFile, status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    path="/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file to the server",
)
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_dir_name = "uploads"
        os.makedirs(upload_dir_name, exist_ok=True)
        file_location = f"{upload_dir_name}/uploaded_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"info": f"File '{file.filename}' saved at '{file_location}'"}
    except Exception as exc:
        logger.exception("Failed to upload file")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not upload file",
        ) from exc
