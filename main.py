import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from src import queries, svAPI, discord_message, news

# Configuración

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Se cargan las variables de entorno
load_dotenv()
news_channel = os.getenv("NEWS_CHANNEL")
bot_token = os.getenv("BOT_TOKEN")


# Comandos

@tasks.loop(hours=1)
async def check_for_news():
    news_json = svAPI.get_news()
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
    print(f"Estamos online como {client.user}")
    check_for_news.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("[") and message.content.endswith("]"):
        # El arbol de decisión debería estar en otro lado. Cuando sea más complejo hay que sacarlo de acá
        if message.content[1:-1] == "?":
            await message.channel.send(discord_message.help_message())
        else:
            search_result = queries.search_by_name(message.content[1:-1])
            if search_result:
                data_json = queries.fetch_data_from_id(search_result[0])
                card_image = svAPI.get_image(data_json["image"])
                text_message = discord_message.prepare_message(data_json, len(search_result))
                await message.channel.send(text_message, file=discord.File(card_image))
                # Esto manda ambas imagenes, pero no se ve bien completa, asi que por ahora suelo muestro la img base.
                # evo_image = queries.svAPI(data_json["evo_image"]) if data_json["evo_image"] else None
                """
                if evo_image:
                    await message.channel.send(text_message, files=[discord.File(card_image),discord.File(evo_image)])
                else:
                    await message.channel.send(text_message, file=discord.File(card_image))
                """
            else:
                await message.channel.send("-# No se encontraron cartas. Puedes ingresar [?] para ver la ayuda (se "
                                           "puede hacer por mensaje privado también)")


# Arranque del bot

client.run(bot_token)
