import re
import discord
from discord.ui import Select, View, Button
from .svAPI import make_card_dict_from_data

# TODO: Poner en un json aparte, en un archivo.
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

rarity_list = {
    1: "Bronze",
    2: "Silver",
    3: "Gold",
    4: "Legendary",
}


# ---- Select dinámico que se genera con las cartas encontradas ----
class CardSelect(Select):
    def __init__(self, card_data: dict):
        self.card_data = card_data
        options = []
        for card_id, card in card_data["card_details"].items():
            if card["common"]["is_token"]:
                continue  # ignorar tokens
            name = card["common"]["name"]
            options.append(discord.SelectOption(label=name, value=card_id))
        if len(options) > 25:
            options = options[:25]
        super().__init__(placeholder="Selecciona una carta...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        data_json = self.card_data
        card_json = make_card_dict_from_data(data_json, selected_id)
        embed, file, view = prepare_card_message(card_json)
        await interaction.response.send_message(embed=embed, file=file, view=view)


# ---- View que contiene el Select ----
class CardSelectView(View):
    def __init__(self, card_data: dict):
        super().__init__(timeout=120)  # se desactiva luego de 120s
        self.add_item(CardSelect(card_data))


# Creamos un boton que mande las cartas relacionadas por privado
class CardExtrasView(View):
    def __init__(self, card_img_url, evo_img_url, related_cards=None):
        super().__init__(timeout=60)
        self.related_cards = related_cards
        self.card_img_url = card_img_url
        self.evo_img_url = evo_img_url

        # Botón para ver el arte de una carta
        art_button = Button(
            label="Ver arte",
            style=discord.ButtonStyle.secondary,
            custom_id="card_image_button"
        )
        art_button.callback = self.send_card_art
        self.add_item(art_button)

        # Pone el botón para ver cartas relacionadas solo si hay
        if related_cards:
            related_button = Button(
                label="Ver cartas relacionadas",
                style=discord.ButtonStyle.secondary,
                custom_id="related_cards_button"
            )
            related_button.callback = self.send_related_cards
            self.add_item(related_button)

    async def send_related_cards(self, interaction: discord.Interaction):
        # La función devuelve el embed, thumbnail y view juntos. Aca no vamos a usar el view por ahora, asi que
        # lo ignoramos. Después suponemos que el thumbnail va a ser igual para todos los embeds, asi que solo
        # uso el primero. Hay que ver como hacer si tienen que ser diferentes.
        related_cards_embeds = [prepare_card_message(related_card) for related_card in self.related_cards]
        if len(related_cards_embeds) == 1:
            await interaction.response.send_message(embed=related_cards_embeds[0][0], file=related_cards_embeds[0][1],
                                                    ephemeral=True)
        else:
            related_cards_embeds_temp = [embed[0] for embed in related_cards_embeds]
            await interaction.response.send_message(embeds=related_cards_embeds_temp, file=related_cards_embeds[0][1],
                                                    ephemeral=True)

    async def send_card_art(self, interaction: discord.Interaction):
        # TODO: Ver excepciones
        embed_normal = discord.Embed(title="")
        embed_normal.set_image(url=self.card_img_url)
        if self.evo_img_url:
            embed_evo = discord.Embed(title="Evolución")
            embed_evo.set_image(url=self.evo_img_url)
            await interaction.response.send_message(
                embeds=[embed_normal, embed_evo],
                ephemeral=True
            )
        else:
            await interaction.response.send_message(embed=embed_normal, ephemeral=True)


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


def strip_html(text_string: str):
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


def prepare_card_message(card_json):
    if card_json["is_token"]:
        description = f"{game_classes[card_json["faction"]]["name"]}craft ({rarity_list[card_json["rarity"]]})"
    else:
        description = (f"{game_classes[card_json["faction"]]["name"]}craft ({rarity_list[card_json["rarity"]]})\n"
                       f"Set: {card_json["card_set_name"]}")
    card_embed = discord.Embed(
        title=card_json["card_name"],
        url=f"https://shadowverse-wb.com/en/deck/cardslist/card/?card_id={card_json["card_id"]}",
        description=description,
        color=game_classes[card_json["faction"]]["color"],
    )
    card_embed.set_thumbnail(url=f"attachment://{game_classes[card_json["faction"]]["icon"]}")
    textbox_split = split_evos(card_json["textbox"])
    if card_json["is_token"]:
        type_text = f"{card_json["traits"]}{type_list[card_json["card_type"]]} Token"
    else:
        type_text = f"{card_json["traits"]}{type_list[card_json["card_type"]]}"
    card_embed.add_field(name="", value=type_text, inline=False)
    if not (card_json["attack"] == 0 and card_json["life"] == 0):
        card_embed.add_field(name="", value=f"{card_json["pp_cost"]}PP {card_json["attack"]}/{card_json["life"]}",
                             inline=False)
    else:
        card_embed.add_field(name="", value=f"{card_json["pp_cost"]}PP", inline=False)
    for ability_text in textbox_split.keys():
        if textbox_split[ability_text]:
            card_embed.add_field(name="", value=textbox_split[ability_text], inline=False)
    if card_json["crest_text"]:
        card_embed.add_field(name="Crest", value=change_html_to_markdown(card_json["crest_text"]), inline=False)

    # Agregamos botones para ver el arte de la carta y sus cartas relacionadas (si hay)
    view = CardExtrasView(card_json["img_url"], card_json["evo_url"], related_cards=card_json["related_cards"])

    thumbnail = discord.File(
        f"files/{game_classes[card_json["faction"]]["icon"]}",
        filename=game_classes[card_json["faction"]]["icon"]
    )
    return card_embed, thumbnail, view
