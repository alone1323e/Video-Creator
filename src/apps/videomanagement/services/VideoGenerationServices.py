from ..utils.download_utils import create_image_scenes, download_music
from ..utils.prompt_utils import format_prompt, format_prompt_for_official_gpt
from ..utils.gpt_utils import get_reply
from ..utils.audio_utils import make_scenes_speech
from ..utils.file_utils import generate_directory
from ..models import TemplatePrompts, Videos, VoiceModels, UserPrompt, Avatars, Intro, Outro
from django.conf import settings
from ..defaults import default_format
from slugify import slugify
from typing import Union, Literal

import logging


logger = logging.getLogger(__name__)


def generate_video(template_id: Union[str, int, None],
                   message: str,
                   gpt_model: Union[str, None],
                   images: Union[str, bool, Literal["WEB", "AI"]],
                   avatar_selection: Union[str],
                   style: Literal["vivid", "natural"],
                   target_audience: str,
                   music: Union[str, None] = None,
                   background: str = None,
                   intro: str = None,
                   outro: str = None,
                   voice_id: Union[int, None] = None,
                   ) -> Videos:

    avatar_selection = int(avatar_selection) if avatar_selection.isnumeric() else "no_avatar"

    template = TemplatePrompts.get_template(template_id)
    logger.info("Retrieved template")

    if template:
        category = template.category
        template_format = template.format

    else:
        template_format = default_format
        category = template_id if len(template_id) > 0 and not template_id.isnumeric() else ""
        template = None

    if settings.GPT_OFFICIAL:
        prompt = format_prompt_for_official_gpt(template_format = template_format, template_category = category,
                                                userprompt = message, target_audience = target_audience)

        message = prompt[0]+prompt[1]

    else:
        prompt = format_prompt(template_format = template_format, template_category = category, userprompt = message,
                               target_audience = target_audience)

        logger.info("api call in gpt4free")

    x = get_reply(prompt, gpt_model = gpt_model)

    user_rompt = UserPrompt.objects.create(template = template, prompt = F'{message}')
    user_rompt.save()
    logger.info(f"Created the user_prompt instance with id : {user_rompt.id}")

    dir_name = generate_directory(rf'media\videos\{slugify(x["title"])}')

    if intro and outro:
        intro = Intro.objects.get(id = int(intro))
        outro = Outro.objects.get(id = int(outro))

    vid = Videos.objects.create(title = x['title'], prompt = user_rompt, dir_name = dir_name, gpt_answer = x,
                                background = background, intro = intro, outro = outro)
    logger.info(f"Created the video instance with id : {vid.id}")

    if avatar_selection != "no_avatar":
        selected_avatar = Avatars.select_avatar(selected = avatar_selection)
        voice_model = selected_avatar.voice
        vid.avatar = selected_avatar

    else:
        voice_model = VoiceModels.objects.get(id = voice_id) if voice_id else VoiceModels.select_voice()

    vid.voice_model = voice_model
    vid.save()

    make_scenes_speech(vid)
    logger.info(f"Generated the scenes audios for the video with id : {vid.id}")

    vid.music = download_music(music)

    if images:
        vid.mode = images
        create_image_scenes(vid, mode = images, style = style)
        logger.info(f"Generated the images for the video with id : {vid.id}")

    vid.status = "GENERATION"
    vid.save()

    return vid
