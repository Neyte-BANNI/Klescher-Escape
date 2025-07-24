import discord
from discord import app_commands
from discord.ext import commands
import os
import math
import re

# === KEEP ALIVE (Flask hack pour Render Web Service) ===
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot Discord en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === CONFIGURATION ===
TOKEN = os.environ["TOKEN"]
LOGO_URL = "https://i.ibb.co/zV62F61G/lesbannis.png"
BANNER_URL = "https://i.ibb.co/bRd0QbLB/imageBB.png"
TIGERCLAW_MERITS = 1876

# === INITIALISATION DISCORD ===
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# === FONCTIONS UTILITAIRES ===
def parse_time_string(time_str: str) -> tuple:
    # Accepte "11h18", "11h", "18m", "11h18m", "90m", "11h 18"
    match = re.match(r'^\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*$', time_str)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours, minutes
    # Accepte aussi "11h18" sans le "m" final (ex : 11h18, 2h5, 3h 07)
    match2 = re.match(r'^\s*(\d+)\s*h\s*(\d{1,2})\s*$', time_str)
    if match2:
        hours = int(match2.group(1))
        minutes = int(match2.group(2))
        return hours, minutes
    return 0, 0

def calculate_merits(hours: int, minutes: int) -> tuple:
    total_minutes = hours * 60 + minutes
    merits = total_minutes * 60  # 1 merit = 1 seconde
    merits_with_fee = math.ceil(merits * 1.005)  # +0.5%
    return merits, merits_with_fee

def calculate_time(merits: int) -> tuple:
    total_minutes = merits / 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    return hours, minutes

def calculate_tigerclaws(merits: int) -> int:
    return math.ceil(merits / TIGERCLAW_MERITS)

# === COMMANDE /convert ===
@bot.tree.command(name="convert", description="Convertit automatiquement entre temps (ex: 12h45) et merits (ex: 45900)")
@app_commands.describe(value="Durée (ex: 12h45 ou 11h18) ou nombre de merits (ex: 45900)")
async def convert(interaction: discord.Interaction, value: str):
    if value.isdigit():
        merits = int(value)
        hours, minutes = calculate_time(merits)
        tigerclaws = calculate_tigerclaws(merits)
        embed = discord.Embed(
            title="⏳ Conversion Merits ➝ Temps",
            description=f"**{merits} merits** correspondent à :",
            color=0x8B0000
        )
        embed.add_field(name="⏱️ Temps", value=f"**{hours}h {minutes}m**", inline=False)
        embed.add_field(
            name="🔑 Tigerclaws nécessaires",
            value=f"**{tigerclaws} Tigerclaw(s)**",
            inline=False
        )
        embed.set_thumbnail(url=LOGO_URL)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Les Bannis • Star Citizen", icon_url=LOGO_URL)
        await interaction.response.send_message(embed=embed)
        return

    hours, minutes = parse_time_string(value)
    if hours == 0 and minutes == 0:
        await interaction.response.send_message("❌ Format invalide. Exemple : `12h45`, `11h18` ou `45900`")
        return

    merits_needed, merits_fee = calculate_merits(hours, minutes)
    tigerclaws_needed = calculate_tigerclaws(merits_needed)
    tigerclaws_fee = calculate_tigerclaws(merits_fee)
    embed = discord.Embed(
        title="⚒️ Conversion Temps ➝ Merits",
        description=f"**{hours}h {minutes}m** correspondent à :",
        color=0x8B0000
    )
    embed.add_field(name="🎖️ Merits nécessaires", value=f"**{merits_needed}**", inline=True)
    embed.add_field(name="💰 Avec 0.5% fee", value=f"**{merits_fee}**", inline=True)
    embed.add_field(
        name="🔑 Tigerclaws nécessaires",
        value=f"**{tigerclaws_needed} Tigerclaw(s)**",
        inline=False
    )
    embed.add_field(
        name="🔑 Tigerclaws (avec 0.5% fee)",
        value=f"**{tigerclaws_fee} Tigerclaw(s)**",
        inline=False
    )
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Les Bannis • Star Citizen", icon_url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté en tant que {bot.user}")

# === LANCEMENT (Web Service mode) ===
keep_alive()  # <= INDISPENSABLE pour Render Web Service !
bot.run(TOKEN)
