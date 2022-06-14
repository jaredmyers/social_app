# simulated api driver
# since api was cut from this example

import json
from chat.send_to_db import send_to_db
from chat.send_to_api import send_to_api


def get_recommended_friends(sessionID):
    '''gets recommended friends from api based on mutually liked music'''

    # database portion

    message = {}
    message['type'] = 'get_recommended'
    message['sessionID'] = sessionID
    matched_friends = send_to_db(message, 'thread_chat_proc')

    return json.loads(matched_friends)


def get_recommended_details(sessionID, username):
    '''simulated api response since the api was cut from this sample'''
    '''this gets the details on which info the users were matched'''

    message = {}
    message['type'] = 'get_details'
    message['sessionID'] = sessionID
    message['username'] = username

    details = send_to_api(message, 'api_processing')

    obj = DisplayDetailsPage(
            details["tracks"],
            details["artists"],
            details["genres"],
            details["albums"],
            details["preview"]
            )

    return obj


class DisplayDetailsPage():

    def __init__(self, mutual_tracks, mutual_artists, mutual_genres, saved_albums, song_preview):
        self.mutual_tracks = mutual_tracks
        self.mutual_artists = mutual_artists
        self.mutual_genres = mutual_genres
        self.saved_albums = saved_albums
        self.preview = song_preview
