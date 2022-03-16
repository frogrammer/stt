import os

DEFAULT_CONFIG = {
    'CAPTIONING': 'NLP',
    'HOST':'ws://localhost:5000',
    'ENDPOINT':'ws://172.17.0.1:5000/speech/recognition/dictation/cognitiveservices/v1?initialSilenceTimeoutMs=60000',
    'FONT':'Calibri',
    'FONT_SIZE': 32,
    'KEEP_ALIVE': 'http://localhost:5000',
    'TEXT_ENCODING': 'ISO-8859-1',
    'VERBOSE_STT': False
}

CONFIG = {key: type(DEFAULT_CONFIG[key])(os.environ[key]) if key in os.environ else DEFAULT_CONFIG[key] for key in DEFAULT_CONFIG}