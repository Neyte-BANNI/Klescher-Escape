import discord
from discord import app_commands
from discord.ext import commands
import os
import math
import re
import threading
from flask import Flask

# --- CONFIGURATION ---
TOKEN = os.environ["TOKEN"]  # Token Discord (variable d'environnement sur Render)
LOGO_URL = "https://i.ibb.co/xt2ycnL4/Chat-GPT-Image-12-juil-2025-07-30-20.png"
BANNER_URL = "https://i.ibb.co/xt2ycnL4/Chat-GPT-Image-12-juil-2025-07-30-20.png"

# --- SERVEUR FLASK KEEP-ALIVE ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Les Bannis actif !"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

threading.Thread(target=run_flask).start()

# --- INITIALISATION DU BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FONCTIONS UTILITAIRES ---
def parse_time_string(time_str: str) -> tuple:
    time_str = time_str.lower().replace(" ", "")

    # Vérifier si le format est 11:24
    match_colon = re.match(r'(\d{1,2}):(\d{1,2})$', time_str)
    if match_colon:
        return int(match_colon.group(1)), int(match_colon.group(2))

    # Vérifier le format 11h24, 11h, 24m
    match = re.match(r'(?:(\d{1,2})h)?(?:(\d{1,2})m)?$', time_str)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
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

# --- COMMANDE /convert ---
@bot.tree.command(name="convert", description="Convertit automatiquement entre temps (ex: 12h45) et merits (ex: 45900)")
@app_commands.describe(value="Durée (ex: 12h45) ou nombre de merits (ex: 45900)")
async def convert(interaction: discord.Interaction, value: str):
    if value.isdigit():
        merits = int(value)
        hours, minutes = calculate_time(merits)
        embed = discord.Embed(
            title="⏳ Conversion Merits ➝ Temps",
            description=f"**{merits} merits** correspondent à :",
            color=0x8B0000
        )
        embed.add_field(name="⏱️ Temps", value=f"**{hours}h {minutes}m**", inline=False)
        embed.set_thumbnail(url=LOGO_URL)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Les Bannis • Star Citizen", icon_url=LOGO_URL)
        await interaction.response.send_message(embed=embed)
        return

    hours, minutes = parse_time_string(value)
    if hours == 0 and minutes == 0:
        await interaction.response.send_message("❌ Format invalide. Exemple : `12h45`, `11:24` ou `45900`")
        return

    merits_needed, merits_fee = calculate_merits(hours, minutes)
    embed = discord.Embed(
        title="⚒️ Conversion Temps ➝ Merits",
        description=f"**{hours}h {minutes}m** correspondent à :",
        color=0x8B0000
    )
    embed.add_field(name="🎖️ Merits nécessaires", value=f"**{merits_needed}**", inline=True)
    embed.add_field(name="💰 Avec 0.5% fee", value=f"**{merits_fee}**", inline=True)
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text="Les Bannis • Star Citizen", icon_url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté en tant que {bot.user}")

# --- LANCEMENT ---
bot.run(TOKEN)
