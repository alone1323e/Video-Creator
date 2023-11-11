from .file_utils import select_music
from moviepy.editor import AudioFileClip, concatenate_audioclips, CompositeAudioClip, ImageClip, VideoFileClip,\
    concatenate_videoclips
from ..models import *


def make_video(video, dir_name, music=True):
    template = video.prompt.template
    silent = AudioFileClip('media\\media\\sound_effects\\blank.wav')

    sounds = Speech.objects.filter(prompt = video.prompt).values_list("file", flat=True)

    sound_list = []

    for sound in sounds:
        audio = AudioFileClip(sound)
        sound_list.append(audio)
        sound_list.append(silent)
        sound_list.append(silent)

    final_audio = concatenate_audioclips(sound_list)

    if music:
        selected_music = select_music(template.category)

        music = AudioFileClip(selected_music.file.path).volumex(0.07)
        if music.duration > final_audio.duration:
            music = music.subclip(0, final_audio.duration)

        music = music.audio_fadein(4).audio_fadeout(4)
        final_audio = CompositeAudioClip([final_audio, music])

    image = ImageClip("media/other/back.jpg").set_duration(final_audio.duration)
    image = image.set_audio(final_audio)

    intro = VideoFileClip(Intro.objects.filter(category = template.category)[0].file.path)
    outro = VideoFileClip(Outro.objects.filter(category = template.category)[0].file.path)

    final_video = concatenate_videoclips([intro, image, outro], method='compose')

    final_video.write_videofile(f"{dir_name}\\output_video.mp4", fps = 59)

    for sound in sound_list:
        sound.close()

    video.output = f"{dir_name}\\output_video.mp4"
    video.save()
    return video
