from .prompt_utils import format_prompt
from .ttsUtils import create_model, save
import os
from slugify import slugify
from .file_utils import generate_directory
from moviepy.editor import AudioFileClip, concatenate_audioclips
from .gptUtils import get_reply


def make_video(template, userprompt, title, voice_model):
    message = format_prompt(template, userprompt = userprompt, title = title)
    x = get_reply(message)
    syn = create_model(model = voice_model.path)
    dir_name = generate_directory(f'media\\media\\videos\\{slugify(x["title"])}')

    silent = AudioFileClip('media\\media\\sound_effects\\blank.wav')

    sounds = []
    for j in x["scenes"]:
        j['dialogue'] = j['dialogue'].split(':')
        sound = save(syn, j['dialogue'][1], save_path = f'{dir_name}/dialogues/{slugify(j["scene"])}.wav')
        sounds.append(sound)

    sound_list = []
    for sound in sounds:
        l = AudioFileClip(sound)
        sound_list.append(l)
        sound_list.append(silent)
        sound_list.append(silent)

    output_audio = concatenate_audioclips(sound_list)
    output_audio.write_audiofile(f"{dir_name}\\output_audio.wav")

