import requests
import json
import os
# Esto sirve para securizar (la clave API no debe estár en el código, la extraemos de un archivo llamado .env)
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
# Primero necesitaremos una URL correspondiente al canal de youtube al que vamos a acceder

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"

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

        print (channel_playlistID);

        # return channel_playlistID
    except requests.exceptions.RequestException as e:
        raise e
    
if __name__ == "__main__":
    getPlaylistid()