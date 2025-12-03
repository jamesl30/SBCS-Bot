import os
import discord
import requests
from discord.ext import commands
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

# Discord configuration
TOKEN = os.getenv("token")
CHANNEL_ID = 827652217901154375

# Advent of Code configuration
AOC_SESSION = os.getenv("AOC_SESSION")
AOC_LEADERBOARD_ID = os.getenv("AOC_LEADERBOARD_ID")
AOC_YEAR = os.getenv("AOC_YEAR", "2025")

# Build AoC API URL
AOC_URL = f"https://adventofcode.com/{AOC_YEAR}/leaderboard/private/view/{AOC_LEADERBOARD_ID}.json"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def fetch_leaderboard():
    """Fetch the private leaderboard JSON from Advent of Code."""
    if not AOC_SESSION:
        raise ValueError("AOC_SESSION environment variable is not set")
    if not AOC_LEADERBOARD_ID:
        raise ValueError("AOC_LEADERBOARD_ID environment variable is not set")

    cookies = {"session": AOC_SESSION}
    headers = {
        "User-Agent": "SBCS-Bot Discord Bot (https://github.com/sbcs/SBCS-Bot)"
    }

    response = requests.get(AOC_URL, cookies=cookies, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise ValueError("Invalid session cookie - please update AOC_SESSION")
    else:
        raise ValueError(f"Failed to fetch leaderboard: HTTP {response.status_code}")


def format_leaderboard(data):
    """Format leaderboard data into a Discord embed."""
    members = data.get("members", {})
    event_year = data.get("event", AOC_YEAR)

    # Filter active members (stars >= 1) and sort by local_score descending
    active_members = [
        member for member in members.values()
        if member.get("stars", 0) >= 1
    ]

    # Sort by local_score (descending), then by last_star_ts (ascending for tiebreaker)
    active_members.sort(key=lambda m: (-m.get("local_score", 0), m.get("last_star_ts", 0)))

    # Build leaderboard text
    if not active_members:
        leaderboard_text = "*No active participants yet. Be the first to earn a star!*"
    else:
        lines = []
        for i, member in enumerate(active_members, 1):
            name = member.get("name") or f"Anonymous #{member.get('id', '?')}"
            stars = member.get("stars", 0)
            score = member.get("local_score", 0)

            # Medal emojis for top 3
            if i == 1:
                prefix = "\U0001F947"  # Gold medal
            elif i == 2:
                prefix = "\U0001F948"  # Silver medal
            elif i == 3:
                prefix = "\U0001F949"  # Bronze medal
            else:
                prefix = f"{i}."

            lines.append(f"{prefix} **{name}** — {stars}\u2b50 ({score} pts)")

        leaderboard_text = "\n".join(lines)

    # Get current timestamp
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    timestamp = now.strftime("%B %d, %Y at %I:%M %p EST")

    # Create embed
    embed = discord.Embed(
        title=f"\U0001F384 Advent of Code {event_year} Leaderboard",
        description=leaderboard_text,
        color=0x2F855A  # Green color
    )

    embed.set_footer(text=f"Last updated: {timestamp}")
    embed.add_field(
        name="\U0001F517 Join the Leaderboard",
        value=f"**Code:** `4312390-e0e2e1f4`\n[View Leaderboard](https://adventofcode.com/2025/leaderboard/private/view/4312390?view_key=39391480)",
        inline=False
    )

    return embed


async def post_leaderboard():
    """Fetch and post the AoC leaderboard to Discord."""
    print("Fetching Advent of Code leaderboard...")

    try:
        data = fetch_leaderboard()
        embed = format_leaderboard(data)

        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"Error: Could not find channel {CHANNEL_ID}")
            await bot.close()
            return

        await channel.send(embed=embed)
        print(f"Posted AoC leaderboard to channel {CHANNEL_ID}")

    except ValueError as e:
        print(f"Configuration error: {e}")
    except requests.RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    await bot.close()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await post_leaderboard()


if __name__ == "__main__":
    if not TOKEN:
        print("Error: Discord token not set. Please set 'token' in .env file")
    else:
        bot.run(TOKEN)
