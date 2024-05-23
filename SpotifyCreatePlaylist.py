import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import random
import tkinter as tk

CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
#your own
SCOPE = 'playlist-modify-private user-top-read'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

class GradientShift(tk.Canvas):
    WIDTH = 2000
    HEIGHT = 2000
    RECT_WIDTH = 10  

    def __init__(self, master=None, **kwargs):
        super().__init__(master, width=GradientShift.WIDTH, height=GradientShift.HEIGHT, **kwargs)
        self.grid()  

        self.draw_gradient()
        self.bind("<Button-1>", self.draw_new_gradient)  

    def draw_gradient(self):
        choice = random.randint(0, 9)
        
        c1 = random.randint(0, 255)
        c2 = random.randint(0, 255)
        c3 = random.randint(0, 255)

        for x in range(GradientShift.WIDTH // GradientShift.RECT_WIDTH): 
            if choice == 0:
                color = f'#{max(0, c1 - (x // (GradientShift.WIDTH // GradientShift.RECT_WIDTH))):02x}{min(255, c2 + x):02x}{min(255, c3 + (x // 4)):02x}'
            elif choice == 1:
                color = f'#{c1:02x}{min(255, c2 + x):02x}{c3:02x}'
            elif choice == 2:
                color = f'#{min(255, c3 + (x // 4)):02x}{min(255, c2 + x):02x}{25:02x}'
            elif choice == 3:
                color = f'#{min(255, x + (c1 // 8)):02x}{min(255, c2 + (c3 // 2)):02x}{min(255, c3 + c2):02x}'
            elif choice == 4:
                color = f'#{max(0, 201 - x):02x}{min(255, c2 + x):02x}{min(255, c3 + (x // 5)):02x}'
            elif choice == 5:
                color = f'#{min(255, (c1 // 4) + 150):02x}{min(255, c2 + x):02x}{min(255, c3 + (x // 4)):02x}'
            elif choice == 6:
                color = f'#{max(0, 252 - x):02x}{min(255, c2 + c3):02x}{min(255, c2 + (2 * x // 3)):02x}'
            elif choice == 7:
                color = f'#{max(0, 74 - (x // 4)):02x}{min(255, c2 + x):02x}{min(255, c3 + 1 + (x // 4)):02x}'
            elif choice == 8:
                color = f'#{min(255, (x // 7) + x):02x}{min(255, c2 + x):02x}{min(255, c3 + (x // 4)):02x}'
            else:
                color = f'#00{max(0, 231 - x):02x}{min(255, 5 * (c3 // 8) + 50):02x}'

            self.create_rectangle(GradientShift.RECT_WIDTH * x, 0, GradientShift.RECT_WIDTH * (x + 1), GradientShift.HEIGHT, fill=color, outline='')

    def draw_new_gradient(self, event):
        self.delete("all")  
        self.draw_gradient()  

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

def createPlaylistWithGenreTracks(genreTracks):
    maxGenre = max(genreTracks, key=lambda x: len(genreTracks[x]))
    maxGenreTracks = genreTracks[maxGenre]

    playlistName = f"Top Tracks - {maxGenre}"
    playlistDescription = f"Playlist generated based on user's top tracks in the genre {maxGenre}"

    try:
        playlist = sp.user_playlist_create(sp.me()['id'], playlistName, public=False, description=playlistDescription)
        trackURIs = [track['uri'] for track in maxGenreTracks]
        sp.playlist_add_items(playlist['id'], trackURIs)
        return playlist
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None

def setPlaylistImage(playlistId):
    root = tk.Tk()
    app = GradientShift(master=root)
    app.update()  # Update the GUI to ensure the canvas is drawn
    app.postscript(file="playlist_image.ps", colormode='color')
    root.destroy()

    try:
        with open("playlist_image.ps", "rb") as imageFile:
            image = imageFile.read()
        sp.playlist_upload_cover_image(playlistId, image)
    except Exception as e:
        print(f"Error setting playlist image: {e}")

def main():
    topTracks = fetchTopTracks()
    if not topTracks:
        print("No top tracks found.")
        return

    artistIds = list(set(artist['id'] for track in topTracks for artist in track['artists'])) 
    artistGenres = fetchArtistGenres(artistIds)
    print("Artist genres fetched:")
    for artistId, genres in artistGenres.items():
        print(f"Artist ID: {artistId}, Genres: {genres}")

    groupedTracks = groupTracksByGenre(topTracks, artistGenres)
    print("Top 40 Tracks Grouped by Genre:")
    for genre, tracks in groupedTracks.items():
        print(f"\nGenre: {genre}, Number of Tracks: {len(tracks)}")

    playlist = createPlaylistWithGenreTracks(groupedTracks)
    if playlist:
        print(f"Playlist created: {playlist['external_urls']['spotify']}")
        setPlaylistImage(playlist['id'])
        print("Playlist image set successfully.")
    else:
        print("Failed to create playlist.")

if __name__ == "__main__":
    main()
