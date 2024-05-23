import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import scrolledtext

CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
#your own stuff here 
SCOPE = 'playlist-modify-private user-top-read'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

def fetchTopTracks(limit=40, timeRange='long_term'):
    try:
        results = sp.current_user_top_tracks(limit=limit, time_range=timeRange)
        return results['items']
    except Exception as e:
        print(f"Error fetching top tracks: {e}")
        return []

def fetchArtistGenres(artistIds):
    try:
        artists = sp.artists(artistIds)
        artistGenres = {artist['id']: artist['genres'] for artist in artists['artists']}
        return artistGenres
    except Exception as e:
        print(f"Error fetching artist genres: {e}")
        return {}

def groupTracksByGenre(tracks, artistGenres):
    genreTracks = {}
    for track in tracks:
        trackGenres = set()
        for artist in track['artists']:
            trackGenres.update(artistGenres.get(artist['id'], []))
        for genre in trackGenres:
            if genre not in genreTracks:
                genreTracks[genre] = []
            genreTracks[genre].append(track)
    return genreTracks

def fetchTrackFeatures(trackId):
    try:
        meta = sp.track(trackId)
        features = sp.audio_features(trackId)[0]
        return {
            'name': meta['name'],
            'album': meta['album']['name'],
            'artist': meta['album']['artists'][0]['name'],
            'releaseDate': meta['album']['release_date'],
            'length': meta['duration_ms'],
            'popularity': meta['popularity'],
            'acousticness': features['acousticness'],
            'danceability': features['danceability'],
            'energy': features['energy'],
            'instrumentalness': features['instrumentalness'],
            'liveness': features['liveness'],
            'loudness': features['loudness'],
            'speechiness': features['speechiness'],
            'tempo': features['tempo'],
            'timeSignature': features['time_signature'],
            'key': features['key']
        }
    except Exception as e:
        print(f"Error fetching track features: {e}")
        return {}

def displayTopTracks():
    topTracks = fetchTopTracks()
    if not topTracks:
        displayText("No top tracks found.")
        return
    
    topTracksInfo = "\n".join([f"{track['name']} by {', '.join([artist['name'] for artist in track['artists']])}" for track in topTracks])
    displayText(f"Top Tracks:\n\n{topTracksInfo}")

def displayGroupedTracks():
    topTracks = fetchTopTracks()
    if not topTracks:
        displayText("No top tracks found.")
        return

    artistIds = list(set(artist['id'] for track in topTracks for artist in track['artists']))
    artistGenres = fetchArtistGenres(artistIds)

    groupedTracks = groupTracksByGenre(topTracks, artistGenres)
    groupedTracksInfo = ""
    for genre, tracks in groupedTracks.items():
        groupedTracksInfo += f"\nGenre: {genre}\n"
        for track in tracks:
            groupedTracksInfo += f"  {track['name']} by {', '.join([artist['name'] for artist in track['artists']])}\n"

    displayText(f"Grouped Tracks by Genre:\n\n{groupedTracksInfo}")

def displayTrackPairs():
    topTracks = fetchTopTracks()
    if not topTracks:
        displayText("No top tracks found.")
        return

    topTrackIds = [track['id'] for track in topTracks]
    trackFeatures = [fetchTrackFeatures(trackId) for trackId in topTrackIds]
    tempos = [track['tempo'] for track in trackFeatures]
    names = [track['name'] for track in trackFeatures]
    keys = [track['key'] for track in trackFeatures]

    pairs = {
        'Tier One': {},
        'Tier Two': {},
        'Tier Three': {},
        'Tier Four': {},
        'Tier Five': {}
    }

    for i, nameI in enumerate(names):
        for j, nameJ in enumerate(names):
            if i != j:
                pair = tuple(sorted((nameI, nameJ)))
                if pair in pairs['Tier One'] or pair in pairs['Tier Two'] or pair in pairs['Tier Three'] or pair in pairs['Tier Four'] or pair in pairs['Tier Five']:
                    continue

                tempo_diff = abs(tempos[i] - tempos[j])
                key_diff = abs(keys[i] - keys[j])
                key_cycle_diff = min(abs(keys[i] - (keys[j] + 12)), abs((keys[i] + 12) - keys[j]))

                if tempo_diff <= 3.1:
                    if keys[i] == keys[j]:
                        pairs['Tier One'][pair] = "Same key"
                    elif key_diff == 5 or key_cycle_diff == 5:
                        pairs['Tier Two'][pair] = "Key difference of 5"
                    elif key_diff <= 2:
                        pairs['Tier Three'][pair] = "Key difference of 2 or less"
                    elif key_diff <= 4:
                        pairs['Tier Four'][pair] = "Key difference of 4 or less"
                    else:
                        pairs['Tier Five'][pair] = "Other"

    pairsInfo = ""
    for tier, pairDict in pairs.items():
        pairsInfo += f"\n{tier} Pairs:\n"
        for pair, reason in pairDict.items():
            pairsInfo += f"{pair[0]} - {pair[1]} ({reason})\n"

    displayText(f"Track Feature Pairs:\n\n{pairsInfo}")

def displayText(text):
    text_area.config(state=tk.NORMAL)
    text_area.delete('1.0', tk.END)
    text_area.insert(tk.INSERT, text)
    text_area.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Spotify Data Analysis")

btnTopTracks = tk.Button(root, text="Display Top Tracks", command=displayTopTracks)
btnTopTracks.pack()

btnGroupedTracks = tk.Button(root, text="Display Grouped Tracks", command=displayGroupedTracks)
btnGroupedTracks.pack()

btnTrackPairs = tk.Button(root, text="Display Track Pairs", command=displayTrackPairs)
btnTrackPairs.pack()

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30, state=tk.DISABLED)
text_area.pack()

root.mainloop()
