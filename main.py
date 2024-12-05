import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import random
import os

load_dotenv()
client_id = os.getenv("Client_ID")
client_secret = os.getenv("Client_secret")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_all_tracks(query, search_type='track', limit=50):
    offset = 0
    filtered_tracks = []

    while True:
        results = sp.search(q=query, type=search_type, limit=limit, offset=offset)
        tracks = results['tracks']['items']
        total_tracks = results['tracks']['total']

        for track in tracks:
            for artist in track['artists']:
                if query.lower() in artist['name'].lower():
                    filtered_tracks.append(track)
                    break

        offset += limit
        if offset >= total_tracks:
            break
    return filtered_tracks

def get_random_song(tracks):
    if not tracks:
        return None
    random_track = random.choice(tracks)
    return {
        'name': random_track['name'],
        'artist': random_track['artists'][0]['name'],
        'url': random_track['external_urls']['spotify']
    }

def main():
    query = input("Enter a genre or artist: ")
    tracks = get_all_tracks(query)
    print(f"Number of songs found: {len(tracks)}")    
    song = get_random_song(tracks)
    if song:
        print(f"Random Song: {song['name']} by {song['artist']}")
        print(f"Listen here: {song['url']}")
    else:
        print("No songs found for the given query.")

if __name__ == "__main__":
    main()