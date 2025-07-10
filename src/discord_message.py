import re
import discord


# Mensaje de ayuda. Ver si ponerlo en un archivo, así es más fácil de editar.
def help_message():
    return ("# Como usar el bot\nUsar el bot es fácil, tenes que mandar un mensaje entre corchetes, y va a hacer una "
            "busqueda por nombre. Ejemplo:\n\n`[albert]`\n\nSi necesitas ser más especifico con tu busqueda, podes poner "
            "! al principio para hacer una busqueda exacta. Esto quiere decir que el nombre tiene que estar completo, "
            "y solo va a devolver una carta. Ejemplo:\n\n`[!fairy]`\n\nEl bot prioriza las cartas del set principal a los "
            "tokens, entonces buscar [fairy] va a devolver Fairy Tamer, en vez del token si no se usa la busqueda exacta.\n\n-# [Código Fuente](<"
            "https://github.com/thegamesx/svwb-discord-bot>)")


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


def change_html_to_markdown(text, link=None):
    text = text.replace("<br>", "\n")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("<strong>", "**")
    text = text.replace("</strong>", "**")
    text = re.sub(r"<h\d(.*?)>", '## ', text)
    text = re.sub(r"</h\d>", '\n', text)
    text = text.replace('</div>', "\n")
    text = strip_html(text)
    if len(text) > 4096:
        text = text[:3900] + f"...\n\nMensaje muy largo. [Ver el resto.](<{link}>)"
    return text


def prepare_news_message(title=None, desc=None, news_id=None, type_name=None):
    news_embed = discord.Embed(
        title=title,
        description=change_html_to_markdown(desc, link=f"https://shadowverse-wb.com/en/news/detail/?id={news_id}"),
        url=f"https://shadowverse-wb.com/en/news/detail/?id={news_id}",
        color=discord.Color.blue()
    )
    news_embed.set_footer(text=type_name)
    return news_embed


# Prepara el texto para dejarlo con markdown
def prepare_message(card_json, search_items):
    textbox = split_evos(card_json["textbox"])
    msg = f"> ### [{card_json["name"]}](<https://shadowverse-wb.com/en/deck/cardslist/card/?card_id={card_json["card_id"]}>)\n"
    msg += f"**Clase:** {card_json["class"]}\n**Set:** {card_json["set"]}\n"
    for item in textbox:
        if item:
            msg += f"```\n{item}\n```"
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
