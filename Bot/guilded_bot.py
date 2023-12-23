import asyncio
import datetime
import json
import os
import threading
import traceback

import aiohttp
import guilded
from guilded.ext import commands
import config
import requests
import pathlib

client = commands.Bot(command_prefix="gc!")


@client.event
async def on_message_delete(message: guilded.Message):
    print(1)
    endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.server.id}.json", "r")
    endpoint = json.load(endpoint_file)["discord"]
    r1 = requests.get(f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5)
    if message.channel.id in \
            r1.json()[
                "config"]["channels"]["guilded"]:
        embed = guilded.Embed(title=f"{message.author.name} - Deleted", description=message.content, colour=0xf5c400)
        embed.add_field(name="Created at",
                        value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M.%S")} UTC')
        r2 = requests.get(f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5)
        channel = await client.fetch_channel(r2.json()["config"]["logs"]["guilded"])
        await channel.send(embed=embed)
    r1.close()


@client.event
async def on_message_edit(before: guilded.Message, after: guilded.Message):
    print(2)
    endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{before.server.id}.json", "r")
    endpoint = json.load(endpoint_file)["discord"]
    r1 = requests.get(f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5)
    if before.channel.id in \
            r1.json()[
                "config"]["channels"]["guilded"]:

        embed = guilded.Embed(title=f"{before.author.name} - Edited", description=after.content, colour=0xf5c400)
        embed.add_field(name="Jump", value=f"[Jump]({after.jump_url})")
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        r2 = requests.get(f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5)
        channel = await client.fetch_channel(
            r2.json()[
                "config"]["logs"][
                "guilded"])
        r2.close()
        await channel.send(embed=embed)
    r1.close()


@client.event
async def on_message(message: guilded.Message):
    if message.content.lower().startswith("gc!"):
        global endpoint
        if message.content.lower().startswith("gc!register"):
            try:
                endpoint = int(message.content.replace("gc!register ", ""))
            except ValueError:
                await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
                return
            print(endpoint)
            if endpoint == "":
                await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
            else:
                for server in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers"):
                    if server.endswith(".json"):
                        try:
                            discord_server = json.load(open(server, "r"))["discord"]
                            if discord_server == endpoint:
                                await message.channel.send(
                                    f"Enpoint exists already: https://guildcord.deutscher775.de/{endpoint}")
                                return
                        except:
                            pass
                    else:
                        pass

                try:
                    data = {"discord": endpoint}
                    json.dump(data,
                              open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.guild.id}.json",
                                   "x"))
                except FileExistsError:
                    await message.channel.send(f"Enpoint exists already: https://guildcord.deutscher775.de/{endpoint}")
                    return
                webhook = await message.channel.create_webhook(name="Guildcord")
                r = requests.post(
                    f"https://guildcord.deutscher775.de/update/{endpoint}?channel_guilded={message.channel.id}&"
                    f"webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}", timeout=5)
                r.close()
                await message.channel.send(f"Updated enpoint: https://guildcord.deutscher775.de/{endpoint}")
        if message.content.lower().startswith("gc!help"):
            embed = guilded.Embed(title="Guildcord", description="API Docs: https://guildcord.deutscher775.de/docs")
            embed.add_field(name="register",
                            value="Register you server.\nNote: First register your discord server, then guilded.",
                            inline=False)
            embed.add_field(name="set-log",
                            value="Setup you log channel.\nUsage: DISCORD_SERVER_ID GUILDED_CHANNEL_ID",
                            inline=False)
            embed.add_field(name="allow",
                            value="Allow a bot or webhook to be forwarded.\nUsage: DISCORD_SERVER_ID USER_ID",
                            inline=False)
            embed.add_field(name="add-bridge", value="Add another channel to bridge over.\nNote: Works like `register`",
                            inline=False)
            await message.channel.send(embed=embed)
        if message.content.lower().startswith("gc!set-log"):
            try:
                endpoint = int(message.content.replace("gc!set-log ", "").split(" ")[0])
            except ValueError:
                await message.channel.send("Invalid Format: `gc!set-log DISCORD_SERVER_ID GUILDED_CHANNEL_ID`")
                return
            channelid = message.content.replace("gc!set-log ", "").split(" ")[1]
            if endpoint == "" or channelid == "":
                await message.channel.send("Invalid Format: `gc!set-log DISCORD_SERVER_ID GUILDED_CHANNEL_ID`")
            else:
                r = requests.post(
                    f"https://guildcord.deutscher775.de/update/{endpoint}?channel_guilded={message.channel.id}&"
                    f"log_guilded={channelid}&token={config.MASTER_TOKEN}", timeout=5)
                r.close()
                await message.channel.send(f"Updated enpoint: https://guildcord.deutscher775.de/{endpoint}")

        if message.content.lower().startswith("gc!allow"):
            try:
                endpoint = int(message.content.replace("gc!allow ", "").split(" ")[0])
                print(endpoint)
            except ValueError:
                print(1)
                await message.channel.send("Invalid Format: `gc!allow DISCORD_SERVER_ID GUILDED_USER_ID`")
                return
            allowid = message.content.replace("gc!allow ", "").split(" ")[1]
            print(allowid)
            if endpoint == "" or allowid == "":
                await message.channel.send("Invalid Format: `gc!allow DISCORD_SERVER_ID GUILDED_USER_ID`")
            else:
                r = requests.post(
                    f"https://guildcord.deutscher775.de/update/{endpoint}?allowed_ids={allowid}&token={config.MASTER_TOKEN}", timeout=5)
                r.close()
                await message.channel.send(f"Updated enpoint: https://guildcord.deutscher775.de/{endpoint}")

        if message.content.lower().startswith("gc!add-bridge"):
            try:
                endpoint = int(message.content.replace("gc!add-bridge ", ""))
            except ValueError:
                await message.channel.send("Invalid Format: `gc!add-bridge DISCORD_SERVER_ID`")
                return
            print(endpoint)
            if endpoint == "":
                await message.channel.send("Invalid Format: `gc!add-bridge DISCORD_SERVER_ID`")
            else:
                webhook = await message.channel.create_webhook(name="Guildcord")
                r = requests.post(
                    f"https://guildcord.deutscher775.de/update/{endpoint}?channel_guilded={message.channel.id}&"
                    f"webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}", timeout=5)
                r.close()
                await message.channel.send(f"Updated enpoint: https://guildcord.deutscher775.de/{endpoint}")


    else:
        try:
            endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.server.id}.json",
                                 "r")
            endpoint = json.load(endpoint_file)["discord"]
            r1 = requests.get(
                    f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5)
            if message.channel.id in r1.json()[
                "config"]["channels"][
                "guilded"]:
                try:
                    blacklist = requests.get(
                        f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5).json()[
                        "config"]["blacklist"]
                    for word in blacklist:
                        if word is not None:
                            if word.lower() in message.content.lower():
                                embed = guilded.Embed(title=f"{message.author.name} - Flagged",
                                                      description=message.content, colour=0xf5c400)
                                await message.delete()
                                channel = await client.fetch_channel(str(requests.get(
                                    f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5).json()[
                                                                             "config"]["logs"][
                                                                             "guilded"]))
                                await channel.send(embed=embed)
                                return
                        else:
                            pass
                    else:
                        allowed_ids = requests.get(
                            f"https://guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}", timeout=5).json()[
                            "config"]["allowed-ids"]
                        if not message.author.bot or message.author.id in allowed_ids:
                            if not message.attachments:
                                try:
                                    r = requests.post(
                                        f"https://guildcord.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                        f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                        f"message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&"
                                        f"sender_channel={message.channel.id}", timeout=5)
                                    r.close()
                                except:
                                    await message.reply(
                                        "Oops.. something went wrong sending your message. Try again or join the [support server](https://guilded.gg/guildcord)")
                            if message.attachments:
                                if len(message.attachments) == 1:
                                    try:
                                        r = requests.post(
                                            f"https://guildcord.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                            f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                            f"message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}"
                                            f"&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url.replace('![]', '').replace('(', '').replace(')', '')}", timeout=5)
                                        r.close()
                                    except:
                                        await message.reply("Oops.. something went wrong sending your message. Try again or join the [support server](https://guilded.gg/guildcord)")
                                else:
                                    attachments = ""
                                    for attachment in message.attachments:
                                        attachments += attachment.url.replace("![]", "").replace("(", "").replace(")",
                                                                                                                  "")
                                    try:
                                        r = requests.post(
                                            f"https://guildcord.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                            f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                            f"message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}"
                                            f"&sender_channel={message.channel.id}&message_attachments={attachments[:-1]}", timeout=5)
                                        r.close()
                                    except:
                                        await message.reply("Oops.. something went wrong sending your message. Try again or join the [support server](https://guilded.gg/guildcord)")
                    blacklist.close()

                except:
                    traceback.print_exc()
                    pass
        except FileNotFoundError:
            pass


client.run(config.GUILDED_TOKEN)
