from .file_utils import select_music, select_background
from moviepy.editor import AudioFileClip, concatenate_audioclips, CompositeAudioClip, ImageClip, VideoFileClip,vfx,\
    concatenate_videoclips, CompositeVideoClip
from ..models import *
from PIL import Image


def make_video(video, dir_name, music=True):
    template = video.prompt.template
    silent = AudioFileClip('media\\media\\sound_effects\\blank.wav')
    black = ImageClip('media\\media\\stock_images\\black.jpg')
    sounds = Speech.objects.filter(prompt = video.prompt)

    background = select_background(template.category)

    clip = ImageClip(background.file.path)
    w, h = clip.size
    sound_list = []
    vids = []
    for sound in sounds:
        audio = AudioFileClip(sound.file.path)
        sound_list.append(audio)
        sound_list.append(silent)
        sound_list.append(silent)
        scenes = SpeechImage.objects.filter(scene = sound)

        if len(scenes)> 0 :
            for x in scenes:
                if 'jpg' in x.file.path or 'jpeg' in x.file.path:
                    image = Image.open(x.file.path)
                    image = image.convert('RGB')
                    image = image.resize((int(w*0.65), int(h*0.65)))
                    image.save(x.file.path)

                    image = ImageClip(x.file.path).set_duration((audio.duration+2)/len(scenes))
                    image = image.fadein(image.duration*0.2).fadeout(image.duration*0.2)
                    vids.append(image)
        else:
            vids.append(black.set_duration(audio.duration+2))


    #top=65, left = 355, opacity=4
    final_video = concatenate_videoclips(vids).margin(top=background.image_pos_top, left = background.image_pos_left,
                                                      opacity=4)

    final_audio = concatenate_audioclips(sound_list)
    final_audio.write_audiofile(f"{dir_name}\\output_audio.wav")
    if music:
        selected_music = select_music(template.category)

        music = AudioFileClip(selected_music.file.path).volumex(0.07)
        if music.duration > final_audio.duration:
            music = music.subclip(0, final_audio.duration)

        music = music.audio_fadein(4).audio_fadeout(4)
        final_audio = CompositeAudioClip([final_audio, music])

    clip = clip.set_duration(final_audio.duration)
    clip = clip.set_audio(final_audio)

    color = [int(x) for x in background.color.split(',')]

    masked_clip = clip.fx(vfx.mask_color, color = color, thr = background.through, s = 7)

    final_clip = CompositeVideoClip([final_video,
                                    masked_clip.set_duration(final_audio.duration)
    ], size = (1920, 1080))

    intro = VideoFileClip(Intro.objects.filter(category = template.category)[0].file.path)
    outro = VideoFileClip(Outro.objects.filter(category = template.category)[0].file.path)

    final_video = concatenate_videoclips([intro, final_clip, outro], method='compose')

    final_video.write_videofile(f"{dir_name}\\output_video.mp4", fps = 24, threads = 8)

    for sound in sound_list:
        sound.close()

    video.output = f"{dir_name}\\output_video.mp4"
    video.save()
    return video
