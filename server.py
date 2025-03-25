import os
import dotenv
import pathlib
import fastapi

dotenv.load_dotenv()


UPLOAD_DIR = pathlib.Path(os.getenv("UPLOAD_DIR"))
RESULT_DIR = pathlib.Path(os.getenv("RESULT_DIR"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


#app = fastapi.FastAPI()

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