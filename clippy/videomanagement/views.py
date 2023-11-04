from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from .gptUtils import make_video

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
        voice_id = request.data.get('voice_Id', 1)
        title = request.data.get('title')
        prompt = request.data.get('prompt')
        target_audience = request.data.get('target_audience')

        template = TemplatePrompts.objects.get(id = template_id)
        voice_model = VoiceModels.objects.get(id = voice_id)
        make_video(template, userprompt = prompt, title = title, voice_model = voice_model)

        return Response({"message": "The video has been made successfully"})
