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
WORDS_PER_LINE = 8
SPEAKER_COLOUR = ['white', 'yellow', 'purple', 'orange', 'pink', 'red', 'green', 'blue']
FONT = config.CONFIG['FONT']
FONT_SIZE = config.CONFIG['FONT_SIZE']
TEXT_ENCODING = config.CONFIG['TEXT_ENCODING']

def extract_audio(in_video_path: str, out_audio_path:str):
    """extract audio from video

    Args:
        in_path (str): path to video

    Returns:
        str: path to audio
    """
    in_clip = mp.VideoFileClip(in_video_path)
    in_clip.audio.write_audiofile(out_audio_path)

def add_captions(in_srt_path: str, in_video_path: str, out_video_path: str):
    in_clip = mp.VideoFileClip(in_video_path)
    subs_generator = lambda txt: TextClip(txt, font=FONT, fontsize=FONT_SIZE, color='white', bg_color='black')
    # srt does not work so using csv
    srt_s = pd.read_csv(in_srt_path, encoding=TEXT_ENCODING)
    srt_list = [[(i[0], i[1]), i[2]] for i in srt_s.to_numpy().tolist()]
    subtitles = SubtitlesClip(srt_list, subs_generator)
    result = mp.CompositeVideoClip([in_clip, subtitles.set_position(('center','bottom'))])
    result.write_videofile(out_video_path, fps=in_clip.fps, temp_audiofile='/tmp/temp-audio.m4a', remove_temp=True, codec='libx264', audio_codec='aac')
