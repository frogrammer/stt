from enum import Enum
import io
import shutil
from pathlib import Path
import os
import typing
import uuid
import zipfile

import src.stt
import src.video

ENCODING = 'latin-1'
ROOT_DIR = Path(__file__).parent.parent
IN_DIR = str(Path(ROOT_DIR, 'in'))
PROC_DIR = str(Path(ROOT_DIR, 'proc'))
OUT_DIR = str(Path(ROOT_DIR, 'out'))
DO_NOT_ARCHIVE = ['.wav']

class Status(Enum):
    STARTED = 1
    AUDIO_PROCESSED = 2
    STT_PROCESSED = 3
    CAPTIONS_PROCESSED = 4
    ARCHIVED = 5
    COMPLETED = 6
    ERROR = 7

def create_folders():
    for path in [p for p in [IN_DIR, PROC_DIR, OUT_DIR] if not os.path.exists(p)]:
        os.mkdir(path)

def clear_folders():
    for path in [p for p in [IN_DIR, PROC_DIR, OUT_DIR] if os.path.exists(p)]:
        shutil.rmtree(path, True)
    create_folders()

def get_task_path(task_id: str) -> Path:
    return Path(PROC_DIR, task_id)

def create_task(video_path: str) -> str:
    create_folders()
    task_id = str(uuid.uuid4())
    task_path = get_task_path(task_id)
    if not os.path.exists(task_path):
        os.mkdir(task_path)
    shutil.move(video_path, task_path)
    return task_id

def query(task_id: str) -> list:
    return os.listdir(get_task_path(task_id))

def status(task_id: str) -> Status:
    task_path = get_task_path(task_id)
    has_archive = any([f'{task_id}.zip' in f for f in os.listdir(OUT_DIR)])
    has_proc_folder = os.path.exists(task_path)

    if has_archive:
        return Status.ARCHIVED if has_proc_folder else Status.COMPLETED
    elif has_proc_folder:
        has_stt = any(['.json' in f for f in os.listdir(task_path)])
        has_audio = any(['.wav' in f for f in os.listdir(task_path)])
        has_captioned_video = any(['.mp4' in f and task_id in f for f in os.listdir(task_path)])
        return Status.CAPTIONS_PROCESSED if has_captioned_video and has_stt \
            else Status.STT_PROCESSED if has_stt \
            else Status.AUDIO_PROCESSED if has_audio \
            else Status.STARTED
    else:
        return Status.ERROR

def store(task_id: str, file_name: str, data: typing.Union[str, bytes]):
    create_task(task_id)
    data = str(data, ENCODING)
    with open(Path(get_task_path(task_id), file_name), 'w', encoding=ENCODING) as task_f:
        task_f.write(data)

def delete(task_id: str):
    task_path = get_task_path(task_id)
    if os.path.exists(task_path):
        shutil.rmtree(get_task_path(task_id), True)

def archive(task_id: str) -> str:
    task_path = get_task_path(task_id)
    for to_delete in [f for f in query(task_id) if f[-4:] in DO_NOT_ARCHIVE]:
        os.remove(Path(task_path, to_delete))
    return shutil.make_archive(Path(OUT_DIR, task_id), 'zip', task_path)

def process_step(task_id: str):
    task_status = status(task_id)
    task_path = get_task_path(task_id)
    task_files = query(task_id)
    in_video_file = next(iter([f for f in task_files if '.mp4' in f and task_id not in f]), None)
    in_video_path = None if not in_video_file else str(Path(task_path, in_video_file))
    out_video_path = str(Path(task_path, f'{task_id}.mp4'))
    audio_path = str(Path(task_path, f'{task_id}.wav'))
    stt_path = str(Path(task_path, f'{task_id}.json'))
    log_path = str(Path(task_path, f'{task_id}.log'))
    utterances_path = str(Path(task_path, f'{task_id}.csv'))
    if task_status is Status.STARTED:
        src.video.extract_audio(in_video_path, audio_path)
    if task_status is Status.AUDIO_PROCESSED:
        src.stt.process_audio(audio_path, stt_path, utterances_path, log_path)
    if task_status is Status.STT_PROCESSED:
        os.remove(audio_path)
        src.video.add_captions(stt_path, in_video_path, out_video_path)
    if task_status is Status.CAPTIONS_PROCESSED:
        os.remove(in_video_path)
        archive(task_id)
    if task_status is Status.ARCHIVED:
        delete(task_id)

def process_sync(task_id: str):
    task_status = status(task_id)
    while task_status is not (Status.COMPLETED or Status.ERROR):
        process_step(task_id)
        task_status = status(task_id)