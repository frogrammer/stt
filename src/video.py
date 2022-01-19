"""helpers for video files
"""
from ctypes.wintypes import WORD
import json
import math
from pathlib import Path
import string

import moviepy.editor as mp
import nltk
import pandas as pd
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip

SUBTITLE_BUFFER_S = 0
WORDS_PER_LINE = 8
SPEAKER_COLOUR = ['white', 'yellow', 'purple', 'orange', 'pink', 'red', 'green', 'blue']

nltk.download('punkt')

def extract_audio(in_path: str) -> str:
    """extract audio from video

    Args:
        in_path (str): path to video

    Returns:
        str: path to audio
    """
    in_clip = mp.VideoFileClip(in_path)
    out_path = f'{".".join(in_path.split(".")[:-1])}.wav'
    in_clip.audio.write_audiofile(out_path)
    return out_path

def _get_captions(row: dict):
    cumulative_pos = 0
    timings = []
    captions = []
    for s in row['Sentences']:
        s = s.replace(',', ',\n')
        num_words = s.count(' ') + 1
        if num_words <= WORDS_PER_LINE:
            captions.append(s)
        else:
            words = s.split(' ')
            for i in range(0, len(words), WORDS_PER_LINE):
                captions.append(' '.join(words[i:i + WORDS_PER_LINE]))

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

def add_subtitles(results_json: str, in_path: str, out_path: str):
    stt_results = []
    with open(results_json, 'r', encoding='UTF-8') as f_json:
        stt_results = json.loads(f_json.read())
    stt_pd = pd.DataFrame([r['NBest'][0] for r in stt_results])
    stt_pd['Sentences'] = stt_pd['Display'].apply(nltk.sent_tokenize)
    stt_pd['Captions'] = stt_pd.apply(_get_captions, axis=1)
    timings_s = stt_pd.explode('Captions')['Captions'].dropna().drop_duplicates()
    srt_s = timings_s.apply(lambda srt: ((srt['Start'], srt['End']), srt['Caption']))
    in_clip = mp.VideoFileClip(in_path)
    subs_generator = lambda txt: TextClip(txt, font='Arial', fontsize=12, color='white', bg_color='black')
    subtitles = SubtitlesClip(srt_s.to_numpy().tolist(), subs_generator)
    result = mp.CompositeVideoClip([in_clip, subtitles.set_position(('center','bottom'))])
    file_ext = in_path.split('.')[-1]
    result.write_videofile(str(Path(out_path, f'out.{file_ext}')), fps=in_clip.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
