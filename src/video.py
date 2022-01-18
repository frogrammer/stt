"""helpers for video files
"""
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
import pandas as pd
import math
from pathlib import Path

SUBTITLE_BUFFER_S = 3

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

def add_subtitles(subtitles_path: str, in_path: str, out_path: str):
    subtitles_pd = pd.read_csv(subtitles_path)
    in_clip = mp.VideoFileClip(in_path)

    subtitles_pd['start_s'] = subtitles_pd['Offset'].apply(lambda t: math.floor(t / 10000000))
    subtitles_pd['end_s'] = subtitles_pd.apply(lambda row: math.floor((row['Offset'] + row['Duration']) / 10000000), axis=1)

    subs_generator = lambda txt: TextClip(txt, font='Arial', fontsize=18, color='white', bg_color='black')
    subs_text = []

    # there's probably a better way to do this using window fns.
    for time in range(0, math.floor(in_clip.duration)):
        sub_sub = subtitles_pd.query(f'start_s >= {time} and end_s <= {time + SUBTITLE_BUFFER_S}')
        if len(sub_sub) > 0:
            sub_text = sub_sub['Text'].str.cat(sep=' ')
            subs_text.append(((time, time + SUBTITLE_BUFFER_S), sub_text))

    subtitles = SubtitlesClip(subs_text, subs_generator)
    result = mp.CompositeVideoClip([in_clip, subtitles.set_pos(('center','bottom'))])

    file_ext = in_path.split('.')[-1]

    result.write_videofile(str(Path(out_path, f'out.{file_ext}')), fps=in_clip.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
