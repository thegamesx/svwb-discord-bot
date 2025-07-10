import re
import discord
from discord.ui import Select, View

game_classes = {
    0: {"name": "Neutral", "icon": "class_neutral.png", "color": discord.Color.light_gray()},
    1: {"name": "Forest", "icon": "class_elf.png", "color": discord.Color.green()},
    2: {"name": "Sword", "icon": "class_royal.png", "color": discord.Color.yellow()},
    3: {"name": "Rune", "icon": "class_witch.png", "color": discord.Color.blurple()},
    4: {"name": "Dragon", "icon": "class_dragon.png", "color": discord.Color.orange()},
    5: {"name": "Abyss", "icon": "class_nightmare.png", "color": discord.Color.dark_red()},
    6: {"name": "Haven", "icon": "class_bishop.png", "color": discord.Color.light_embed()},
    7: {"name": "Portal", "icon": "class_nemesis.png", "color": discord.Color.blue()},
}

type_list = {
    1: "Follower",
    2: "Amulet",
    3: "Amulet",
    4: "Spell",
}


# ---- Select dinámico que se genera con las cartas encontradas ----
class CardSelect(Select):
    def __init__(self, card_data: dict):
        self.card_data = card_data
        options = []
        for card_id, card in card_data.items():
            if card["common"]["is_token"]:
                continue  # ignorar tokens
            name = card["common"]["name"]
            options.append(discord.SelectOption(label=name, value=card_id))
        if len(options) > 25:
            options = options[:25]
        super().__init__(placeholder="Selecciona una carta...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        selected_card = self.card_data[selected_id]
        embed, file = prepare_card_message(
            card_id=selected_card["common"]["card_id"],
            card_name=selected_card["common"]["name"],
            card_type=selected_card["common"]["type"],
            faction=selected_card["common"]["class"],
            textbox=selected_card["common"]["skill_text"],
            img_hash=selected_card["common"]["card_image_hash"],
            evo_hash=selected_card["evo"]["card_image_hash"] if selected_card["evo"] else None,
        )
        await interaction.response.send_message(embed=embed, file=file)


# ---- View que contiene el Select ----
class CardSelectView(View):
    def __init__(self, card_data: dict):
        super().__init__(timeout=120)  # se desactiva luego de 120s
        self.add_item(CardSelect(card_data))


# Mensaje de ayuda. Ver si ponerlo en un archivo, así es más fácil de editar.
# TODO: Cambiar esto
def help_message():
    return ("# Como usar el bot\nUsar el bot es fácil, tenes que mandar un mensaje entre corchetes, y va a hacer una "
            "busqueda por nombre. Ejemplo:\n\n`[albert]`\n\nSi necesitas ser más especifico con tu busqueda, podes poner "
            "! al principio para hacer una busqueda exacta. Esto quiere decir que el nombre tiene que estar completo, "
            "y solo va a devolver una carta. Ejemplo:\n\n`[!fairy]`\n\nEl bot prioriza las cartas del set principal a los "
            "tokens, entonces buscar [fairy] va a devolver Fairy Tamer, en vez del token si no se usa la busqueda exacta.\n\n-# [Código Fuente](<"
            "https://github.com/thegamesx/svwb-discord-bot>)")


# Separamos la caja de texto en 3: lo normal, la evo y la super evo
def split_evos(textbox):
    if not textbox:
        return {"normal": None, "evo": None, "super_evo": None}
    if "<ev>" in textbox or "<sev>" in textbox:
        normal = textbox[:textbox.find("<ev>")] if "<ev>" in textbox else textbox[:textbox.find("<sev>")]
        evo = re.findall(r'<ev>(.*?)</ev>', textbox)
        evo = evo[0] if evo else None
        super_evo = re.findall(r'<sev>(.*?)</sev>', textbox)
        super_evo = super_evo[0] if super_evo else ""
    else:
        normal = textbox
        evo = None
        super_evo = None
    return {
        "normal": strip_html(normal) if normal else None,
        "evo": strip_html(evo) if evo else None,
        "super_evo": strip_html(super_evo) if super_evo else None,
    }


def strip_html(text_string):
    # El bold no es compatible con el quote, asi por ahora lo dejo comentado
    # text_string = text_string.replace("<b>", "**")
    # text_string = text_string.replace("</b>", "**")
    text_string = re.sub(r'<.+?>', '', text_string)
    return text_string


def change_html_to_markdown(text):
    text = text.replace("<br>", "\n")
    text = text.replace("&nbsp;", "")
    text = text.replace("&amp;", "&")
    text = text.replace("<strong>", "**")
    text = text.replace("</strong>", "**")
    text = re.sub(r"<h\d(.*?)>", '## ', text)
    text = re.sub(r"</h\d>", '\n', text)
    text = text.replace('</div>', "\n")
    text = strip_html(text)
    return text


def prepare_news_message(title=None, desc=None, news_id=None, type_name=None):
    news_embed = discord.Embed(
        title=title,
        description=change_html_to_markdown(desc),
        url=f"https://shadowverse-wb.com/en/news/detail/?id={news_id}",
        color=discord.Color.blue()
    )
    news_embed.set_footer(text=type_name)
    return news_embed


def prepare_card_message(
        card_id=None,
        card_name=None,
        card_type=None,
        textbox=None,
        faction=None,
        crest_text=None,
        related_cards=None,
        img_hash=None,
        evo_hash=None,
):
    card_embed = discord.Embed(
        title=card_name,
        url=f"https://shadowverse-wb.com/en/deck/cardslist/card/?card_id={card_id}",
        description=f"{game_classes[faction]["name"]}craft - {type_list[card_type]}",
        color=game_classes[faction]["color"],
    )
    card_embed.set_thumbnail(url=f"attachment://{game_classes[faction]["icon"]}")
    textbox_split = split_evos(textbox)
    for ability_text in textbox_split.keys():
        if textbox_split[ability_text]:
            card_embed.add_field(name="", value=textbox_split[ability_text], inline=False)
    card_embed.set_image(url=f"https://shadowverse-wb.com/uploads/card_image/eng/card/{img_hash}.png")
    thumbnail = discord.File(f"files/{game_classes[faction]["icon"]}", filename=game_classes[faction]["icon"])
    return card_embed, thumbnail


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
