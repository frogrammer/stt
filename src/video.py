"""helpers for video files
"""
import moviepy.editor as mp

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
