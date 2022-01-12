""" main stt application.
"""
import os

import azure.cognitiveservices.speech as speechsdk

SPEECH_KEY = os.getenv('SPEECH_KEY')
REGION = os.getenv('REGION')

def from_file(in_path: str, out_path: str):
    """ take audio/video from in_path and generate assets in out_path 
    """

    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=REGION)
    audio_input = speechsdk.AudioConfig(filename="in_path")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result = speech_recognizer.recognize_once_async().get()
    print(result.text)
