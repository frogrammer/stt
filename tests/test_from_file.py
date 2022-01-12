""" test from_file
"""
from pathlib import Path

import requests
from src.stt import from_file
from src.video import extract_audio

TEST_VIDEO = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4'
ROOT_DIR = Path(__file__).parent.parent
IN_PATH = str(Path(ROOT_DIR, 'in', 'test.mp4'))
OUT_PATH = str(Path(ROOT_DIR, 'out'))

def test_from_file():
    """ downloads TEST_VIDEO and runs from_file. does not verify result.
    """

    req_obj = requests.get(TEST_VIDEO)
    with open(IN_PATH, 'wb') as f_in:
        f_in.write(req_obj.content)

    audio_path = extract_audio(IN_PATH)

    from_file(audio_path, OUT_PATH)
