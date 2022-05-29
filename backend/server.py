import os
import enum
import pathlib
import json
import uuid
import time
import datetime
import base64
import threading
import asyncio
import queue

from typing import List, Dict, Optional
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor

import fastapi
from fastapi import FastAPI
from fastapi import Cookie
from fastapi import Request
from fastapi import responses
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from fastapi.responses import RedirectResponse

from pydantic import BaseModel

from src.controllers import BaseController

from src.image_generator import PCAStyleGan
from src.image_generator import PCAStyleGANEdits
from src.custom_logging import Logger
from src.user_study import UserStudy

DEBUGGING = os.environ.get('GANSLIDER_DEBUGGING', 'False').lower() in [
    'true', '1', 't']
ROOT_DIR = os.environ.get('GANSLIDER_ROOT_DIR', '/')
BACKEND_SERVE = os.environ.get('GANSLIDER_BACKEND_SERVE', 'False').lower() in [
    'true', '1', 't']

pca_stylegan_generator = PCAStyleGan()

study_controller = BaseController(pca_stylegan_generator)
user_study = UserStudy()

logger = Logger(__name__)
logger.info(["DEBUGGING on:", DEBUGGING])
logger.info(["ROOT_DIR", ROOT_DIR])
logger.info(["Serve wepapp from backend:", BACKEND_SERVE])


lock = threading.Semaphore(1)

executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="GenerateImage")
logExecutor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="Logging")
q = queue.Queue()


class ImageEdit(BaseModel):
    edits: List[Dict[str, str]]
    size: Optional[int]
    seed: int
    timestamp: Optional[int]


class Interaction(BaseModel):
    edits: List[Dict[str, str]]
    size: Optional[int]
    seed: int
    timestamp: Optional[int]
    sliderType: str
    taskid: str
    status: str


class PostTaskSurveyAnswers(BaseModel):
    slider_type: str
    num_sliders: int
    likert: List
    nasa_tlx: List
    taskid: str


class FinalSurvey(BaseModel):
    questions: List


class TaskStatus(BaseModel):
    timestamp: str
    status: str
    edits: List
    taskid: str
    extra: str


class FilmstripUpdate(BaseModel):
    isUpdating: bool
    idx: int
    taskid: str
    timestamp: str


def generate_image(edits, size, seed):
    img = study_controller.new_edit(
        "samplePID", "sampledEID", edits, size, seed)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img = base64.standard_b64encode(buffer.getvalue())

    return img


##################################################################################################################
#
# API START
#
##################################################################################################################

app = FastAPI()

@app.get('/user-study')
def get_user_study(PROLIFIC_PID: str, STUDY_ID: str, SESSION_ID: str):

    if DEBUGGING:
        logger.debug(
            f"User Study requested for: [PID:{PROLIFIC_PID}][STUDY_ID:{STUDY_ID}][SESSION_ID:{SESSION_ID}]")

    resp = RedirectResponse(url=ROOT_DIR)
    resp.set_cookie('PROLIFIC_PID', PROLIFIC_PID, httponly=True)
    resp.set_cookie('PROLIFIC_SESSION_ID', SESSION_ID, httponly=True)
    resp.set_cookie('PROLIFIC_STUDY_ID', STUDY_ID, httponly=True)
    resp.set_cookie('SESSION_ID', uuid.uuid4(), httponly=True)
    return resp


@app.post('/api/image')
def get_image(interaction: ImageEdit):

    img = ""
    if lock.acquire():
        task = executor.submit(generate_image, interaction.edits,
                            interaction.size, interaction.seed)
        img = task.result()
        lock.release()

    return {"status_code": 200, "content": {"interaction": interaction.dict(), "image_data": img}}


@app.get('/api/user_study/config')
def get_user_study_config(PROLIFIC_PID: str = Cookie(None), PROLIFIC_SESSION_ID: str = Cookie(None), PROLIFIC_STUDY_ID: str = Cookie(None), SESSION_ID: str = Cookie(None)):
    config = user_study.next(PROLIFIC_PID)
    logger.log_config(config,
                      PROLIFIC_PID,
                      PROLIFIC_SESSION_ID,
                      PROLIFIC_STUDY_ID,
                      SESSION_ID
                      )
    return JSONResponse(config)


@app.post('/api/log/interaction')
def log_interaction(interaction: Interaction, PROLIFIC_PID: str = Cookie(None), PROLIFIC_SESSION_ID: str = Cookie(None), PROLIFIC_STUDY_ID: str = Cookie(None), SESSION_ID: str = Cookie(None)):
    if DEBUGGING:
        logger.debug(f"Log interaction for: {PROLIFIC_PID}")

    try:
        logExecutor.submit(
            logger.log_interaction,
            PROLIFIC_PID,
            PROLIFIC_SESSION_ID,
            PROLIFIC_STUDY_ID,
            SESSION_ID,
            interaction.edits,
            interaction.seed,
            interaction.timestamp,
            interaction.sliderType,
            interaction.taskid,
            interaction.status
        )
    except Exception as e:
        logger.error(e, extra={'color': '\033[91m'})
        return 500

    return 200


@app.post('/api/log/post_task_survey')
def log_task_survey(post_task_survey: PostTaskSurveyAnswers, PROLIFIC_PID: str = Cookie(None), PROLIFIC_SESSION_ID: str = Cookie(None), PROLIFIC_STUDY_ID: str = Cookie(None), SESSION_ID: str = Cookie(None)):
    if DEBUGGING:
        logger.debug(f"Log post_task_survey for: {PROLIFIC_PID}")

    try:
        logExecutor.submit(
            logger.log_task_survey,
            post_task_survey.dict(),
            PROLIFIC_PID,
            PROLIFIC_SESSION_ID,
            PROLIFIC_STUDY_ID,
            SESSION_ID
        )
    except Exception as e:
        logger.error(e)
    finally:
        return 200


@app.post('/api/log/final_survey')
def log_interaction(final_survey: FinalSurvey, PROLIFIC_PID: str = Cookie(None), PROLIFIC_SESSION_ID: str = Cookie(None), PROLIFIC_STUDY_ID: str = Cookie(None), SESSION_ID: str = Cookie(None)):
    if DEBUGGING:
        logger.debug(f"Log final_survey for: {PROLIFIC_PID}")

    try:
        logExecutor.submit(
            logger.log_final_survey,
            final_survey.dict(),
            PROLIFIC_PID,
            PROLIFIC_SESSION_ID,
            PROLIFIC_STUDY_ID,
            SESSION_ID
        )
    except Exception as e:
        logger.error(e)
    finally:
        return 200


@app.post('/api/log/task')
def log_task_finished(task: TaskStatus, PROLIFIC_PID: str = Cookie(None), PROLIFIC_SESSION_ID: str = Cookie(None), PROLIFIC_STUDY_ID: str = Cookie(None), SESSION_ID: str = Cookie(None)):
    if DEBUGGING:
        logger.debug(f"Log task status for: {PROLIFIC_PID}")

    try:
        logExecutor.submit(
            logger.log_task,
            task.dict(),
            PROLIFIC_PID,
            PROLIFIC_SESSION_ID,
            PROLIFIC_STUDY_ID,
            SESSION_ID)
    except Exception as e:
        logger.error(e)
    finally:
        return 200


@app.post('/api/log/slider_filmstrip_update')
def log_slider_filmstrip_update(update: FilmstripUpdate, PROLIFIC_PID: str = Cookie(None), PROLIFIC_SESSION_ID: str = Cookie(None), PROLIFIC_STUDY_ID: str = Cookie(None), SESSION_ID: str = Cookie(None)):
    if DEBUGGING:
        logger.debug(f"Log update status {update}")

    try:
        logExecutor.submit(
            logger.log_filmstrip_update,
            update.dict(),
            PROLIFIC_PID,
            PROLIFIC_SESSION_ID,
            PROLIFIC_STUDY_ID,
            SESSION_ID)
    except Exception as e:
        logger.error(e)
    finally:
        return 200


@app.middleware("http")
async def check_cookie(request: Request, call_next):
    pid = request.cookies.get('PROLIFIC_PID')

    if '/user-study' not in request.url.path and not pid:
        return JSONResponse(status_code=401, content={"msg": "You are not authorized to participate in this user study."})

    response = await call_next(request)
    return response


if BACKEND_SERVE:
    app.mount("/", StaticFiles(directory="../frontend/build", html=True))
