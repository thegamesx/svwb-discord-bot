import re


# Separamos la caja de texto en 3: lo normal, la evo y la super evo
def split_evos(textbox):
    if "<ev>" in textbox or "<sev>" in textbox:
        normal = textbox[:textbox.find("<ev>")] if "<ev>" in textbox else textbox[:textbox.find("<sev>")]
        evo = re.findall(r'<ev>(.*?)</ev>', textbox)
        evo = evo[0] if evo else ""
        super_evo = re.findall(r'<sev>(.*?)</sev>', textbox)
        super_evo = super_evo[0] if super_evo else ""
    else:
        normal = textbox
        evo = ""
        super_evo = ""
    return [strip_html(normal), strip_html(evo), strip_html(super_evo)]


def strip_html(text_string):
    # El bold no es compatible con el quote, asi por ahora lo dejo comentado
    # text_string = text_string.replace("<b>", "**")
    # text_string = text_string.replace("</b>", "**")
    text_string = re.sub(r'<.+?>', '', text_string)
    return text_string


# Prepara el texto para dejarlo con markdown
def prepare_message(card_json, search_items):
    textbox = split_evos(card_json["textbox"])
    msg = f"> ### [{card_json["name"]}](<https://shadowverse-wb.com/en/deck/cardslist/card/?card_id={card_json["card_id"]}>)\n"
    msg += f"**Clase:** {card_json["class"]}\n**Set:** {card_json["set"]}"
    for item in textbox:
        if item:
            msg += f"```{item}```"
    if card_json["crest_text"]:
        msg += f"```Crest: {strip_html(card_json["crest_text"])}```"
    if card_json["related_cards"]:
        msg += "_Cartas relacionadas: "
        for card in card_json["related_cards"]:
            msg += f"{card}, "
        msg = msg[:-2]
        msg += "_"
    if search_items > 1:
        msg += f"\n-# Se encontraron {search_items} cartas. Prueba siendo más especifico si no es la carta que buscas."
    return msg
