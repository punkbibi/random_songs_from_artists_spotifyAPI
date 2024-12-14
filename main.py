from flask import Flask, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import random
import os
import sqlite3

app = Flask(__name__)

# Load the environment variables
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
                    filtered_tracks.append({
                        'name': track['name'],
                        'artist': artist['name'],
                        'url': track['external_urls']['spotify']
                    })
                    break

        offset += limit
        if offset >= total_tracks:
            break
    return filtered_tracks

def get_random_song(tracks):
    if not tracks:
        return None
    return random.choice(tracks)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    tracks = get_all_tracks(query)
    if not tracks:
        return render_template('results.html', message="No songs found for the given query.")

    song = get_random_song(tracks)

    conn = sqlite3.connect('spotify.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS songs
                    (name TEXT, artist TEXT, url TEXT)''')

    existing_songs = cursor.execute("SELECT name, artist FROM songs").fetchall()
    if (song['name'], song['artist']) in existing_songs:
        cursor.close()
        conn.close()
        return render_template('results.html', message="This song has already been added to the database.", song=song)

    cursor.execute("INSERT INTO songs VALUES (?, ?, ?)", (song['name'], song['artist'], song['url']))
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('results.html', message="Song added to the database.", song=song)

if __name__ == "__main__":
    app.run()