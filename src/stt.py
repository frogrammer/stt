"""stt helper functions
"""
from pathlib import Path
import os
import time

import azure.cognitiveservices.speech as speechsdk

HOST = os.getenv('HOST')
ENDPOINT = os.getenv('ENDPOINT')

def from_file(in_path: str, out_path: str):
    """ take audio/video from in_path and generate assets in out_path
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

    evts = []

    with open(Path(out_path, 'rec.txt'), 'w') as f_rec:
        f_rec.write('')

    def write_events(evts):
        with open(Path(out_path, 'rec.txt'), 'a') as f_rec:
            f_rec.writelines([f'{evt.result.offset}\t{evt.result.text}\n' for evt in evts])

    speech_recognizer.recognizing.connect(evts.append)
    #speech_recognizer.recognized.connect(evts.append)

    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()

    batch_size = 100
    waterline = 0

    while not done:
        time.sleep(.5)
        if len(evts) >= waterline + batch_size:
            write_events(evts[waterline:waterline+batch_size])
            waterline += batch_size

    write_events(evts[waterline:])
