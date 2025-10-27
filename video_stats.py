import requests
import json
import os
# Carga variables de entorno desde .env para no hardcodear la API key en el código
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
# Construimos la URL para consultar el canal por su handle (parámetro forHandle)

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

# Función que extrae el ID de la playlist de subidas (uploads) de un canal de YouTube a través de la respuesta JSON
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

# Recorre la playlist y almacena en una lista los IDs (videoId) de cada vídeo
def getVideoIds(playlistId):
    videoID = []
    pageToken = None
    baseURL = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"
# En cada iteración, si existe pageToken, lo añade como parámetro a la URL para paginar
    try:
        while True:
            # Esta función hace que si el siguiente pageToken del json es un valor no nulo lo añade a la url base
            url = baseURL
            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Recorremos data['items'] y extraemos contentDetails['videoId'] para añadirlo a la lista videoID
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                videoID.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

            #Guardamos un las ids en un JSON
            with open("videoIds.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        return videoID
        
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlistId = getPlaylistid()
    print(getVideoIds(playlistId))