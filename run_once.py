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
    with open("day.txt", 'r') as source_file:
        if source_file.readline() == str(datetime.now(timezone.utc).strftime('%m-%d')):
            await bot.close()
            return
        else:
            with open("day.txt", 'w') as destination_file:
                destination_file.write(datetime.now(timezone.utc).strftime('%m-%d'))
    print("Starting daily problem fetch")
    try:
        response = requests.get(EXPRESS_SERVER_URL)

        print("Got response")
        while response.status_code != 200:
            print("Waiting 10 seconds to start up server again")
            time.sleep(10)
            response = requests.get(EXPRESS_SERVER_URL)

        # Check if the request was successful
        if response.status_code == 200:
            daily_problem = response.json()

            # Prepare the problem message
            message = str(datetime.now(timezone.utc).strftime('%m-%d')) + f": **{daily_problem['question']['title']}**.\n\nQuestion Difficulty: **{daily_problem['question']['difficulty']}**\n\nLink: https://www.leetcode.com{daily_problem['link']}\n\nStatement: {daily_problem['question']['content']}"
            message = message.replace('<strong>', '**')
            message = message.replace('</strong>', '**')
            message = message.replace('<code>', '`')
            message = message.replace('</code>', '`')
            message = message.replace('<code>', '`')
            message = message.replace('</code>', '`')
            message = message[:message.rfind('<strong class="example">Example 1:')]
            message.replace(r'\n', '\n')
            soup = BeautifulSoup(message, "html.parser")
            for data in soup(['script']):
                data.decompose()
            message = ""
            for string in soup.stripped_strings:
                if (string=='.'):
                    message+=(string + '\n\n')
                else:
                    message+=(string+ " ")
            message.strip()
            message = message.replace(' ,', ',')
            message = message.replace(' .', '.')
            message = message.replace(' :', ':')
            message = message.replace(' ]', ']')
            message = message.replace(' [', '[')
            print(message)
            message = "Good Morning <@&1172561226576965683>\n\nThis is your coding interview problem for " + message + "\n\nHave a great day! Reminder: You can get the Daily Programming role in the <#760321299083034635>"
            message = message.replace('\n\n\n\n', '\n\n')
            msg = await bot.get_channel(channel).send(message[:2000])
            msg.publish()
            if len(message) > 2000:
                msg = await bot.get_channel(channel).send(message[2000:])
                msg.publish()

            print(f"Posted daily problem: {daily_problem['question']['title']}")
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
