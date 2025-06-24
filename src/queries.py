import json

with open('json/cardList.json', 'r') as file:
    card_list = json.load(file)

# Probablemente debería usar lo que está en cardList.json. Revisar después
class_list = {
    0: "Neutral",
    1: "Forestcraft",
    2: "Swordcraft",
    3: "Runecraft",
    4: "Dragoncraft",
    5: "Abysscraft",
    6: "Havencraft",
    7: "Portalcraft",
}


# Algunas cartas tienen otras relacionadas o efectos que no están en el mismo id. Acá buscamos esos datos de ser el caso
def check_additional_data(card_id):
    if card_id in card_list["data"]["cards"].keys():
        related_cards = card_list["data"]["cards"][card_id]["related_card_ids"]
        specific_effect = card_list["data"]["cards"][card_id]["specific_effect_card_ids"]
        related_cards_list = []
        if related_cards:
            for card in related_cards:
                related_cards_list.append(card_list["data"]["card_details"][str(card)]["common"]["name"])
        specific_effect_text = card_list["data"]["specific_effect_card_info"][
            str(specific_effect[0])] if specific_effect else []
        return {"related_cards": related_cards_list, "specific_effect": specific_effect_text}
    else:
        return {"related_cards": "", "specific_effect": ""}


def fetch_data_from_id(card_id):
    additional_data = check_additional_data(card_id)
    card_data = {
        "card_id": card_list["data"]["card_details"][card_id]["common"]["card_id"],
        "name": card_list["data"]["card_details"][card_id]["common"]["name"],
        "class": class_list[card_list["data"]["card_details"][card_id]["common"]["class"]],
        "textbox": card_list["data"]["card_details"][card_id]["common"]["skill_text"],
        "flavor": card_list["data"]["card_details"][card_id]["common"]["flavour_text"],
        "image": card_list["data"]["card_details"][card_id]["common"]["card_image_hash"],
        "evo_image": card_list["data"]["card_details"][card_id]["evo"]["card_image_hash"] if
        card_list["data"]["card_details"][card_id]["evo"] else "",
        "set": card_list["data"]["card_set_names"][
            str(card_list["data"]["card_details"][card_id]["common"]["card_set_id"])],
        "related_cards": additional_data["related_cards"],
        "crest_text": additional_data["specific_effect"]["skill_text"] if additional_data["specific_effect"] else "",
    }
    return card_data


def search_by_name(query):
    results = []
    id_list = card_list["data"]["card_details"].keys()
    # Si la búsqueda arranca con un !, hacemos una búsqueda exacta
    if query[0] == "!":
        for card_id in id_list:
            if query[1:].lower() == card_list["data"]["card_details"][card_id]["common"]["name"].lower():
                results.append(card_id)
    else:
        for card_id in id_list:
            if query.lower() in card_list["data"]["card_details"][card_id]["common"]["name"].lower():
                results.append(card_id)
    return results
