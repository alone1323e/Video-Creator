from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .utils.video_utils import make_video
from rest_framework.decorators import api_view, permission_classes
from .utils.download_utils import download_playlist, download_images
from .utils.prompt_utils import format_prompt
from .utils.gpt_utils import get_reply
from .utils.audio_utils import make_scenes_speech
from.utils.file_utils import generate_directory
from slugify import slugify

class TemplatePromptView(viewsets.ModelViewSet):
    serializer_class = TemplatePromptsSerializer
    queryset = TemplatePrompts.objects.all()
    permission_classes = [AllowAny]


class MusicView(viewsets.ModelViewSet):
    serializer_class = MusicSerializer
    queryset = Music.objects.all()
    permission_classes = [AllowAny]


class TestView(viewsets.ModelViewSet):
    serializer_class = TemplatePromptsSerializer
    queryset = TemplatePrompts.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        template_id = request.data.get('template_id', 2)
        voice_id = request.data.get('voice_id', 1)
        title = request.data.get('title')
        prompt = request.data.get('prompt')
        gptModel = request.data.get('gpt_model')
        target_audience = request.data.get('target_audience')

        template = TemplatePrompts.objects.get(id = template_id)
        voice_model = VoiceModels.objects.get(id = voice_id)

        userprompt = UserPrompt.objects.create(template = template, prompt = prompt)
        userprompt.save()

        message = format_prompt(template, userprompt = userprompt, title = title)
        vid = Videos.objects.create(title = title, prompt = userprompt)

        x = get_reply(message, gpt_model = gptModel)
        vid.gpt_answer = x

        dir_name = generate_directory(f'media\\media\\videos\\{slugify(x["title"])}')
        make_scenes_speech(x, vid, voice_model, dir_name)

        for j in vid.gpt_answer['scenes']:
            scene = Speech.objects.get(prompt = vid.prompt, text = j['dialogue']["dialogue"].strip())
            for image in j['images']:
                l = download_images(image,f'{dir_name}/images/', amount = 1)
                if len(l) > 0:
                    SpeechImage.objects.create(scene = scene, file = l[0])

        vid.save()

        result = make_video(vid, dir_name)

        return Response({"message": "The video has been made successfully",
                         "result": VideoSerializer(result).data})

@api_view(['POST'])
@permission_classes([AllowAny])
def downloadPlaylist(request):
    category = request.data.get('category')
    link = request.data['link']
    download_playlist(link, category = category)
    return Response({'Message': 'Successful'})

