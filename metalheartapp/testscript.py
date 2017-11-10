import requests
import time
import urllib.parse as urllibparse

AUTH_URL = 'https://accounts.spotify.com/authorize'
CLIENT_ID = 'e1a3ac15261445d39bae81dd74284012'
CLIENT_SECRET = 'c49321b03c874a549e305550475067a9'
REDIRECT_URL = 'http://localhost:8000/callback'

def foo():
    payload = {'client_id': CLIENT_ID, 'response_type' : 'code', 'redirect_uri':REDIRECT_URL}
    r = requests.get(AUTH_URL, params=payload)
    return r

def get_authorize_url():
    payload = {'client_id': CLIENT_ID,
                   'response_type': 'code',
                   'redirect_uri': REDIRECT_URL}

    payload['scope'] = 'user-read-private user-read-email'
    payload['show_dialog'] = True

    urlparams = urllibparse.urlencode(payload)

    return "%s?%s" % (AUTH_URL, urlparams)