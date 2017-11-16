import requests
import time
import urllib.parse as urllibparse
import six
import base64
import datetime
from . import utility
from enum import Enum

AUTH_URL = 'https://accounts.spotify.com/authorize'
CLIENT_ID = 'e1a3ac15261445d39bae81dd74284012'
CLIENT_SECRET = 'c49321b03c874a549e305550475067a9'
REDIRECT_URL = 'http://localhost:8000/callback'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
USER_ALBUMS = 'https://api.spotify.com/v1/me/albums'
GET_ARTIST = 'https://api.spotify.com/v1/artists/'



def make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(six.text_type(
        client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}


class Artist(object):
    def __init__(self, artist_id, name):
        self.artist_id = artist_id
        self.name = utility.remove_redundant_chars(name)
        self.__albums = []
        self.next_query = None

    def get_albums(self, session, auth):       
        if self.__albums == []:
            albums, self.next_query = auth.get_artist_albums_and_next(self.artist_id, session, 50)
            for item in albums:
                item.name = utility.remove_redundant_chars(item.name)
            self.__albums = albums
        return self.__albums

    def is_albums_extendable(self):
        if self.next_query:
            return True
        else:
            return False

    def next_albums(self, session, auth):
        if self.next_query:
            limit, offset = parse_next_query(self.next_query)
            albums, self.next_query = auth.get_artist_albums_and_next(self.artist_id, session, int(limit), int(offset))
            self.__albums = self.__albums.extend(albums)
            return albums

class Album(object):
    def __init__(self, album_id, name, artist_id=None):
        self.album_id = album_id
        self.name = name
        self.artist_id = artist_id


def create_artist_id_list(album_list):
    artist_id_list = []
    for album in album_list:
        artist_id = album.artist_id
        if artist_id not in artist_id_list:
            artist_id_list.append(artist_id)
    return artist_id_list


class Authorization(object):
    """Handles the Spotify Authorization"""

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_type = None
        self.logged_in = False
        self.show_dialog = True
        self.state = None
        self.expire_time = None




#--------Set Attributes------------------------------
    def set_token_with_session(self, session):
        if session:
            if 'acces_token' in session:
                self.logged_in = session['acces_token'] is not None
                if(self.logged_in):
                    self.access_token = session['acces_token']
                    self.refresh_token = session['refresh_token']
                    self.token_type = session['token_type']
                    self.expire_time = datetime.datetime.fromtimestamp(session['expire_time']) 
    

    def clear_session(self, session):
        self.access_token = None
        self.refresh_token = None
        self.token_type = None
        self.logged_in = False
        self.state = None
        self.expire_time = None
        session['acces_token'] = None
        session['refresh_token'] = None
        session['token_type'] = None
        session['expire_time'] = None


    def _set_token_with_response(self, token_info, session):
        self.access_token = token_info['access_token']
        self.token_type = token_info['token_type']
        self.expire_time = datetime.datetime.now() \
        + datetime.timedelta(seconds=token_info['expires_in'])
        self._update_session(session)

    def _update_session(self, session):
        session['acces_token'] = self.access_token
        session['refresh_token'] = self.refresh_token
        session['token_type'] = self.token_type
        session['expire_time'] = time.mktime(self.expire_time.timetuple()) 

#----------------------------------------------------

#--------API CALL-------------------------------------
    def _get_user_albums_data(self, session, limit, offset=None):
        self._check_acces_token(session)
        payload = {'limit': limit}
        if offset is not None:
            payload['offset'] = offset
        urlparams = urllibparse.urlencode(payload)
        headers = self._make_headers()
        headers['Content-Type'] = 'application/json'

        response = requests.get("%s?%s" % (
            USER_ALBUMS, urlparams), headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None


    def _get_acces_token(self, code, session):
        """make a request to get refresh and acces token """
        payload = {'redirect_uri': REDIRECT_URL,
                'code': code,
                'grant_type': 'authorization_code'}

        headers = make_authorization_headers(CLIENT_ID, CLIENT_SECRET)

        response = requests.post(TOKEN_URL, data=payload,
                                headers=headers, verify=True)
        if response.status_code == 200:
            token_info = response.json()
            self.access_token = token_info['access_token']
            self.token_type = token_info['token_type']
            self.refresh_token = token_info['refresh_token']
            self.expire_time = datetime.datetime.now() \
            + datetime.timedelta(seconds=token_info['expires_in'])
            self._update_session(session)

        return response.status_code
    def _get_artist_albums(self, artist_id, session, limit, offset = None):
        self._check_acces_token(session)
        headers = self._make_headers()
        headers['Content-Type'] = 'application/json'
        payload = {'limit': limit, "album_type": "single,album,compilation"}
        if offset is not None:
            payload['offset'] = offset
        urlparams = urllibparse.urlencode(payload)
        response = requests.get("%s?%s" % (
            GET_ARTIST + artist_id + '/albums', urlparams), headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

#------------------------------------------------------


#--------Public Function-------------------------------
    def get_authorize_url(self):
        """ Gets the URL to use to authorize this app"""
        payload = {'client_id': CLIENT_ID,
                   'response_type': 'code',
                   'redirect_uri': REDIRECT_URL,
                   'scope': 'user-library-read'}
        payload['state'] = self.state
        payload['show_dialog'] = self.show_dialog
        urlparams = urllibparse.urlencode(payload)

        return "%s?%s" % (AUTH_URL, urlparams)

    def get_access_token(self, code, state, session):
        """Get access token with callback code and
            returns operation result"""
        if self.state == state:
            status_code = self._get_acces_token(code, session)
            if status_code == 200:
                return True, status_code
            else:
                return False, status_code
        else:
            return False, status_code


    def get_artist_albums_and_next(self, artist_id, session, limit, offset = None ):
        data = self._get_artist_albums(artist_id, session, limit, offset )
        album_list = []
        if data:
            for item in data['items']:
                album_list.append(Album(item['id'], item['name']))
        return album_list, data['next']

    def get_artist(self,session, artist_id):
        self._check_acces_token(session)
        headers = self._make_headers()
        headers['Content-Type'] = 'application/json'

        response = requests.get(GET_ARTIST + artist_id, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return Artist(data['id'], data['name'])
        else:
            return None

    def get_users_all_artists(self, session):
        """ Get users all saved artists """
        self._check_acces_token(session)
        offset = 0
        limit = 50
        artist_list = []
        artist_list, next_query = self.get_user_artists_and_next(
            session, limit, offset)
        while next_query is not None:
            limit, offset = parse_next_query(next_query)
            next_artists, next_query = self.get_user_artists_and_next(
                session, int(limit), int(offset))
            artist_list.extend(next_artists)
        return artist_list

    def get_users_all_albums(self, session):
        """ Get users all saved albums """
        self._check_acces_token(session)
        offset = 0
        limit = 50
        album_list = []
        album_list, next_query = self.get_user_albums_and_next(
            session, limit, offset)
        while next_query is not None:
            limit, offset = parse_next_query(next_query)
            next_albums, next_query = self.get_user_albums_and_next(
                session, int(limit), int(offset))
            album_list.extend(next_albums)
        return album_list

    def get_user_albums_and_next(self, session, limit, offset=None):
        """Get users saved albums and next query with given input """
        self._check_acces_token(session)
        next_query = None
        album_list = []
        data = self._get_user_albums_data(session, limit, offset)
        if data:
            next_query = data['next']
            for item in data['items']:
                album_data = item['album']
                album = Album(
                    album_data['id'], album_data['name'], album_data['artists'][0]['id'])
                album_list.append(album)

        return album_list, next_query

    def get_user_artists_and_next(self, session, limit, offset=None):
        """Get users saved artists and next query with given input """
        self._check_acces_token(session)
        next_query = None
        artist_list = []
        data = self._get_user_albums_data(session, limit, offset)
        if data:
            next_query = data['next']
            for item in data['items']:
                if item['album']['artists'][0]:
                    artist_data = item['album']['artists'][0]
                    if not any(a.artist_id == artist_data['id'] for a in artist_list):
                        artist = Artist(artist_data['id'], artist_data['name'])
                        artist_list.append(artist)
        return artist_list, next_query

    def get_artist_all_albums(self, artist_id, session):
        """Get artists all albums """
        self._check_acces_token(session)
        index = 0
        limit = 50
        album_list = []
        album_list, next_query = self.get_artist_albums_and_next(
            artist_id, session, limit, index)
        while next_query is not None:
            offset, limit = parse_next_query(next_query)
            next_albums, next_query = self.get_artist_albums_and_next(
                artist_id, session, int(limit), int(offset))
            album_list.extend(next_albums)
        return album_list


#------------------------------------------------------



    def _make_headers(self):
        return {'Authorization': 'Bearer %s' % self.access_token}


    def _is_token_expired(self):
        if self.expire_time < datetime.datetime.now():
            return True
        else:
            return False

    def _check_acces_token(self, session):
        if self._is_token_expired():
            self._get_acces_token_with_refresh(session)

    def _get_acces_token_with_refresh(self, session):
        payload = {'refresh_token': self.refresh_token,
                   'grant_type': 'refresh_token'}

        headers = make_authorization_headers(CLIENT_ID, CLIENT_SECRET)

        response = requests.post(TOKEN_URL, data=payload,
                                 headers=headers, verify=True)
        if response.status_code == 200:
            token_info = response.json()
            self._set_token_with_response(token_info,session)


    
def parse_next_query(next_query):
    result = urllibparse.urlparse(next_query)
    params = urllibparse.parse_qs(result.query)
    offset, limit = params['offset'][0], params['limit'][0]
    return limit, offset
