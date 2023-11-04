import g4f
import json


def get_reply(prompt,time = 0,format="json"):
    time += 1
    g4f.logging = True  # enable logging
    g4f.check_version = False

    response = g4f.ChatCompletion.create(model = "gpt-3.5-turbo", messages = [{"content": prompt}], stream = True, )
    x = ""
    for message in response:
        x += message
    if format == "json":
        try:
            return json.loads(x)

        except Exception:
            if time == 5:
                return Exception("Max gpt limit is 5 , try again with different prompt !!")

            return get_reply(prompt, time = time)
    return x




