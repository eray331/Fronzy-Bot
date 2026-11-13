import hashlib
import random

import discord
from discord import app_commands
from discord.ext import commands

SORU_CEVAPLARI = [
    "Kesinlikle evet 😎", "Hayır kanka 💀", "Belki... bir de sen düşün 🤔",
    "Büyük ihtimalle evet", "Hiç sanmıyorum", "Aynen aynen 🔥",
    "Sonra tekrar sor, kafam yok 😴", "Yüzde yüz!",
]


class Eglence(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="zar", description="Zar atar")
    @app_commands.describe(yuz="Zarın yüz sayısı (varsayılan 6)")
    async def zar(self, interaction: discord.Interaction, yuz: app_commands.Range[int, 2, 1000] = 6):
        await interaction.response.send_message(f"🎲 {interaction.user.mention} attı: **{random.randint(1, yuz)}** (1-{yuz})")

    @app_commands.command(name="yazitura", description="Yazı tura atar")
    async def yazitura(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🪙 **{random.choice(['YAZI', 'TURA'])}** geldi!")

    @app_commands.command(name="sec", description="Seçenekler arasından birini seçer (virgülle ayır)")
    @app_commands.describe(secenekler="Örn: pizza, burger, döner")
    async def sec(self, interaction: discord.Interaction, secenekler: str):
        liste = [s.strip() for s in secenekler.split(",") if s.strip()]
        if len(liste) < 2:
            return await interaction.response.send_message("❌ En az 2 seçenek yaz (virgülle ayır).", ephemeral=True)
        await interaction.response.send_message(f"🤔 Benim seçimim: **{random.choice(liste)}**")

    @app_commands.command(name="sor", description="Bota evet/hayır sorusu sor")
    @app_commands.describe(soru="Sorun")
    async def sor(self, interaction: discord.Interaction, soru: str):
        await interaction.response.send_message(f"❓ {soru}\n🎱 {random.choice(SORU_CEVAPLARI)}")

    @app_commands.command(name="ship", description="İki kişinin uyumunu ölçer")
    async def ship(self, interaction: discord.Interaction, kisi1: discord.Member, kisi2: discord.Member):
        ids = "-".join(sorted([str(kisi1.id), str(kisi2.id)]))
        oran = int(hashlib.md5(ids.encode()).hexdigest(), 16) % 101
        bar = "█" * (oran // 10) + "░" * (10 - oran // 10)
        await interaction.response.send_message(f"💘 {kisi1.mention} x {kisi2.mention}\n`{bar}` **%{oran}**")

    @app_commands.command(name="anket", description="Hızlı evet/hayır anketi açar")
    @app_commands.describe(soru="Anket sorusu")
    async def anket(self, interaction: discord.Interaction, soru: str):
        await interaction.response.send_message(f"📊 **{soru}**")
        mesaj = await interaction.original_response()
        await mesaj.add_reaction("✅")
        await mesaj.add_reaction("❌")


async def setup(bot: commands.Bot):
    await bot.add_cog(Eglence(bot))
