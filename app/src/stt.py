"""stt helper functions
"""
import os
import time
from pathlib import Path
import json
import requests
from requests.structures import CaseInsensitiveDict

import azure.cognitiveservices.speech as speechsdk
import pandas as pd

import config, display

HOST = config.CONFIG['HOST']
ENDPOINT = config.CONFIG['ENDPOINT']
KEEP_ALIVE = config.CONFIG['KEEP_ALIVE']
ENABLE_DIARIZATION = False
ENABLE_LOGGING = False
ENABLE_STDOUT = config.CONFIG['VERBOSE_STT']

def stt_keep_alive() -> bool:
    headers = CaseInsensitiveDict()
    headers["Connection"] = "keep-alive"
    headers["Keep-Alive"] = "timeout=5, max=100"
    res = requests.get(KEEP_ALIVE, headers=headers)
    return res.ok

def process_audio(audio_path: str, stt_path: str, log_path: str = ''):
    """ take audio from in_path and generate assets in out_path
    """
    speech_config = speechsdk.SpeechConfig(host=HOST, endpoint=ENDPOINT)
    speech_config.request_word_level_timestamps()
    if(ENABLE_LOGGING and log_path):
        speech_config.enable_audio_logging()
        speech_config.set_property(speechsdk.PropertyId.Speech_LogFilename, log_path)
    if(ENABLE_DIARIZATION):
        speech_config.set_service_property(
            name='speechcontext-PhraseOutput.Format',
            value='Detailed',
            channel=speechsdk.ServicePropertyChannel.UriQueryParameter
        )

        speech_config.set_service_property(
            name='speechcontext-phraseDetection.speakerDiarization.mode',
            value='Anonymous',
            channel=speechsdk.ServicePropertyChannel.UriQueryParameter
    )

    audio_input = speechsdk.AudioConfig(filename=str(audio_path))
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    done = False
    done_evt = None

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        nonlocal done_evt
        done = True
        done_evt = evt
    
    def display_cb(evt):
        display.write_stdout_sameline(f'{"{:<20}".format(evt.offset)}{"{:<40}".format(evt.result.text)}')

    result_evts = []

    if ENABLE_STDOUT:
        speech_recognizer.recognizing.connect(display_cb)
    
    speech_recognizer.recognized.connect(result_evts.append)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)

    with open(stt_path, 'w', encoding='UTF-8') as f_res:
        f_res.write(json.dumps([json.loads(res.result.json) for res in result_evts]))

    