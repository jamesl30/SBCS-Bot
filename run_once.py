import os
import discord
import requests
from discord.ext import commands
from discord import Embed
import asyncio
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import pytz
import time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("token")

main = 827652217901154375
channel = 827652217901154375
home = 1072138841969938482

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

EXPRESS_SERVER_URL = 'http://localhost:8000'

def get_current_day():
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    return now.strftime("%Y-%m-%d")

def update_day_file(day):
    with open('day.txt', 'w') as f:
        f.write(day)

def read_day_file():
    try:
        with open('day.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

async def fetch_and_post_daily_problem():
    try:
        response = requests.get(EXPRESS_SERVER_URL)
        if response.status_code == 200:
            data = response.json()

            title = data.get('title', 'No title')
            question_id = data.get('questionId', 'N/A')
            difficulty = data.get('difficulty', 'Unknown')
            content = data.get('content', 'No content available')
            question_link = data.get('questionLink', '#')

            soup = BeautifulSoup(content, 'html.parser')
            clean_content = soup.get_text()

            embed = Embed(title=f"Daily LeetCode Problem: {title}", color=0x00ff00)
            embed.add_field(name="Question ID", value=question_id, inline=True)
            embed.add_field(name="Difficulty", value=difficulty, inline=True)
            embed.add_field(name="Link", value=f"[Solve Problem]({question_link})", inline=False)

            if len(clean_content) > 1024:
                clean_content = clean_content[:1021] + "..."

            embed.add_field(name="Problem Description", value=clean_content, inline=False)

            channel_obj = bot.get_channel(channel)
            if channel_obj:
                await channel_obj.send(embed=embed)
                print(f"Posted daily problem: {title}")

                current_day = get_current_day()
                update_day_file(current_day)

                await bot.close()
            else:
                print("Channel not found")
                await bot.close()
        else:
            print(f"Failed to fetch data from Express server. Status code: {response.status_code}")
            await bot.close()
    except Exception as e:
        print(f"Error fetching daily problem: {e}")
        await bot.close()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await fetch_and_post_daily_problem()

if __name__ == "__main__":
    bot.run(TOKEN)