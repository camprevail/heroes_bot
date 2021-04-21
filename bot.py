import discord
from discord.ext import commands
from io import BytesIO
import os, requests, time, json, aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from utils.imageutils import imageGrid
from utils.htmlutils import *
from utils.pagination import LinePaginator



load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

bot = commands.Bot(command_prefix='?')

@bot.command(help="Type ?guide to see the list of heroes.")
async def guide(ctx, character=None):
    with open('names.json', 'r') as f:
        names = json.load(f)

    with open('realnames.txt', 'r') as f:
        realNames = [line.rstrip() for line in f.readlines()]

    if not character:
        embed = discord.Embed(title="**Current list of Heroes**")
        await LinePaginator.paginate(
            bot,
            realNames,
            ctx,
            embed,
            footer_text=f"Usage is {bot.command_prefix}guide <hero name>.",
            empty=False,
            max_lines=20
        )
        return

    def namesearch(char):
        for key, val in names.items():
            if char in val or char == key:
                return key

    url_character = namesearch(character.lower())
    if not url_character:
        await ctx.send(f"`{character}` is not a valid character.")
        return

    a = round(time.perf_counter(), 3) # start performance timer
    url = f'https://www.icy-veins.com/heroes/{url_character}-build-guide'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    buildsinfo = getinfo(soup) # Dict of info for each build.

    # Fetch the icons
    image_urls = []
    for b in buildsinfo.values():
        for level in b.get('levels').values():
            image_urls.append(level.get('url'))
    conn = aiohttp.TCPConnector()
    image_data = await fetch(conn, image_urls)

    # insert the image bytes into the buildsinfo dict
    for b in buildsinfo.values():
        for level in b.get('levels').values():
            _url = level['url']
            level['image_data'] = image_data[_url]

    # Pass the image list into the imageGrid function. It will return a list of images for each build.
    result = imageGrid(buildsinfo)

    # Post each image to discord with the build code as plain text, so users can easily copy it.
    i = 1
    for code, img in result:
        buffer = BytesIO()
        img.save(buffer, 'png')
        buffer.seek(0)
        await ctx.send(f"`Build [{i}/{len(result)}]:  {code}`", file=discord.File(buffer, filename='unknown.png'))
        i += 1
    await ctx.send(f'<{url}>')
    b = round(time.perf_counter(), 3) # finish time
    print(f'{len(result)} image(s) generated in {(str(round(b-a, 3)))} seconds for character {character}.')
    return


bot.run(TOKEN)