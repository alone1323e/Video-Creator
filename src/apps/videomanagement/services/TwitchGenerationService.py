from typing import Literal
from slugify import slugify

from datetime import date

from ..utils.download_utils import create_twitch_clip_scene

from ..utils.twitch import TwitchClient

from ..utils.file_utils import generate_directory
from ..models import Videos, UserPrompt


def generate_twitch_video(
        mode: Literal["game", "streamer"],
        value: str,
        amt: int = 10,
        started_at: str = ""
        ):

    message = f"Mode : {mode} Value : {value}"
    title = f"{value} {date.today()}"
    dir_name = generate_directory(rf'media\videos\{slugify(title)}')

    user_prompt = UserPrompt.objects.create(template = None, prompt = f'{message}')

    video = Videos.objects.create(prompt = user_prompt,
                                  dir_name = dir_name,
                                  title = title)

    client = TwitchClient(path = dir_name)
    client.set_headers()

    value = client.get_streamer_id(value) if mode == "streamer" else client.get_game_id(value)
    clips = client.get_clips(value, mode, started_at)

    description = "Source : \n"
    for count, clip in enumerate(clips[:amt]):
        downloaded_clip = client.download_clip(clip)
        create_twitch_clip_scene(downloaded_clip, clip.get("title"), video.prompt)
        description += f"{count+1} {clip.get('title')} : {clip.get('url')} \n"

    video.gpt_answer = description
    video.save()
    return video
