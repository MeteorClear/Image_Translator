import os
import sys
import dotenv
import shutil
import hashlib

from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR / "source"
sys.path.append(str(MODULE_DIR))
from source import image_processing

# Load environment variables from .env file
dotenv.load_dotenv()

# MongoDB connection details from environment variables
MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Directories for uploaded files and processed results
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))
RESULT_DIR = Path(os.getenv("RESULT_DIR"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


# FastAPI instance
app = FastAPI()


# cal file hash
def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a given file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: SHA-256 hash of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run(image_path: str, save_path: str) -> None:
    """
    Run the image processing pipeline.  
    The image of a given image path read to perform image translation and store.

    Args:
        image_path (str): Path to the input image.
        save_path (str): Path to save the processed image.
    """
    image_translator = image_processing.ProcessingBlock(
        image_path = image_path,
        save_path = save_path
    )

    image_translator.ocr_process()
    image_translator.recollection_text()
    image_translator.build_blocks()
    image_translator.processing_run()
    image_translator.draw_process()
    image_translator.save_result()

    return


@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    """
    Endpoint to upload and process the image file.

    Args:
        image (UploadFile): Image file uploaded by the user

    Returns:
        dict: Success message and file hash.

    Raises:
        HTTPException: If the file no-image file(404) or already exists(303) or processing fails(500).
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="only image file allowed")

    save_path = UPLOAD_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_{image.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    file_hash = get_file_hash(save_path)

    existing_file = collection.find_one({"file_hash": file_hash})
    if existing_file:
        if save_path.is_file():
            save_path.unlink()
        return JSONResponse(
            status_code=303,
            content={"message": "already existing file", "file_hash": file_hash}
        )

    record = {
        "file_hash": file_hash,
        "original_file_path": str(save_path),
        "created_at": datetime.now(timezone.utc),
        "processed": False,
        "processed_at": None,
        "result_file_path": None
    }
    try:
        result = collection.insert_one(record)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    try:
        result_file_path = RESULT_DIR / f"{file_hash}{Path(image.filename).suffix}"

        run(str(save_path), str(result_file_path))

        collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {
                "processed": True,
                "processed_at": datetime.now(timezone.utc),
                "result_file_path": str(result_file_path)
            }}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"process failure: {str(e)}")

    return {"message": "process success", "file_hash": file_hash}


@app.get("/download/{file_hash}")
async def download_image(file_hash: str):
    """
    Endpoint to download the processed image file using its hash.

    Args:
        file_hash (str): SHA-256 hash of the processed file.
    
    Returns:
        FileResponse: The processed file to download.

    Raises:
        HTTPException: If file hash is not found(404), file is not processed(404), or result file is missing(404).
    """
    file_info = collection.find_one({"file_hash": file_hash})

    if not file_info:
        raise HTTPException(status_code=404, detail="file hash not found")

    processed = file_info.get("processed")
    if not processed:
        raise HTTPException(status_code=404, detail="file did not process")
    
    result_file_path = file_info.get("result_file_path")
    if not result_file_path or not Path(result_file_path).is_file():
        raise HTTPException(status_code=404, detail="result file not found")

    return FileResponse(
        path = result_file_path,
        filename = Path(result_file_path).name
    )

'''
Database Record Structure:
record = {
    "file_hash":                SHA-256 hash of the file
    "original_file_path":       Path to the uploaded file
    "created_at":               Timestamp when the file was uploaded(utc)
    "processed":                Boolean to indicate processing status
    "processed_at":             Timestamp when processing completed(utc)
    "result_file_path":         Path to the processed result
}
'''