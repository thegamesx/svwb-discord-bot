import os
import urllib.request
import requests


api_url = "https://shadowverse-wb.com/web/CardList/cardList"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Lang": "en",
    "Connection": "keep-alive",
    "Referer": "https://shadowverse-wb.com/en/deck/cardslist",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}


# Devuelve una imagen de una carta. Ver si es necesario descargarla
def get_image(card_hash):
    localPath = 'files/' + card_hash + ".png"
    if not os.path.exists("files/"):
        os.makedirs("files/")
    if not os.path.isfile(localPath):
        urllib.request.urlretrieve(f"https://shadowverse-wb.com/uploads/card_image/eng/card/{card_hash}.png", localPath)
    return localPath


# Llama a la API oficial, y devuelve un json con los datos.
def call_api(params):
    response = requests.get(api_url, headers=headers, params=params)
    if response.ok:
        return response.json()
    else:
        return {"status_code": response.status_code, "error": f"Error: {response.text}"}
