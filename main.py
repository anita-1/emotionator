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

# authenticate
authentication=SpotifyOAuth(scope=constants.SPOTIPY_SCOPE, client_id=constants.SPOTIPY_CLIENT_ID, 
    client_secret=constants.SPOTIPY_CLIENT_SECRET, redirect_uri=constants.SPOTIPY_REDIRECT_URI)
sp = spotipy.Spotify(auth_manager=authentication)

# playlist you want to sort
pl_id = constants.UNSORTED_PLAYLIST_ID
offset=0
response = sp.playlist_items(pl_id, offset=offset, fields='items.track.id,total', additional_types=['track'])
# track ids array to store all track ids
trackids=[]
for items in response['items']:
    trackids.append(items['track']['id'])

# makes playlist having 2 most similar songs, then each song following similar to previous
similar(trackids, sp)
# makes playlist with valence ascending
valence(trackids, sp)

