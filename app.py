from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

app = Flask(__name__)


#secret is a random string that will be used to sign the session cookie.
app.secret_key= "Vaxo272002"
app.config['SESSION_COOKIE_NAME'] = 'Miks Cookie'
TOKEN_INFO = "token_info"

#endpoints/routes
@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)



@app.route('/redirect')
def redirectPage():
     
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info   
    return redirect(url_for('save_Discover_Weekly', _external = True)) or redirect(url_for('getTracks', _external = True))



@app.route('/redirectSaveDiscover')
def redirectsaveDiscover():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info        
    return redirect(url_for('save_Discover_Weekly', _external = True)) 



@app.route('/saveDiscoverWeekly')
def save_Discover_Weekly():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')
    
    sp = spotipy.Spotify(auth= token_info['access_token'])
    user_id = sp.current_user()['id']
    saved_weekly_playlist_id = None
    discover_weekly_playlist_id = None
    current_playlists = sp.current_user_playlists()['items']

    for playlist in current_playlists:
        if(playlist['name'] == "Discover Weekly"):
            discover_weekly_playlist_id = playlist['id']
        if(playlist['name'] == "Saved Weekly"):
            saved_weekly_playlist_id = playlist['id']

    if not discover_weekly_playlist_id:
        return 'Discover Weekly not found'
    
    if not saved_weekly_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, "Saved Weekly",True)
        saved_weekly_playlist_id = new_playlist['id']

    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
    song_uris = []
    for song in discover_weekly_playlist['items']:
        song_uri = song['track']['uri']
        song_uris.append(song_uri)
    user_id = sp.current_user()['id']
    sp.user_playlist_add_tracks(user_id, saved_weekly_playlist_id, song_uris, None)
    return ("SUCCESS!!!")


@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect('/')
    sp = spotipy.Spotify(auth= token_info['access_token'])
    all_songs = []
    iter = 0
    while True:
        items = sp.current_user_saved_tracks(limit= 50, offset= iter * 50)['items']
        iter += 1
        all_songs += items
        if (len(items) < 50):
            break
    return str(len(all_songs))




def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external = False))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info




def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "___",
        client_secret = "___",
        redirect_uri = url_for('redirectPage', _external = True),
        scope = "user-library-read playlist-modify-public playlist-modify-private")

app.run(debug=True)