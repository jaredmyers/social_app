# simulated api driver
# since api was cut from this example

import json
import os
import mysql
import chat.credentials as cred

conn = mysql.connector.connect(
        host=cred.db_host,
        user=cred.db_user,
        password=cred.db_pw,
        database=cred.db_database
        )


def get_recommended_friends(sessionID):
    '''gets recommened friends from api based on mutually liked music'''

    # grab userID of current user based on session data
    query = "select userID from sessions where sessionID=%s;"
    val = (sessionID,)
    cursor = conn.cursor()
    cursor.execute(query, val)
    query_result = cursor.fetchall()
    userID = query_result[0][0]

    # grab all other users from database for potential match
    # this is done simply because this api is simulated
    # and needs valid usernames from db to simulate friend matches

    query = "select uname from users where userID not in (%s);"
    val = (userID,)
    cursor.execute(query, val)
    query_result = cursor.fetchall()

    matched_friends = []
    for tup in query_result:
        matched_friends.append(tup[0])

    return matched_friends


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
