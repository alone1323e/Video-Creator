from pytube import Playlist
from ..models import Music, Scene, SceneImage
import os
import uuid
from bing_image_downloader import downloader


def download_playlist(url, category):
    playlist = Playlist(url)
    for music in playlist.videos:
        stream = music.streams.filter(only_audio = True).first()
        try:

            filename = str(uuid.uuid4())
            song = stream.download('media/music')
            new_file = f'media/music/{filename}.mp3'
            os.rename(song, new_file)

            Music.objects.create(name = stream.title, file = new_file, category = category)

        except:
            pass

    return True


def download_image(query, path, amount=1):
    return downloader.download(query = f'{query} hd', limit = amount, output_dir = path, adult_filter_off = True,
                               force_replace = False, timeout = 60, )


def create_image_scenes(video, dir_name):
    for j in video.gpt_answer['scenes']:
        if not video.prompt.template.is_sentenced:
            scene = Scene.objects.get(prompt = video.prompt, text = j['dialogue'].strip())

        if not video.prompt.template.is_sentenced and type(j['image']) is list:
            for image in j['image']:
                downloaded_image = download_image(image, f'{dir_name}/images/', amount = 1)
                if len(downloaded_image) > 0:
                    SceneImage.objects.create(scene = scene, file = downloaded_image[0])

        elif video.prompt.template.is_sentenced:
            for x in j['dialogue']:
                scene = Scene.objects.get(prompt = video.prompt, text = x['sentence'].strip())
                downloaded_image = download_image(x['image'], f'{dir_name}/images/', amount = 1)
                if len(downloaded_image) > 0:
                    SceneImage.objects.create(scene = scene, file = downloaded_image[0])

        else:
            downloaded_image = download_image(j['image'], f'{dir_name}/images/', amount = 1)
            if len(downloaded_image) > 0:
                SceneImage.objects.create(scene = scene, file = downloaded_image[0])






