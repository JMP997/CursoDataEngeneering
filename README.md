# CursoDataEngeneering — video_stats.py

Este README documenta el archivo `video_stats.py` tal como está en el repositorio. Está orientado a un entregable de un curso de Ingeniería de Datos: explica el propósito general, dependencias, uso y describe cada función paso a paso según el código actual (incluye notas sobre limitaciones y comportamientos observables).

## Resumen general
Propósito: extraer metadatos de los vídeos subidos por un canal de YouTube (identificado por su handle) y guardar los resultados en un JSON local.

Flujo principal:
1. Leer API key desde `.env`.
2. Obtener el ID de la playlist de "uploads" del canal.
3. Recorrer la playlist para reunir todos los `videoId`.
4. Consultar el endpoint `videos` en *batches* y construir una lista con metadatos.
5. Guardar la lista final en `./data/data{YYYY-MM-DD}.json`.

Valores por defecto en el código:
- `CHANNEL_HANDLE = "MrBeast"`
- `maxResults = 50` (tamaño de página / batch)
- `API_KEY` se lee desde `.env` con `load_dotenv`

## Requisitos
- Python 3.x
- Paquetes: `requests`, `python-dotenv`
  - Instalación: `pip install requests python-dotenv`
- Fichero `.env` en la raíz del proyecto con la variable `API_KEY=TU_API_KEY`
- Carpeta `./data` debe existir antes de ejecutar (el código no la crea actualmente)

## Cómo ejecutar
Desde la ruta del proyecto:
```
python3 /home/mpjesus/CursoDataEngeneering/video_stats.py
```
Salida: un fichero JSON en `./data/data{YYYY-MM-DD}.json` con la lista de diccionarios por vídeo.

---

## Documentación por función (paso a paso)

### getPlaylistid()
- Propósito: obtener el `playlistId` de las subidas del canal (uploads).
- Entrada: ninguna (usa `CHANNEL_HANDLE` y `API_KEY` globales).
- Pasos:
  1. Construye la URL del endpoint `channels` con `part=contentDetails` y `forHandle={CHANNEL_HANDLE}`.
  2. Llama a la API con `requests.get`.
  3. Lanza excepción si la respuesta HTTP no es 2xx (`response.raise_for_status()`).
  4. Parsea JSON y extrae `data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]`.
  5. Devuelve `channel_playlistID`.
- Observaciones: el código asume `items[0]` existe; si el handle no existe falla con KeyError/IndexError.

### getVideoIds(playlistId)
- Propósito: recorrer la playlist y devolver una lista de todos los `videoId`.
- Entrada: `playlistId` (string).
- Pasos:
  1. Inicializa `videoID = []`, `pageToken = None`.
  2. Construye `baseURL` para `playlistItems` con `part=contentDetails` y `maxResults`.
  3. En bucle:
     - Añade `&pageToken={pageToken}` si existe.
     - Llama a la API y valida la respuesta.
     - Recorre `data.get('items', [])` y extrae `item['contentDetails']['videoId']`, añadiéndolo a `videoID`.
     - Actualiza `pageToken = data.get('nextPageToken')` y termina cuando no hay token.
  4. Devuelve la lista acumulada `videoID`.
- Observaciones: usa acceso directo `item['contentDetails']['videoId']` — puede lanzar KeyError si la estructura no es la esperada.

### extract_video_data(videoID)
- Propósito: solicitar metadatos de vídeos por lotes y construir una lista de diccionarios con los campos relevantes.
- Entrada: `videoID` (lista de strings).
- Pasos:
  1. Define `extracted_data = []`.
  2. Define `batch_list` (generador) que corta la lista en trozos de `batch_size` usando índices.
  3. Para cada batch:
     - Construye `videoID_String = ",".join(batch)`.
     - Construye la URL para el endpoint `videos`.
       - En el código actual la URL se arma con parámetros repetidos: `?...part=contentDetails&part=snippet&part=statistics...`
       - Nota: la API de YouTube espera `part=contentDetails,snippet,statistics` (un único `part` con valores separados por comas).
     - Llama a la API y parsea JSON.
     - Por cada `item` en `data.get('items', [])`:
       * Extrae `id`, `snippet`, `contentDetails`, `statistics` desde el `item`.
       * Construye `video_data` con claves:
         - `"video_id"`: `item['id']`
         - `"tittle"`: `snippet['title']` (en el código actual aparece mal escrito como `tittle`)
         - `"publishedAt"`: `snippet['publishedAt']`
         - `"duration"`: `contentDetails['duration']`
         - `"viewCount"`: `statistics.get('viewCount', None)`
         - `"likeCount"`: `statistics.get('likecount', None)` (en el código actual usa `'likecount'` en minúscula — clave incorrecta)
         - `"commentCount"`: `statistics.get('commentCount', None)`
       * Añade `video_data` a `extracted_data`.
  4. Devuelve `extracted_data`.
- Observaciones y limitaciones (según el código actual):
  - La URL `part` está mal formada y puede causar retorno incompleto o errores.
  - Se usan accesos directos (`snippet['title']`, etc.) que pueden lanzar KeyError si falta algún campo; se mezclan con `.get()` en otros campos.
  - Errores tipográficos:
    - `"tittle"` en vez de `"title"` → título aparecerá con la clave incorrecta en la salida.
    - `'likecount'` (minúsculas) en vez de `'likeCount'` → likes pueden aparecer como `None`.
  - No hay manejo de reintentos ni backoff ante límites de cuota o 5xx.
  - El tamaño de batch `maxResults = 50` es apropiado (límite de la API).

### saveJson(extracted_data)
- Propósito: escribir la lista `extracted_data` en un JSON con la fecha actual en el nombre.
- Entrada: `extracted_data` (lista).
- Pasos:
  1. Construye `path = f"./data/data{date.today()}.json"`.
  2. Abre el archivo en modo escritura con `encoding="utf-8"`.
  3. Serializa con `json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)`.
- Observaciones:
  - El código asume que la carpeta `./data` existe; si no existe, la escritura fallará (FileNotFoundError).
  - Buen detalle: usa `ensure_ascii=False` para preservar caracteres Unicode.

---

## Notas finales (para el entregable del curso)
- El código es funcional en su estructura y refleja el flujo típico de extracción y persistencia en un pipeline de ingestión de datos desde una API.
- Antes de entrega o en una versión mejorada, conviene:
  - Corregir la construcción del parámetro `part` en `extract_video_data`.
  - Arreglar los typos (`tittle` → `title`, `'likecount'` → `'likeCount'`).
  - Usar `.get()` de forma consistente para evitar KeyError en respuestas incompletas.
  - Crear la carpeta `./data` si no existe (`os.makedirs("./data", exist_ok=True)`).
  - Añadir manejo de reintentos / backoff y logging para robustez.
  - Añadir tests unitarios que mockeen `requests` para validar comportamiento sin llamar la API real.

Si querés, puedo generar el bloque de Markdown listo para pegar en el README (o aplicarlo directamente) con menos/más detalle según prefieras.
