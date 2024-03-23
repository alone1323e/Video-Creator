from rest_framework.response import Response
from slugify import slugify
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from datetime import date

from ..utils.download_utils import create_twitch_clip_scene

from ..utils.twitch import TwitchClient

from ..utils.file_utils import generate_directory
from ..serializers import VideoSerializer
from ..models import Videos, UserPrompt

from ..swagger_serializers import TwitchSerializer


@swagger_auto_schema(operation_description = "generates a video from twitch clips, depending on the game or streamer",
                     method = "POST",
                     request_body = TwitchSerializer)
@api_view(['POST'])
def generate_twitch(request):
    mode = request.data.get('mode', 'game')
    value = request.data.get('value')
    amt = request.data.get('amt', 10)

    message = f"Mode : {mode} Value : {value}"
    title = f"{request.data.get('value')} {date.today()}"
    dir_name = generate_directory(rf'media\videos\{slugify(title)}')

    userprompt = UserPrompt.objects.create(template = None, prompt = f'{message}')

    video = Videos.objects.create(prompt = userprompt,
                                  dir_name = dir_name,
                                  title = title)

    client = TwitchClient(path = dir_name)
    client.set_headers()

    value = client.get_streamer_id(value) if mode == "streamer" else client.get_game_id(value)
    clips = client.get_clips(value, mode)

    for clip in clips[:amt]:
        downloaded_clip = client.download_clip(clip)
        create_twitch_clip_scene(downloaded_clip, clip.get("title"), video.prompt)

    return Response(VideoSerializer(video).data)
