import os
import sys
import dotenv
import shutil
import hashlib

from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

# Load image processing module
BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR / "source"
sys.path.append(str(MODULE_DIR))
from source import image_processing

# Load environment variables from .env file
dotenv.load_dotenv()

# MongoDB environment variables
MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Directories for uploaded and processed files
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))
RESULT_DIR = Path(os.getenv("RESULT_DIR"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Max file size: 5MB
MAX_SIZE = 5 * 1024 * 1024


# Initialize FastAPI
app = FastAPI()


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
    This function reads an input image file for OCR, translation, 
    then processes it, saves the result.

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
async def upload_image(request: Request, image: UploadFile = File(...)):
    """
    Endpoint to upload and process the image file.

    Args:
        image (UploadFile): Image file uploaded by the user

    Returns:
        dict: Success message and file hash.

    Raises:
        HTTPException: 
            - status_code=400: if the file is not an image.
            - status_code=413: if the file size exceeds MAX_SIZE.
            - status_code=303: if the file already exists (duplicate).
            - status_code=500: if processing fails.
    """
    # Check the file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="only image file allowed")
    
    # Check the file size
    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="file size exceeded")

    # Store input file
    save_path = UPLOAD_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_{image.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Calculate the file hash by sha-256
    file_hash = get_file_hash(save_path)

    # Check duplicates in the database by file_hash
    existing_file = collection.find_one({"file_hash": file_hash})
    if existing_file:
        if save_path.is_file():
            save_path.unlink()
        return JSONResponse(
            status_code=303,
            content={"message": "already existing file", "file_hash": file_hash}
        )

    # Insert new record into DB
    try:
        record = {
            "file_hash": file_hash,
            "original_file_path": str(save_path),
            "created_at": datetime.now(timezone.utc),
            "processed": False,
            "processed_at": None,
            "result_file_path": None
        }
        result = collection.insert_one(record)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    # Run the image processing pipeline
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

    # Return success response
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
        HTTPException:
            - status_code=404: if the file hash is not found in the DB.
            - status_code=404: if the file has not been processed yet.
            - status_code=404: if the result file is missing on disk.
    """
    # Query the database for the record with the given hash
    file_info = collection.find_one({"file_hash": file_hash})
    if not file_info:
        raise HTTPException(status_code=404, detail="file hash not found")

    # Check if the file is processed
    processed = file_info.get("processed")
    if not processed:
        raise HTTPException(status_code=404, detail="file did not process")
    
    # Check if the processed file actually exists
    result_file_path = file_info.get("result_file_path")
    if not result_file_path or not Path(result_file_path).is_file():
        raise HTTPException(status_code=404, detail="result file not found")

    # Return success response
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