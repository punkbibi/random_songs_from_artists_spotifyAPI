import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import random
import os
import sqlite3

conn = sqlite3.connect('spotify.db')
cursor = conn.cursor()

# create a table to store the songs if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS songs
                (name TEXT, artist TEXT, url TEXT)''')


# Load the environment variables
load_dotenv()
client_id = os.getenv("Client_ID")
client_secret = os.getenv("Client_secret")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_all_tracks(query, search_type='track', limit=50):
    offset = 0
    filtered_tracks = []

    while True:
        # search for the tracks
        results = sp.search(q=query, type=search_type, limit=limit, offset=offset)
        
        # get the tracks and the total number of tracks
        tracks = results['tracks']['items']
        total_tracks = results['tracks']['total']

        # loop through the tracks and filter the tracks based on the query
        for track in tracks:
            for artist in track['artists']: # loop through the artists of the track
                if query.lower() in artist['name'].lower():
                    filtered_tracks.append(track)
                    break # break the loop if the artist is found
                
    
        offset += limit
        if offset >= total_tracks:
            break
        
    return filtered_tracks


def get_random_song(tracks):
    if not tracks:
        return None
    
    random_track = random.choice(tracks)
    # return the name, artist and the url of the random track in a dictionary
    return {
        'name': random_track['name'],
        'artist': random_track['artists'][0]['name'],
        'url': random_track['external_urls']['spotify']
    }

def main():
    while True:
        #TODO: add a function to search with genre
        
        query = input("Enter a artist: ")
        
        tracks = get_all_tracks(query)
        song = get_random_song(tracks)
        
        existing_songs = cursor.execute("SELECT name, artist FROM songs").fetchall()
        
        print(f"Number of songs found: {len(tracks)}")    

        # check if the song is already in the database
        if (song['name'], song['artist']) in existing_songs:
            print("This song has already been added to the database.")
            continue
        
        elif song:
            print(f"Random Song: {song['name']} by {song['artist']}")
            print(f"Listen here: {song['url']}")
            
            # add the song to the database
            cursor.execute("INSERT INTO songs VALUES (?, ?, ?)", (song['name'], song['artist'], song['url']))
            conn.commit()
            
            print("Song added to the database.")
            break
        else:
            print("No songs found for the given query.")
            break


if __name__ == "__main__":
    main()
    cursor.close()
    conn.close()
