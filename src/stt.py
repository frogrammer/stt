"""stt helper functions
"""
from pathlib import Path
import os

import azure.cognitiveservices.speech as speechsdk

HOST = os.getenv('HOST')
ENDPOINT = os.getenv('ENDPOINT')

def from_file(in_path: str, out_path: str):
    """ take audio/video from in_path and generate assets in out_path
    """

    speech_config = speechsdk.SpeechConfig(host=HOST, endpoint=ENDPOINT)
    audio_input = speechsdk.AudioConfig(filename=str(in_path))
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()
    print(result.text)

    with open(Path(out_path, 'out.txt'), 'wb') as f_out:
        f_out.write(result.text)
