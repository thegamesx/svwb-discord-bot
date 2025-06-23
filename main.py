import os
import discord
from dotenv import load_dotenv
from functools import lru_cache
from src import queries, svAPI, discord_message

# Configuración

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@lru_cache()
def get_bot_token():
    load_dotenv()
    return os.getenv("BOT_TOKEN")


# Comandos

@client.event
async def on_ready():
    print(f"Estamos online como {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("[") and message.content.endswith("]"):
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
            await message.channel.send("-# No se encontraron cartas.")


# Arranque del bot

client.run(get_bot_token())
