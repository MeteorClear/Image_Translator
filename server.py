import os
import dotenv
import pathlib
import hashlib
import shutil
from fastapi import FastAPI, UploadFile, File
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

    # todo: check duplication

    # todo: save file info in db

    try:
        pass
        # todo: run process

        # todo: update db

    except Exception as e:
        pass
        # todo: exception

    return