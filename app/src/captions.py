"""helpers for video files
"""
import json
from pathlib import Path
import os

import moviepy.editor as mp
import nltk
import pandas as pd
import spacy
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip

import config

SUBTITLE_BUFFER_S = 0
MAX_LINE_LENGTH = 8
IDEAL_LINE_LENGTH = 6
MIN_LINE_LENGTH = 5

FONT = config.CONFIG['FONT']
FONT_SIZE = config.CONFIG['FONT_SIZE']
POS_LINEBREAK = ['NN', 'VB', '.', ',']
POS_LINESTART = ['CC', 'TO']
PUNCTUATION = [',', '.', 'n\'t', '\'', '?', '!', '\'s']
CAPTION_ENGINE = config.CONFIG['CAPTIONING']

def _words_to_caption(words: list[str]) -> str:
    caption = ' '.join(words)
    for p in PUNCTUATION:
        caption = caption.replace(f' {p}', p)
    return caption

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
                    break
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

def _get_captions_spacy(row: dict):
    nlp = spacy.load('en_core_web_sm')  # shoud not require web call as downloaded in build process
    cumulative_pos = 0
    timings = []
    captions = []
    for s in row['Sentences']:
        nlp_s = nlp(s)
        s = s.replace(',', ',\n')
        num_words = s.count(' ') + 1
        if num_words <= MAX_LINE_LENGTH:
            captions.append(s)
        else:
            words = s.split(' ')
            for i in range(0, len(words), IDEAL_LINE_LENGTH):
                if len(words[i:]) <= MAX_LINE_LENGTH:
                    captions.append(' '.join(words[i:]))
                    break
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

def _get_captions_nltk(row: dict):
    try:
        cumulative_pos = 0
        timings = []
        captions = []
        sentences_words = [nltk.word_tokenize(s) for s in row['Sentences']]
        sentences_pos = nltk.pos_tag_sents(sentences_words)
        # try to fix issues where length of pos does not match stt words due to splitting
        # e.g. "wan na" -> "wanna"
        for s_idx, s_pos in enumerate(sentences_pos):
            to_delete = []
            stt_sent_words = row['Sentences'][s_idx].split(' ')
            for w_idx, w_pos in enumerate(s_pos[:-1]):
                try:
                    if w_idx <= len(stt_sent_words) and w_idx not in to_delete and stt_sent_words[w_idx] == f'{w_pos[0]}{s_pos[w_idx+1][0]}':
                        s_pos[w_idx] = (stt_sent_words[w_idx], w_pos[1])
                        to_delete.append(w_idx+1)
                except:
                    pass
            for w_idx in to_delete:
                del s_pos[w_idx]

        for s_pos in sentences_pos:
            if len(s_pos) <= MAX_LINE_LENGTH:
                captions.append(_words_to_caption([w_pos[0] for w_pos in s_pos]))
            else:
                candidate_linebreaks = [idx for idx, val in enumerate(s_pos) if any([pos in val[1] for pos in POS_LINEBREAK])]
                candidate_linebreaks.extend([idx -1 for (idx, val) in enumerate(s_pos) if any([pos in val[1] for pos in POS_LINESTART]) and idx > 1])
                last_linebreak = 0
                curr_caption_words = []
                for idx, w_pos in enumerate(s_pos):
                    curr_caption_words.append(w_pos[0])
                    preferred_candidate = (idx in candidate_linebreaks and idx-last_linebreak >= IDEAL_LINE_LENGTH)
                    not_a_better_candidate = (idx in candidate_linebreaks and idx-last_linebreak >= MIN_LINE_LENGTH and idx + 1 not in candidate_linebreaks)
                    no_candidates_within_max_length = (not any([i in candidate_linebreaks for i in range(last_linebreak, last_linebreak + MAX_LINE_LENGTH)]) and idx - last_linebreak == IDEAL_LINE_LENGTH)
                    is_last = idx == len(s_pos) - 1
                    punctuation_follows = is_last or s_pos[idx+1][0] in PUNCTUATION
                    create_caption = is_last or not punctuation_follows and(preferred_candidate or not_a_better_candidate or no_candidates_within_max_length)
                    if create_caption:
                        caption = _words_to_caption(curr_caption_words)
                        if is_last and len(curr_caption_words) < MIN_LINE_LENGTH:
                            captions[-1] = f'{captions[-1]} {caption}'
                        else:
                            captions.append(caption)
                        curr_caption_words = []
                        last_linebreak = idx

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
    except:
        timings = _get_captions(row)
    return timings

CAPTIONING = {
    'BASIC': _get_captions,
    'NLTK': _get_captions_nltk,
    'SPACY': _get_captions_spacy
}

def write_srt(stt_path: str, out_srt_path: str):
    stt_results = []
    # read STT json
    with open(stt_path, 'r', encoding='UTF-8') as f_json:
        stt_results = json.loads(f_json.read())

    # restructure with pandas to [(start, end), caption]
    stt_pd = pd.DataFrame([r['NBest'][0] for r in stt_results])
    stt_pd['Sentences'] = stt_pd['Display'].apply(nltk.sent_tokenize)
    stt_pd['Captions'] = stt_pd.apply(CAPTIONING[CAPTION_ENGINE], axis=1)
    timings_s = stt_pd.explode('Captions')['Captions'].dropna().drop_duplicates()
    srt_s = timings_s.apply(lambda srt: pd.Series({'start':srt['Start'], 'end':srt['End'], 'caption':srt['Caption']}))
    
    # write csv
    srt_s.to_csv(out_srt_path, header=True, index=False)
