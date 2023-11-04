import g4f
import json
from .prompt_utils import format_prompt
from .ttsUtils import create_model, save
import os
from slugify import slugify
from .file_utils import generate_directory
from moviepy.editor import AudioFileClip, concatenate_audioclips


def get_reply(prompt,time = 0,format="json"):
    time += 1
    g4f.logging = True  # enable logging
    g4f.check_version = False

    response = g4f.ChatCompletion.create(model = "gpt-3.5-turbo", messages = [{"content": prompt}], stream = True, )
    x = ""
    for message in response:
        x += message
    if format == "json":
        try:
            return json.loads(x)

        except Exception:
            if time == 5:
                return Exception("Max gpt limit is 5 , try again with different prompt !!")

            return get_reply(prompt, time = time)
    return x


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



