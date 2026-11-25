# SpotifyPython

A local Python app (spotipy and Tkinter) that reads your Spotify top tracks, groups them by artist genre, and pairs songs by tempo and key. `SpotifyAPI.py` is the analyzer; `SpotifyCreatePlaylist.py` creates playlists.

## System design

How a request or a run moves through the code, then the choices behind that shape. In the decision charts, a **solid** box is the route this repo takes and a **dashed** box is the alternative it turns down; the edge label is the tradeoff.

### Top tracks to pairs

SpotifyAPI.py uses spotipy. The scopes in the file are playlist-modify-private and user-top-read . Forty long-term top tracks are grouped by the union of their artists’ genres. Pairs inside a 3.1 tempo band are tiered by key distance.

```mermaid
flowchart TD
  classDef chosen fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
  oauth["spotipy OAuth"]
  top["40 long-term top tracks"]
  genre["Union of artist genres"]
  feats["Audio features"]
  pairs["Tempo within 3.1, then key tiers"]
  oauth --> top --> genre
  top --> feats --> pairs
  class oauth,top,genre,feats,pairs chosen
```

### Tempo and key

Energy and danceability are fetched and then ignored by the pairing. The tiers use tempo and key only. Client id and secret are empty strings in the file. You fill them in locally.

```mermaid
flowchart TD
  classDef chosen fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
  classDef rejected fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,stroke-dasharray:5 5,color:#616161
  q{Which songs sit together}
  q -->|"tempo band, then distance on the circle of fifths"| key["Five key tiers"]
  q -->|"energy and danceability"| other["Features the pairing ignores"]
  class key chosen
  class other rejected
```

Longer write-up: [aamogh.vercel.app/projects/music-analyzer](https://aamogh.vercel.app/projects/music-analyzer.html)
