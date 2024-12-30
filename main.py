import os
import discord
import requests
from discord.ext import commands
from discord import Embed
import asyncio
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import schedule
import pytz
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv
import subprocess

def get_pid_by_port(port):
    try:
        result = subprocess.run(['lsof', '-t', '-i', f':{port}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid = result.stdout.decode('utf-8').strip()
        
        if pid:
            return int(pid)
        else:
            print(f"No process found on port {port}.")
            return None
    except Exception as e:
        print(f"Error finding PID: {e}")
        return None

load_dotenv()

TOKEN = os.getenv("token")

main = 827652217901154375
channel = 827652217901154375
home = 1072138841969938482
#channel = home

#intents setup
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

client = discord.Client(intents=intents)
# URL for the Express server where the daily problem is exposed
EXPRESS_SERVER_URL = 'http://localhost:8000'

current_date = ""

@bot.command()
async def daily(ctx):
    with open("day.txt", 'r') as source_file:
        if source_file.readline() == str(datetime.now(timezone.utc).strftime('%m-%d')):
            return
        else:
            with open("day.txt", 'w') as destination_file:
                destination_file.write(datetime.now(timezone.utc).strftime('%m-%d'))
    try:
        command = "ps aux"
        pid_list = subprocess.check_output(command, shell=True).decode().splitlines()
        if pid_list:
            # Kill each process by PID
            for pid in pid_list:
                kill_command = f"kill -9 {pid}"
                subprocess.run(kill_command, shell=True)
                print(f"Terminated process with PID: {pid}")

        response = requests.get(EXPRESS_SERVER_URL)
        
        # Check if the request was successful
        if response.status_code == 200:
            daily_problem = response.json()

            # Prepare the problem message
            message = str(datetime.now(timezone.utc).strftime('%m-%d')) + f": **{daily_problem['question']['title']}**.\n\nQuestion Difficulty: **{daily_problem['question']['difficulty']}**\n\nLink: https://www.leetcode.com{daily_problem['link']}\n\nStatement: {daily_problem['question']['content']}"
            #message = f"Statement: {daily_problem['question']['content']}"
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
            message = "Good Morning <@&1172561226576965683>\n\nThis is your coding interview problem for " + message + "\n\nHave a great day! Reminder: You can get the Daily Programming role in the <#884991300296925214>\n\nNote: You can discuss about the Question in the following thread: <#1169709010958688376>"
            message = message.replace('\n\n\n\n', '\n\n')
            msg = await bot.get_channel(channel).send(message)
            '''
                "Good Morning <@&1172561226576965683>\n\nThis is your coding interview problem for "
                + str(datetime.now(timezone.utc).strftime('%m-%d'))
                + f": **{daily_problem['question']['title']}**.\n\nQuestion Difficulty: **{daily_problem['question']['difficulty']}**\n\nLink: https://www.leetcode.com{daily_problem['link']}",
                embed=Embed(title=f"{daily_problem['question']['title']}", description = message))
            '''
            msg.publish()
            return
        else:
            message = "Sorry, I couldn't fetch the daily problem at the moment."        

    except Exception as e:
        # In case of any error, we provide a fallback message
        message = f"An error occurred while fetching the daily problem: {str(e)}"
        print(message)
    msg = await bot.get_channel(channel).send(message)
async def send_scheduled_message():
    await daily(await bot.get_channel(home).send(f'{bot.user} is sending new problem!'))

# Function to check the time and send the message at a specific time
async def schedule_message():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=19, minute=0, second=5, microsecond=0)
        if now > target_time:
            target_time = target_time.replace(day=now.day + 1)
        sleep_duration = (target_time - now).total_seconds()
        print(f"Sending next daily problem in {sleep_duration} seconds...")
        time.sleep(sleep_duration)  # Sleep until the target time
        await send_scheduled_message()  # Run the job after the sleep

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await daily(await bot.get_channel(home).send(f'{bot.user} has connected to Discord!'))
    await schedule_message()

bot.run(TOKEN)
