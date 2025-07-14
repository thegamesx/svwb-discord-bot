import os
import urllib.request
from urllib.parse import urlparse
import aiohttp

# Configuración de la API

card_api_url = "https://shadowverse-wb.com/web/CardList"
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


# Se descarga la imagen para después enviarla, pero antes se fija si la había descargado antes.
# Por ahora no se borran los archivos descargados, pero se podría revisar si esto se vuelve un problema.
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


async def get_new_by_id(news_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{news_api_url}/detail?id={news_id}", headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return {"status_code": response.status, "error": f"Error: {await response.text()}"}


async def get_news():
    async with aiohttp.ClientSession() as session:
        async with session.get(news_api_url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return {"status_code": response.status, "error": f"Error: {await response.text()}"}


async def search_card(params):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{card_api_url}/cardList", headers=headers, params=params) as response:
            if response.status == 200:
                json_data = await response.json()
                return {
                    "status_code": response.status,
                    "data": json_data["data"],
                    "error": None
                }
            return {
                "status_code": response.status,
                "data": None,
                "error": f"Error: {await response.text()}"
            }


def search_by_name(name, params=None):
    if params is None:
        params = {}
    params.update({"free_word": name})
    return params


def search_by_cost(params, cost_list):
    cost_string = ""
    for cost in cost_list:
        cost_string += f"{cost},"
    params.update({"cost": cost_string[:-1]})


def make_card_dict_from_data(card_json, card_id):
    card_id = str(card_id) # Forzamos str, tira error si es int
    crest_text = None
    related_cards = []
    if card_json["card_details"][card_id]["common"]["is_token"]:
        is_token = True
        set_name = None
    else:
        is_token = False
        set_id = card_json["card_details"][card_id]["common"]["card_set_id"]
        set_name = card_json['card_set_names'][str(set_id)]
    if card_json["cards"]:
        if card_id in card_json["cards"].keys():
            specific_effects = card_json["cards"][card_id]["specific_effect_card_ids"]
            # Por ahora no hay carta que tenga más de un efecto específico. Revisar esto si eso llegue a cambiar
            if specific_effects:
                crest_text = card_json["specific_effect_card_info"][str(specific_effects[0])]["skill_text"]
            if not is_token:
                for related_card_id in card_json["cards"][card_id]['related_card_ids']:
                    # Hay que especificar que es un token en la recursion, asi evitamos una recursion infinita
                    related_cards.append(make_card_dict_from_data(card_json,related_card_id))
    trait_text = ""
    for trait in card_json["card_details"][card_id]["common"]["tribes"]:
        if trait != 0:
            trait_text += card_json["tribe_names"][str(trait)] + " "
    return {
        "card_id": card_json["card_details"][card_id]["common"]["card_id"],
        "card_name": card_json["card_details"][card_id]["common"]["name"],
        "card_type": card_json["card_details"][card_id]["common"]["type"],
        "card_set_name": set_name,
        "attack": card_json["card_details"][card_id]["common"]["atk"],
        "life": card_json["card_details"][card_id]["common"]["life"],
        "pp_cost": card_json["card_details"][card_id]["common"]["cost"],
        "rarity": card_json["card_details"][card_id]["common"]["rarity"],
        "faction": card_json["card_details"][card_id]["common"]["class"],
        "textbox": card_json["card_details"][card_id]["common"]["skill_text"],
        "img_url": f"https://shadowverse-wb.com/uploads/card_image/eng/card/{card_json["card_details"][card_id]["common"]["card_image_hash"]}.png",
        "evo_url": f"https://shadowverse-wb.com/uploads/card_image/eng/card/{card_json["card_details"][card_id]["evo"]["card_image_hash"]}.png" if
        card_json["card_details"][card_id]["evo"] else None,
        "traits": trait_text,
        "crest_text": crest_text,
        "related_cards": related_cards,
        "is_token": is_token,
    }
