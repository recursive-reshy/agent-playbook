import json

def load_session( cookie_text ):
    return json.loads( cookie_text )