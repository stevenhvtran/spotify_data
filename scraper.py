"""
A scraper for my Spotify account - extracts playlist data into a pandas df
"""
from urllib.parse import urlencode
import requests
import pandas as pd


def get_callback_url(client_id, redirect_uri, scopes=''):
    """
    Gets the URL for the user to complete OAuth2 login
    :returns: The URL that the user has to visit
    """
    base_url = 'https://accounts.spotify.com/authorize/?'
    query_params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scopes
        }
    encoded_params = urlencode(query_params)
    encoded_url = base_url + encoded_params
    return encoded_url


def parse_access_code_url(access_code_url):
    """
    Parses an access code containing URL and returns just the code
    :access_code_url: The redirect URL after the user logs in
    :returns: The access code without the rest of the URL
    """
    access_code = access_code_url.split('?code=')[1]
    return access_code


def get_access_token(access_code, redirect_uri, client_id, client_secret):
    """
    Gets a user's access token from their access code
    :access_code: The user's access code after they login to their account
    :returns: The access token linked to the access code is returned
    """
    request_body = {
        'grant_type': 'authorization_code',
        'code': access_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
        }
    response = requests.post('https://accounts.spotify.com/api/token',
                             data=request_body)
    json_response = response.json()
    return json_response['access_token']


def get_user(access_token):
    header = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me',
                            headers=header)
    user_data = response.json()
    user = User(user_data, access_token)
    return user


class User:
    def __init__(self, user_data, access_token):
        self.access_token = access_token
        self.user_data = user_data
        self.get_user_playlists()

    def __getattr__(self, item):
        return self.user_data[item]

    def __repr__(self):
        return self.user_data['display_name']

    def get_user_playlists(self):
        user_id = self.user_data['id']
        access_token = self.access_token
        playlist_url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        path_param = {'user_id': user_id}
        header = {'Authorization': f'Bearer {self.access_token}'}
        playlist_data = requests.get(playlist_url,
                                     params=path_param,
                                     headers=header).json()
        items = playlist_data['items']
        playlists = []
        for playlist in items:
            if playlist['owner']['id'] == self.id:
                playlists.append(Playlist(user_id, access_token, playlist))
        self.user_data.update({'playlists': playlists})


class Playlist:
    def __init__(self, user_id, access_token, playlist_data):
        self.user_id = user_id
        self.access_token = access_token
        self.playlist_data = playlist_data
        self.get_playlist_tracks()

    def __getattr__(self, item):
        return self.playlist_data[item]

    def __repr__(self):
        return self.playlist_data['name']

    def get_playlist_tracks(self):
        user_id = self.user_id
        access_token = self.access_token
        playlist_id = self.playlist_data['id']
        query_param = {'fields': 'items(added_at, track)'}
        tracks_url = f'https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}/tracks'
        header = {'Authorization': f'Bearer {self.access_token}'}
        tracks_data = requests.get(tracks_url,
                                   headers=header,
                                   params=query_param).json()
        track_items = tracks_data['items']
        tracks = [Track(access_token, item) for item in track_items]
        self.playlist_data.update({'tracks': tracks})


class Track:
    def __init__(self, access_token, track_data):
        self.access_token = access_token
        self.track_data = track_data['track']
        self.track_data.update({'added_at': track_data['added_at']})

    def __getattr__(self, item):
        return self.track_data[item]

    def __repr__(self):
        return self.track_data['name']


redirect_uri = 'http://localhost:3000/callback'
client_id = input('What is your client ID? ')
client_secret = input('What is your client secret? ')

# Get the user's callback URL for further authentication
scopes = 'user-library-read playlist-read-private user-top-read'
callback_url = get_callback_url(client_id, redirect_uri, scopes)

# Get the access code from the URL
input_message = f'Go to {callback_url} and paste the url here: \n'
access_code_url = input(input_message)
access_code = parse_access_code_url(access_code_url)

# Get the user's access token for further API usage
access_token = get_access_token(access_code, redirect_uri, client_id,
                                client_secret)

user = get_user(access_token)

columns = ['track_name', 'playlist_name', 'album_name', 'artist_name',
           'added_at', 'duration_ms', 'explicit', 'popularity', 'track_id',
           'playlist_id', 'album_id', 'artist_id']

# Initialise data frame
my_data = pd.DataFrame(columns=columns)

# Populate the data frame
for playlist in user.playlists:
    for track in playlist.tracks:
        for artist in track.artists:
            df = pd.DataFrame([[
                track.name,
                playlist.name,
                track.album['name'],
                artist['name'],
                track.added_at,
                track.duration_ms,
                track.explicit,
                track.popularity,
                track.id,
                playlist.id,
                track.album['id'],
                artist['id']
            ]],
                columns=columns)
            my_data = my_data.append(df, ignore_index=True)

# Write data frame to a CSV file for analysis
my_data.to_csv('./data.csv')
