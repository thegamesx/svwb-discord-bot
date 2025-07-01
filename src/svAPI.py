import os
import urllib.request
from urllib.parse import urlparse
import requests

news_api_url = "https://shadowverse-wb.com/web/Information"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Lang": "en",
    "Connection": "keep-alive",
    "Referer": "https://shadowverse-wb.com/en/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}


def get_news_image(img_url):
    if img_url:
        if not os.path.exists("temp/"):
            os.makedirs("temp/")
        image_path = f"temp/{os.path.basename(urlparse(img_url).path)}"
        urllib.request.urlretrieve(img_url, image_path)
    else:
        image_path = "files/news_banner_empty.png"
    return image_path


def get_image(card_hash):
    localPath = 'temp/' + card_hash + ".png"
    if not os.path.exists("temp/"):
        os.makedirs("temp/")
    if not os.path.isfile(localPath):
        urllib.request.urlretrieve(f"https://shadowverse-wb.com/uploads/card_image/eng/card/{card_hash}.png", localPath)
    return localPath


def get_new_by_id(news_id):
    response = requests.get(f"{news_api_url}/detail?id={news_id}", headers=headers)
    if response.ok:
        return response.json()
    else:
        return {"status_code": response.status_code, "error": f"Error: {response.text}"}


def get_news():
    response = requests.get(news_api_url, headers=headers)
    if response.ok:
        return response.json()
    else:
        return {"status_code": response.status_code, "error": f"Error: {response.text}"}
