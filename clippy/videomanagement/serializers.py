from . models import *
from rest_framework import serializers


class TemplatePromptsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplatePrompts
        fields = "__all__"


class MusicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Music
        fields = "__all__"
