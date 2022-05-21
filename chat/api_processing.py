# simulated api driver
# since api was cut from this example


import json
import os

def get_recommended_friends(sessionID):

    print(os.getcwd())
    with open("chat/static/recommended_simulated_api.json", "r") as file:
        recommended_friends = json.load(file)

    return recommended_friends["recommended"]

def get_recommended_details(sessionID, username):
    '''simulated api response since the api was cut from this sample'''
    '''this gets the details on which info the users were matched'''

    with open("chat/static/details_simulated_api.json", "r") as file:
        details = json.load(file)

    obj = DisplayDetailsPage(details["tracks"], details["artists"], details["genres"], details["albums"], details["preview"])

    return obj


class DisplayDetailsPage():

    def __init__(self, mutual_tracks, mutual_artists, mutual_genres, saved_albums, song_preview):
        self.mutual_tracks = mutual_tracks
        self.mutual_artists = mutual_artists
        self.mutual_genres = mutual_genres
        self.saved_albums = saved_albums
        self.preview = song_preview
