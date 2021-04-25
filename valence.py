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

def valence(trackids, sp):

    features = sp.audio_features(trackids) 

    # swap until features has ascending valence
    for i in range(0, len(features) - 1):
        smallest = [i, features[i]['valence']]
        for j in range(i, len(features)):
            if (features[j]['valence'] < smallest[1] ):
                smallest =  [j, features[j]['valence']]
        features[i], features[smallest[0]] = features[smallest[0]], features[i]


    # delete playlists with the same name
    playlist_name = 'VAL'
    playlists = sp.user_playlists(constants.SPOTIFY_USERNAME)['items']
    for x in playlists:
        if x['name'] == playlist_name:
            sp.user_playlist_unfollow(constants.SPOTIFY_USERNAME, x['id'])

    # make a playlist and add ascending valence tracks to it
    sp.user_playlist_create(constants.SPOTIFY_USERNAME, name=playlist_name)
    PLAYLIST_ID = sp.user_playlists(constants.SPOTIFY_USERNAME)['items'][0]['id']
    for i in features:
        uri = [i['uri']]
        sp.user_playlist_add_tracks(constants.SPOTIFY_USERNAME, PLAYLIST_ID, uri)


    print('valence playlist made, waiting for mood...')
    while(True):
        # random songs for each mood
        numSongsSection = int(len(features) / 3 )
        randomInteger = random.randint(0, numSongsSection - 1) 
        sadUri = features[randomInteger]['uri']
        neutralUri = features[randomInteger + numSongsSection]['uri']
        happyUri = features[randomInteger + (2 * numSongsSection)]['uri']
        uri = ''
        playSong = False
        type = 'neutral'
        if(path.exists('happy')):
            type = 'happy'
            playSong = True
            os.remove("happy")
        if(path.exists('sad')):
            type='sad'
            playSong = True
            os.remove("sad")
        if(path.exists('neutral')):
            type='neutral'
            playSong = True
            os.remove("neutral")
        if(playSong):
            playSong = False
            devices = sp.devices()
            print(json.dumps(devices, sort_keys=True, indent=4))
            deviceID = devices['devices'][0]['id']        
            if(type=='happy'):
                uri=happyUri
            if(type=='sad'):
                uri=sadUri
            if(type=='neutral'):
                uri=neutralUri
            sp.start_playback(deviceID, None, [uri])
        time.sleep(0.2)