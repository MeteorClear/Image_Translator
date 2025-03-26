import os
import dotenv
import pathlib
import hashlib
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from datetime import datetime
from pymongo import MongoClient

dotenv.load_dotenv()


MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

UPLOAD_DIR = pathlib.Path(os.getenv("UPLOAD_DIR"))
RESULT_DIR = pathlib.Path(os.getenv("RESULT_DIR"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


#app = FastAPI()

# cal file hash
def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# api
def upload_image(image: UploadFile = File(...)):
    save_path = UPLOAD_DIR / f"{datetime.datetime().strftime('%Y%m%d_%H%M%S_%f')}_{image.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    file_hash = get_file_hash(save_path)

    existing_file = collection.find_one({"file_hash": file_hash})
    if existing_file:
        raise HTTPException(status_code=303, detail="already existing file")

    record = {
        "file_hash": file_hash,
        "original_file_path": str(save_path),
        "created_at": datetime.datetime(),
        "processed": False,
        "processed_at": None,
        "result_file_path": None
    }
    result = collection.insert_one(record)

    try:
        # todo: run process

        # if run success
        result_file_path = RESULT_DIR / f"{file_hash}{pathlib.Path(image.filename).suffix}"
        collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {
                "processed": True,
                "processed_at": datetime.datetime(),
                "result_file_path": str(result_file_path)
            }}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"process failure: {str(e)}")

    return {"message": "process success", "file_hash": file_hash}


# if exist res file, send file
def download_image(file_hash: str):
    file_info = collection.find_one({"file_hash": file_hash})

    if not file_info:
        raise HTTPException(status_code=404, detail="file hash not found")

    processed = file_info.get("processed")
    if not processed:
        raise HTTPException(status_code=404, detail="file did not process")
    
    result_file_path = file_info.get("result_file_path")
    if not result_file_path or not pathlib.Path(result_file_path).is_file():
        raise HTTPException(status_code=404, detail="result file not found")

    # hash found, processed, response, send file

    return

'''
record = {
    "file_hash":
    "original_file_path":
    "created_at":
    "processed":
    "processed_at":
    "result_file_path":
}
'''