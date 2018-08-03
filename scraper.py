"""
A scraper for my Spotify account - extracts playlist data into SQL form
"""
from urllib.parse import urlencode
import psycopg2
import requests


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
        'scopes': scopes
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
    user = User(user_data)
    return user


class User:
    def __init__(self, user_data):
        self.user_data = user_data
        self.get_user_playlists()

    def __getattr__(self, item):
        return self.user_data[item]

    def get_user_playlists(self):
        user_id = self['id']
        print(user_id)


def main():
    """Executes the main code for scraping"""
    redirect_uri = 'http://localhost:3000/callback'
    client_id = input('What is your client ID? ')
    client_secret = input('What is your client secret? ')

    # Get the user's callback URL for further authentication
    scopes = 'user-library-read,playlist-read-private,user-top-read'
    callback_url = get_callback_url(client_id, redirect_uri, scopes)

    # Get the access code from the URL
    input_message = f'Please visit {callback_url} and paste the url here: '
    access_code_url = input(input_message)
    access_code = parse_access_code_url(access_code_url)

    # Get the user's access token for further API usage
    access_token = get_access_token(access_code, redirect_uri, client_id,
                                    client_secret)

    user = get_user(access_token)


if __name__ == '__main__':
    main()