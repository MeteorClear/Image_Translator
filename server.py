import os
import dotenv
import pathlib
import fastapi
import hashlib

dotenv.load_dotenv()


UPLOAD_DIR = pathlib.Path(os.getenv("UPLOAD_DIR"))
RESULT_DIR = pathlib.Path(os.getenv("RESULT_DIR"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


#app = fastapi.FastAPI()

# cal file hash
def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# todo: arg set, image
def upload_image():
    # todo: save image

    # todo: cal hash

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