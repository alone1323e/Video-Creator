import g4f
import json


def check_json(json):
    for scene in json['scenes']:
        if ':' not in scene['dialogue']:
            return False

    return True


def get_reply(prompt, time=0, format="json"):
    time += 1
    g4f.logging = True  # enable logging
    g4f.check_version = False

    response = g4f.ChatCompletion.create(model = "gpt-3.5-turbo", messages = [{"content": prompt}], stream = True, )
    x = ""
    for message in response:
        x += message
    if format == "json":
        try:

            js = json.loads(x)
            if not check_json(js):
                raise Exception('Wrong format in dialogue')

            return js

        except Exception:
            if time == 5:
                raise Exception("Max gpt limit is 5 , try again with different prompt !!")

            return get_reply(prompt, time = time)
    return x

