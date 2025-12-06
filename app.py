import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

# Spotify API credentials - replace with your own
CLIENT_ID = 'f08303c2ccff4d9d9da856a895ad4eaf'
CLIENT_SECRET = '9e5dc694788648669cb7cefad428b0cc'

# Mood to audio features mapping
MOOD_FEATURES = {
    'happy': {'valence': (0.6, 1.0), 'energy': (0.5, 1.0), 'tempo': (100, 180)},
    'sad': {'valence': (0.0, 0.4), 'energy': (0.0, 0.5), 'tempo': (60, 100)},
    'energetic': {'valence': (0.5, 1.0), 'energy': (0.7, 1.0), 'tempo': (120, 200)},
    'chill': {'valence': (0.3, 0.7), 'energy': (0.0, 0.4), 'tempo': (60, 110)},
    'romantic': {'valence': (0.4, 0.8), 'energy': (0.2, 0.6), 'tempo': (70, 120)},
    'angry': {'valence': (0.0, 0.4), 'energy': (0.7, 1.0), 'tempo': (120, 180)}
}

def authenticate_spotify():
    """Authenticate with Spotify API using Client Credentials"""
    auth_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def search_tracks_by_genre_and_mood(sp, genre, mood, limit=50):
    """Search for tracks by genre"""
    if mood not in MOOD_FEATURES:
        print(f"Mood '{mood}' not recognized. Using 'happy' as default.")
        mood = 'happy'
    
    # Try multiple search strategies
    tracks = []
    
    # Strategy 1: Search by genre only (most reliable)
    try:
        results = sp.search(q=f"genre:{genre}", type='track', limit=limit)
        tracks = results['tracks']['items']
    except:
        pass
    
    # Strategy 2: If no results, try without "genre:" prefix
    if not tracks:
        try:
            results = sp.search(q=genre, type='track', limit=limit)
            tracks = results['tracks']['items']
        except:
            pass
    
    # Strategy 3: Try with year to get more varied results
    if not tracks:
        try:
            results = sp.search(q=f"{genre} year:2020-2024", type='track', limit=limit)
            tracks = results['tracks']['items']
        except:
            pass
    
    return tracks

def get_track_info(track):
    """Extract and format track information"""
    name = track['name']
    artists = ", ".join([artist['name'] for artist in track['artists']])
    album = track['album']['name']
    url = track['external_urls']['spotify']
    duration_ms = track['duration_ms']
    duration_min = duration_ms // 60000
    duration_sec = (duration_ms % 60000) // 1000
    
    return {
        'name': name,
        'artists': artists,
        'album': album,
        'url': url,
        'duration': f"{duration_min}:{duration_sec:02d}"
    }

def print_playlist(tracks, genre, mood):
    """Print the playlist in a nice format"""
    print("\n" + "="*80)
    print(f"🎵  {mood.upper()} {genre.upper()} PLAYLIST  🎵".center(80))
    print("="*80)
    print(f"\nFound {len(tracks)} tracks:\n")
    
    for i, track in enumerate(tracks, 1):
        info = get_track_info(track)
        print(f"{i}. {info['name']}")
        print(f"   Artist(s): {info['artists']}")
        print(f"   Album: {info['album']}")
        print(f"   Duration: {info['duration']}")
        print(f"   Listen: {info['url']}")
        print()
    
    print("="*80)
    
    # Export to text file option
    export = input("\nWould you like to export this playlist to a text file? (y/n): ").strip().lower()
    if export == 'y':
        filename = f"{mood}_{genre}_playlist.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{mood.upper()} {genre.upper()} PLAYLIST\n")
            f.write("="*80 + "\n\n")
            for i, track in enumerate(tracks, 1):
                info = get_track_info(track)
                f.write(f"{i}. {info['name']}\n")
                f.write(f"   Artist(s): {info['artists']}\n")
                f.write(f"   Album: {info['album']}\n")
                f.write(f"   Duration: {info['duration']}\n")
                f.write(f"   Listen: {info['url']}\n\n")
        print(f"✓ Playlist exported to {filename}")

def main():
    print("=== Spotify Mood & Genre Track Finder ===\n")
    
    # Get user input
    genre = input("Enter genre (e.g., pop, rock, jazz, electronic): ").strip().lower()
    mood = input("Enter mood (happy, sad, energetic, chill, romantic, angry): ").strip().lower()
    num_tracks = int(input("How many tracks? (recommended: 10-30): "))
    
    print("\nAuthenticating with Spotify...")
    sp = authenticate_spotify()
    
    print(f"Searching for {mood} {genre} tracks...")
    tracks = search_tracks_by_genre_and_mood(sp, genre, mood, limit=50)
    
    if not tracks:
        print(f"No tracks found. Try a different genre like: pop, hip-hop, indie, electronic, jazz")
        return
    
    # Shuffle for variety
    random.shuffle(tracks)
    
    # Limit to requested number
    if len(tracks) > num_tracks:
        tracks = tracks[:num_tracks]
    
    # Print the playlist
    print_playlist(tracks, genre, mood)

if __name__ == "__main__":
    main()