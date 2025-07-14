import os
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from src import queries, svAPI, discord_message, news

# Configuración

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# Se cargan las variables de entorno
load_dotenv()
news_channel = os.getenv("NEWS_CHANNEL")
bot_token = os.getenv("BOT_TOKEN")


# Comandos

@tasks.loop(hours=1)
async def check_for_news():
    news_json = await svAPI.get_news()
    news_to_send = news.checkForNewEntries(news_json)
    if news_to_send["success"]:
        channel = client.get_channel(int(news_channel))
        if news_to_send["error"]:
            print(f"Error fetching news: {news_to_send["error"]}")
        else:
            if news_to_send["data"]:
                for entry in news_to_send["data"]:
                    try:
                        news_data = svAPI.get_new_by_id(entry["id"])
                        news_embed = discord_message.prepare_news_message(
                            title=entry["title"],
                            desc=news_data["data"]["message"],
                            news_id=entry["id"],
                            type_name=entry["type_name"],
                        )
                        # Esto se podría poner en una función aparte
                        if entry["image_url"]:
                            news_embed.set_image(url=entry["image_url"])
                            await channel.send(embed=news_embed)
                        else:
                            news_banner = discord.File("files/news_banner_empty.png", filename="news_banner.png")
                            news_embed.set_image(url="attachment://news_banner.png")
                            await channel.send(file=news_banner, embed=news_embed)
                        print(f"Se envió {entry["title"]}")
                    except Exception as error:
                        print(f"Error: {error}")
                news.saveEntries(news_to_send["data"])


@client.event
async def on_ready():
    await tree.sync()
    print(f"Estamos online como {client.user}")
    check_for_news.start()


# noinspection PyUnresolvedReferences
@tree.command(
    name="search",
    description="Busca una carta",
)
async def search_card(interaction: discord.Interaction, search_query: str):
    try:
        print(f"Buscando {search_query}")
        search = await svAPI.search_card(svAPI.search_by_name(search_query))
        if search["status_code"] == 200:
            # Primero que nada, nos fijamos si se encontró alguna carta
            if search["data"]["card_details"]:
                all_card_ids = search["data"]["card_details"].keys()
                # Separamos los IDs de las cartas y los tokens
                card_ids = []
                token_ids = []
                for card_id in all_card_ids:
                    token_ids.append(card_id) if search["data"]["card_details"][card_id]["common"]["is_token"] else card_ids.append(card_id)
                if len(card_ids) == 1:

                    card_details = svAPI.make_card_dict_from_data(search["data"], card_ids[0])
                    card_embed, thumbnail_file, related_cards_view = discord_message.prepare_card_message(card_details)

                    await interaction.response.send_message(embed=card_embed, file=thumbnail_file, view=related_cards_view)
                else:
                    # Si se encuentran más de una carta, se devuelve una lista para que el usuario elija cuál mostrar
                    view = discord_message.CardSelectView(search["data"])
                    await interaction.response.send_message(
                        content=f"🔍 Se encontraron {search["data"]["count"]} cartas. Elegí una:",
                        view=view,
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message(f"-# ❌ No se encontraron cartas.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error {search["status_code"]}: {search["error"]}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)


# Arranque del bot

client.run(bot_token)
