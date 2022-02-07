""" test from_file
"""
from pathlib import Path
import requests
import src.task

TEST_VIDEO = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4'

def test_process():
    task_id = ''
    try:
        src.task.create_folders()
        req_obj = requests.get(TEST_VIDEO)
        in_video_path = Path(src.task.IN_DIR, 'test.mp4')
        with open(in_video_path, 'wb') as f_in:
            f_in.write(req_obj.content)
        task_id = src.task.create_task(in_video_path)
        src.task.process_sync(task_id)
    finally:
        src.task.delete(task_id)