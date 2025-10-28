import requests
import json
from datetime import date
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

        return videoID
        
    except requests.exceptions.RequestException as e:
        raise e

def extract_video_data(videoID):
    extracted_data = []
    def batch_list(video_id_list, batch_size):
        for video_id in range (0, len(video_id_list), batch_size):
            yield video_id_list[video_id: video_id + batch_size]    

    try:
        for batch in batch_list(videoID, maxResults):
            videoID_String = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={videoID_String}&key={API_KEY}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items',[]):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics  = item ['statistics']
                video_data = {
                    "video_id": video_id,
                    "title": snippet['title'],
                    "publishedAt": snippet['publishedAt'],
                    "duration": contentDetails['duration'],
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None)
                }
                extracted_data.append(video_data)
    
        return extracted_data
    
    except requests.exceptions.RequestException as e:
        raise e

def saveJson(extracted_data):
    path = f"./data/data{date.today()}.json"
    with open(path, "w", encoding= "utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent= 4, ensure_ascii=False)

if __name__ == "__main__":
    playlistId = getPlaylistid()
    video_ids = getVideoIds(playlistId)
    video_data = extract_video_data(video_ids)
    saveJson(video_data)