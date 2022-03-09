from enum import Enum
import shutil
from pathlib import Path
import os
import typing
import uuid

import captions, display, stt, video

ENCODING = 'latin-1'
ROOT_DIR = Path(__file__).parent
IN_DIR = str(Path(ROOT_DIR, 'in'))
PROC_DIR = str(Path(ROOT_DIR, 'proc'))
OUT_DIR = str(Path(ROOT_DIR, 'out'))
DO_NOT_ARCHIVE = ['.wav', '.m4a']
PRINT_STDOUT = True

class Status(Enum):
    STARTED = 1
    AUDIO_PROCESSED = 2
    STT_PROCESSED = 3
    CAPTIONS_PROCESSED = 4
    VIDEO_CAPTIONED = 5
    ARCHIVED = 6
    COMPLETED = 7
    ERROR = 8

class Actions(Enum):
    EXTRACT_AUDIO = 1
    PROCESS_STT = 2
    PROCESS_CAPTIONS = 3
    CAPTION_VIDEO = 4
    CREATE_ARCHIVE = 5
    CLEAR_TEMPORARY_FILES = 6
    TERMINATE_SUCCESS = 7
    TERMINATE_ERROR = 8


def create_folders():
    for path in [p for p in [IN_DIR, PROC_DIR, OUT_DIR] if not os.path.exists(p)]:
        os.mkdir(path)

def clear_folders():
    for path in [p for p in [IN_DIR, PROC_DIR, OUT_DIR] if os.path.exists(p)]:
        shutil.rmtree(path, True)
    create_folders()

def get_task_path(task_id: str) -> Path:
    return Path(PROC_DIR, task_id)

def query(task_id: str) -> list:
    return os.listdir(get_task_path(task_id))

def create_task(path: str) -> str:
    create_folders()
    if Path(path).is_file():
        task_id = str(uuid.uuid4())
        task_path = get_task_path(task_id)
        if not os.path.exists(task_path):
            os.mkdir(task_path)
        if '.zip' in path:
            shutil.unpack_archive(path, task_path)
        else:
            shutil.move(path, task_path)
    if Path(path).is_dir():
        shutil.move(path, task_path)
    return task_id

def status(task_id: str) -> Status:
    task_path = get_task_path(task_id)
    has_archive = any([f'{task_id}.zip' in f for f in os.listdir(OUT_DIR)])
    has_proc_folder = os.path.exists(task_path)

    if has_archive:
        return Status.ARCHIVED if has_proc_folder else Status.COMPLETED
    elif has_proc_folder:
        has_stt = any(['.json' in f for f in os.listdir(task_path)])
        has_audio = any(['.wav' in f for f in os.listdir(task_path)])
        has_srt = any(['.csv' in f for f in os.listdir(task_path)])
        has_captioned_video = any(['.mp4' in f and task_id in f for f in os.listdir(task_path)])
        return Status.VIDEO_CAPTIONED if has_captioned_video and has_srt \
            else Status.CAPTIONS_PROCESSED if has_srt \
            else Status.STT_PROCESSED if has_stt \
            else Status.AUDIO_PROCESSED if has_audio \
            else Status.STARTED
    else:
        return Status.ERROR

def print_status(task_id: str):
    task_status = status(task_id)
    display.write_stdout(f'id={task_id}\tstatus={task_status.name}\taction={Actions(task_status.value).name}')


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
    # if someone has input audio, stt or srt with the video, use the provided. Else generate something new.
    in_video_file = next(iter([f for f in task_files if '.mp4' in f and task_id not in f]), None)
    in_srt = next(iter([f for f in task_files if '.csv' in f and task_id not in f]), None)
    in_stt = next(iter([f for f in task_files if '.json' in f and task_id not in f]), None)
    in_audio = next(iter([f for f in task_files if '.wav' in f and task_id not in f]), None)
    in_video_path = None if not in_video_file else str(Path(task_path, in_video_file))
    out_video_path = str(Path(task_path, f'{task_id}.mp4'))
    srt_path = str(Path(task_path, in_srt if in_srt else f'{task_id}.csv'))
    audio_path = str(Path(task_path, in_audio if in_audio else f'{task_id}.wav'))
    stt_path = str(Path(task_path, in_stt if in_stt else f'{task_id}.json'))
    log_path = str(Path(task_path, f'{task_id}.log'))
    print_status(task_id)
    if task_status is Status.STARTED:
        video.extract_audio(in_video_path, audio_path)
    if task_status is Status.AUDIO_PROCESSED:
        if stt.stt_keep_alive():
            stt.process_audio(audio_path, stt_path, log_path)
        else: 
            err = 'Could not connect to cogntive service: {stt.KEEP_ALIVE}, {stt.HOST}'
            display.write_stderr(err)
            raise err
    if task_status is Status.STT_PROCESSED:
        try:
            os.remove(audio_path)
        except:
            pass
        captions.write_srt(stt_path, srt_path)
    if task_status is Status.CAPTIONS_PROCESSED:
        video.add_captions(srt_path, in_video_path, out_video_path)
    if task_status is Status.VIDEO_CAPTIONED:
        os.remove(in_video_path)
        archive(task_id)
    if task_status is Status.ARCHIVED:
        delete(task_id)

def process_sync(task_id: str):
    task_status = status(task_id)
    while task_status is not (Status.COMPLETED or Status.ERROR):
        process_step(task_id)
        task_status = status(task_id)

def get_tasks() -> list:
    return [d for d in os.listdir(PROC_DIR) if Path(PROC_DIR, d).is_dir()]