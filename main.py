import os
import discord
import requests
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("token")

#intents setup
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

client = discord.Client(intents=intents)
# URL for the Express server where the daily problem is exposed
EXPRESS_SERVER_URL = 'http://localhost:8000'

@bot.command()
async def daily(ctx):
    try:
        # Fetch the daily problem from the Express server
        response = requests.get(EXPRESS_SERVER_URL)
        
        # Check if the request was successful
        if response.status_code == 200:
            daily_problem = response.json()

            # Prepare the problem message
            message = str(datetime.today().strftime('%m-%d')) + f": **{daily_problem['question']['title']}**.\n\nQuestion Difficulty: **{daily_problem['question']['difficulty']}**\n\nLink: https://www.leetcode.com{daily_problem['link']}\n\nStatement: {daily_problem['question']['content']}"
            message = message[:message.rfind('<strong class="example">Example 1:')]
            message.replace(r'\n', '\n')
            print(message)
            soup = BeautifulSoup(message, "html.parser")
            for data in soup(['script']):
                data.decompose()
            message = ""
            for string in soup.stripped_strings:
                if (string=='.'):
                    message+=(string + '\n\n')
                else:
                    message+=(string+ " ")
            message.replace(' ,', ',')
            message.replace(' .', '.')
            message.replace(' :', ':')
            message = "Good Morning <@&1172561226576965683>\n\nThis is your coding interview problem for " + message + "Have a great day! Reminder: You can get the Daily Programming role in the <#884991300296925214>\n\nNote: You can discuss about the Question in the following thread: <#1169709010958688376>"
        else:
            message = "Sorry, I couldn't fetch the daily problem at the moment."

    except Exception as e:
        # In case of any error, we provide a fallback message
        message = f"An error occurred while fetching the daily problem: {str(e)}"

    # Send the message to the Discord channel
    await ctx.send(message)

# Function to calculate the number of seconds until 8 PM today
def get_seconds_until_8pm():
    now = datetime.now()
    target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now >= target_time:
        # If it's already past 8 PM today, schedule for 8 PM tomorrow
        target_time += timedelta(days=1)
    return (target_time - now).total_seconds()

# Function to schedule the daily message at 8 PM every day
async def schedule_daily_message():
    while True:
        # Wait until 8 PM
        seconds_until_8pm = get_seconds_until_8pm()
        await asyncio.sleep(seconds_until_8pm)  # Wait until 8 PM
        await daily()  # Send the daily problem

        # Sleep for 24 hours and repeat
        await asyncio.sleep(86400)  # 86400 seconds = 24 hours

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    schedule_daily_message()

bot.run(TOKEN)
