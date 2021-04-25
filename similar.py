import spotipy
from spotipy.oauth2 import SpotifyOAuth
import constants
import spotipy.util as util
import json
import os
from os import path
import time
import random
from similar import similar
from valence import valence

def similar(trackids, sp):
    
    # features = most similar grouped together
    features = sp.audio_features(trackids) 

    # large value of mainSum to compare to 
    mainSum = 10000

    # first 2 most similar by comparing each track with the other ones
    for i in range(0, len(features) - 1):
        for j in range(i + 1, len(features)):
            differences = {x: features[j][x] - features[i][x] for x in ['instrumentalness', 'acousticness', 'liveness', 'speechiness',
                'energy', 'danceability', 'valence']}
            # the smaller the sum of the differences, the more similar they are
            sum = 0
            for x in differences:
                differences[x] = round(abs(differences[x]), 4)
                sum = sum + differences[x]
            sum = round(sum, 4)
            if(sum < mainSum):
                mainSum = sum 
                indices = [i, j]
            
    # make a sort array and add the 2 track objects to it, deleting from features
    sort=[]
    for x in range(0, len(indices)):
        sort.append(features[indices[x] - x])
        del (features[indices[x] - x])

    # compare last sorted element with each in features
    while(len(features) > 1):
        lastElementSort = sort[len(sort) - 1]
        mainSum = 10000
        for i in range(0, len(features)):
            differences = {x: lastElementSort[x] - features[i][x] for x in ['instrumentalness', 'acousticness', 'liveness', 'speechiness',
            'energy', 'danceability', 'valence']}
            sum = 0
            for x in differences:
                differences[x] = round(abs(differences[x]), 4)
                sum = sum + differences[x]
            sum = round(sum, 4)
            if(sum < mainSum):
                mainSum = sum 
                indices = [i]
        sort.append(features[indices[0]])
        del features[indices[0]]
        
    sort.append(features[0])
    del features[0]

    # delete playlists with the same name
    playlist_name = 'SAMESIES'
    playlists = sp.user_playlists(constants.SPOTIFY_USERNAME)['items']
    for x in playlists:
        if x['name'] == playlist_name:
            sp.user_playlist_unfollow(constants.SPOTIFY_USERNAME, x['id'])

    # make a playlist and add tracks to it
    sp.user_playlist_create(constants.SPOTIFY_USERNAME, name=playlist_name)
    PLAYLIST_ID = sp.user_playlists(constants.SPOTIFY_USERNAME)['items'][0]['id']
    for x in sort:
        tid = [x['uri']]
        sp.user_playlist_add_tracks(constants.SPOTIFY_USERNAME, PLAYLIST_ID, tid)

    print('similar playlist made')