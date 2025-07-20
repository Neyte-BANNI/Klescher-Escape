import discord
from discord import app_commands
from discord.ext import commands
import os
import math
import re

# --- CONFIGURATION ---
TOKEN = os.environ["TOKEN"]  # Token Discord (ajouté dans Koyeb Environment Variables)
LOGO_URL = "https://i.ibb.co/xt2ycnL4/Chat-GPT-Image-12-juil-2025-07-30-20.png"
BANNER_URL = "https://i.ibb.co/xt2ycnL4/Chat-GPT-Image-12-juil-2025-07-30-20.png"

# --- INITIALISATION ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FONCTIONS UTILITAIRES ---
def parse_time_string(time_str: str) -> tuple:
    hours = 0
    minutes = 0
    match = re.match(r'(?:(\d+)h)?(?:(\d+)m)?$', time_str)
    if match:
        if match.group(1):
            hours = int(match.group(1))
        if match.group(2):
            minutes = int(match.group(2))
    return hours, minutes

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
        await interaction.response.send_message("❌ Format invalide. Exemple : `12h45` ou `45900`")
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