"""stt helper functions
"""
import os
import time
from pathlib import Path
import json

import azure.cognitiveservices.speech as speechsdk
import pandas as pd

HOST = os.getenv('HOST')
ENDPOINT = os.getenv('ENDPOINT')

def from_file(in_path: str, out_path: str):
    """ take audio from in_path and generate assets in out_path
    """

    speech_config = speechsdk.SpeechConfig(host=HOST, endpoint=ENDPOINT)
    speech_config.request_word_level_timestamps()
    audio_input = speechsdk.AudioConfig(filename=str(in_path))
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    done = False

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    utterance_evts = []
    result_evts = []
    

    speech_recognizer.recognizing.connect(utterance_evts.append)
    speech_recognizer.recognized.connect(result_evts.append)

    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)

    utterances_pd = pd.DataFrame([json.loads(u.result.json) for u in utterance_evts])
    utterances_pd.to_csv(Path(out_path, 'utterances.csv'))

    with open(Path(out_path, 'results.json'), 'w', encoding='UTF-8') as f_res:
        f_res.write(json.dumps([json.loads(res.result.json) for res in result_evts]))
