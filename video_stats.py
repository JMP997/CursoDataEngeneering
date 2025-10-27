import requests
import json
import os
# Esto sirve para securizar (la clave API no debe estár en el código, la extraemos de un archivo llamado .env)
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
# Primero necesitaremos una URL correspondiente al canal de youtube al que vamos a acceder

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

# Funcion que estrae la ID de playlist de un canal de youtube a traves de un JSON
def getPlaylistid():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # print(json.dumps(data, indent= 4))

        # Lo que estamos haciendo ahora es acceder a la playlist del canal mediante la clave del json que hemos obtenido desde la API
        channel_items = data["items"][0]
        channel_playlistID = channel_items["contentDetails"]["relatedPlaylists"]['uploads']
        #print (channel_playlistID);

        return channel_playlistID
    except requests.exceptions.RequestException as e:
        raise e    

# Esta función va a coger cada ID correspondiente a un video y la va a almacenar en una lista
def getVideoIds(playlistId):
    videoID = []
    pageToken = None
    baseURL = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"
# Mientras que la condición sea cuerta a la URL base se le va a añadir el pageToken
    try:
        while True:
            url = baseURL
            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                videoID.append(video_id)

            pageToken = data.get('nextPageToken')

            with open("videoIds.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            if not pageToken:
                break

        return videoID
        
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlistId = getPlaylistid()
    print(getVideoIds(playlistId))