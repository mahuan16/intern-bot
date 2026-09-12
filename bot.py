import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import re
from scraper import scrape_and_save
from views import PostingView


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") # grab discord token DONT SHARE IT
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 
GENERAL_ID = int(os.getenv("GENERAL_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True # let bot read messages in server

# init bot; rn use ! to indicate command
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready(): # when bot connects
    print(f"Logged in as {bot.user}")
    check_for_new_postings.start()
    affirmations.start()

@bot.event
async def on_message(message): # VERTY important function VERY important trust

    if message.author == bot.user:
        return
    
    match = re.search(r"\b(i am|i'm|im)\s+(.+)", message.content, re.IGNORECASE)

    if match:
        name = match.group(2).strip()
        if name.lower() == 'internbot':
            await message.channel.send(f"Nuh uh, I'm InternBot!")
            return
        await message.channel.send(f"Hi {name}, I'm InternBot!")

    await bot.process_commands(message)


@tasks.loop(minutes = 5)
async def check_for_new_postings():
    new_postings = scrape_and_save()
    print(f"Loop ran, found {len(new_postings)} new postings.")

    channel = bot.get_channel(CHANNEL_ID)

    for posting in new_postings:
        embed = discord.Embed(
            title=posting.position,
            description=posting.description or "No description provided.",
            color=discord.Color.blue(),
            url=posting.url
        )
        embed.add_field(name="Company", value=posting.company, inline=True)
        embed.add_field(name="Location", value=posting.location, inline=True)
        embed.add_field(name="Pay", value=posting.pay or "Not listed", inline=True)

        view = PostingView(posting_id=posting.id)

        await channel.send(embed=embed, view=view)

import csv
import random
import datetime

# function for when you wonder why you're in this major when 
# ai can code better than you and you are dperecated haha
pst = datetime.timezone(datetime.timedelta(hours=-7))

scheduled_times = [
    datetime.time(hour=8, minute=0, tzinfo=pst),
    datetime.time(hour=12, minute=0, tzinfo=pst),
    datetime.time(hour=18, minute=30, tzinfo=pst),
    datetime.time(hour=20, minute=0, tzinfo=pst),
    datetime.time(hour=23, minute=0, tzinfo=pst)
]
@tasks.loop(time=scheduled_times)
async def affirmations():
    channel = bot.get_channel(GENERAL_ID)
    wholesome_quote ="sob"

    with open("affirmations.csv", mode="r") as f:
        reader = csv.reader(f)
    
        wholesome_quote = "".join(random.choice(list(reader)))
        #wholesome_quote = wholesome_quote[1:-1].strip('"')
        print(wholesome_quote)
    await channel.send(wholesome_quote)

@bot.command()
async def affirm(ctx):
    wholesome_quote ="sob"

    with open("affirmations.csv", mode="r") as f:
        reader = csv.reader(f)
    
        wholesome_quote = "".join(random.choice(list(reader)))
        #wholesome_quote = wholesome_quote[1:-1].strip('"')
        print(wholesome_quote)
    await ctx.send(wholesome_quote)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def maria(ctx):
    await ctx.send("Maria is the best, most amazing person in the whole world. You should pray to her and give her your gratitude and shower her with compliments and gifts. All hail Goddess Maria.")

bot.run(TOKEN)