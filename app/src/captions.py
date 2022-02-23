"""helpers for video files
"""
import json
from pathlib import Path
import os

import moviepy.editor as mp
import nltk
import pandas as pd
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip

import config

SUBTITLE_BUFFER_S = 0
MAX_LINE_LENGTH = 8
IDEAL_LINE_LENGTH = 5
SPEAKER_COLOUR = ['white', 'yellow', 'purple', 'orange', 'pink', 'red', 'green', 'blue']
FONT = config.CONFIG['FONT']
FONT_SIZE = config.CONFIG['FONT_SIZE']

def _get_captions(row: dict):
    cumulative_pos = 0
    timings = []
    captions = []
    for s in row['Sentences']:
        s = s.replace(',', ',\n')
        num_words = s.count(' ') + 1
        if num_words <= MAX_LINE_LENGTH:
            captions.append(s)
        else:
            words = s.split(' ')
            for i in range(0, len(words), IDEAL_LINE_LENGTH):
                if len(words[i:]) <= MAX_LINE_LENGTH:
                    captions.append(' '.join(words[i:]))
                    break;
                else:
                    captions.append(' '.join(words[i:i + IDEAL_LINE_LENGTH]))

    for c in captions:
        num_words = c.count(' ') + 1
        start =  row['Words'][cumulative_pos]['Offset']
        end = row['Words'][cumulative_pos + num_words - 1]['Offset'] + \
            row['Words'][cumulative_pos + num_words - 1]['Duration']
        timings.append({
            "Caption": c,
            "Start": start / 10000000,
            "End": (end  / 10000000) + SUBTITLE_BUFFER_S
        })
        cumulative_pos += num_words
    return timings

def write_srt(stt_path: str, out_srt_path: str):
    stt_results = []
    # read STT json
    with open(stt_path, 'r', encoding='UTF-8') as f_json:
        stt_results = json.loads(f_json.read())

    # restructure with pandas to [(start, end), caption]
    stt_pd = pd.DataFrame([r['NBest'][0] for r in stt_results])
    stt_pd['Sentences'] = stt_pd['Display'].apply(nltk.sent_tokenize)
    stt_pd['Captions'] = stt_pd.apply(_get_captions, axis=1)
    timings_s = stt_pd.explode('Captions')['Captions'].dropna().drop_duplicates()
    srt_s = timings_s.apply(lambda srt: pd.Series({'start':srt['Start'], 'end':srt['End'], 'caption':srt['Caption']}))
    
    # write csv
    srt_s.to_csv(out_srt_path, header=True, index=False)