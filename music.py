import asyncio
from typing import Optional

import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands

DJ_ROL = "ŞARKI MASTER"

YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}
FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
ytdl = yt_dlp.YoutubeDL(YTDL_OPTS)


async def fetch(query: str) -> dict:
    """Arama/link -> {title, url, webpage_url, duration}"""
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
    if "entries" in data:
        data = data["entries"][0]
    return {
        "title": data.get("title", "Bilinmeyen"),
        "url": data["url"],
        "webpage_url": data.get("webpage_url") or query,
        "duration": data.get("duration") or 0,
    }


def sure(sn: int) -> str:
    m, s = divmod(int(sn), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


class GuildState:
    def __init__(self):
        self.queue: list[dict] = []
        self.current: Optional[dict] = None
        self.volume: float = 0.5
        self.loop: bool = False
        self.text_channel: Optional[discord.abc.Messageable] = None


def dj_mi(member: discord.Member) -> bool:
    return member.guild_permissions.administrator or any(r.name == DJ_ROL for r in member.roles)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.states: dict[int, GuildState] = {}

    def state(self, guild_id: int) -> GuildState:
        return self.states.setdefault(guild_id, GuildState())

    # ── çalma döngüsü
    async def play_next(self, guild: discord.Guild):
        st = self.state(guild.id)
        vc = guild.voice_client
        if not vc:
            return
        if st.loop and st.current:
            st.queue.insert(0, st.current)
        if not st.queue:
            st.current = None
            return

        track = st.queue.pop(0)
        st.current = track
        try:
            info = await fetch(track["webpage_url"])  # taze stream linki
        except Exception as e:
            st.current = None
            if st.text_channel:
                await st.text_channel.send(f"❌ **{track['title']}** çalınamadı: {e}")
            return await self.play_next(guild)

        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(info["url"], **FFMPEG_OPTS), volume=st.volume
        )

        def after(err):
            if err:
                print("Oynatma hatası:", err)
            asyncio.run_coroutine_threadsafe(self.play_next(guild), self.bot.loop)

        vc.play(source, after=after)
        if st.text_channel:
            await st.text_channel.send(f"🎶 Şimdi çalıyor: **{track['title']}** `[{sure(track['duration'])}]`")

    async def baglan(self, interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
        uye = interaction.user
        if not uye.voice or not uye.voice.channel:
            await interaction.followup.send("❌ Önce bir ses kanalına gir.", ephemeral=True)
            return None
        vc = interaction.guild.voice_client
        if vc is None:
            vc = await uye.voice.channel.connect()
        elif vc.channel != uye.voice.channel:
            await vc.move_to(uye.voice.channel)
        return vc

    async def dj_kontrol(self, interaction: discord.Interaction) -> bool:
        if not dj_mi(interaction.user):
            await interaction.response.send_message(f"❌ Bu komut için **{DJ_ROL}** rolü lazım.", ephemeral=True)
            return False
        return True

    # ── komutlar
    @app_commands.command(name="cal", description="Şarkı çalar (isim veya YouTube linki)")
    @app_commands.describe(sorgu="Şarkı adı veya link")
    async def cal(self, interaction: discord.Interaction, sorgu: str):
        await interaction.response.defer()
        vc = await self.baglan(interaction)
        if vc is None:
            return
        st = self.state(interaction.guild.id)
        st.text_channel = interaction.channel
        try:
            track = await fetch(sorgu)
        except Exception as e:
            return await interaction.followup.send(f"❌ Bulunamadı: {e}")
        st.queue.append(track)
        if vc.is_playing() or vc.is_paused():
            await interaction.followup.send(f"➕ Kuyruğa eklendi: **{track['title']}** (sıra: {len(st.queue)})")
        else:
            await interaction.followup.send(f"🔎 Bulundu: **{track['title']}**")
            await self.play_next(interaction.guild)

    @app_commands.command(name="gec", description="Çalan şarkıyı geçer (DJ)")
    async def gec(self, interaction: discord.Interaction):
        if not await self.dj_kontrol(interaction):
            return
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            st = self.state(interaction.guild.id)
            loop_onceki, st.loop = st.loop, False
            vc.stop()
            st.loop = loop_onceki
            await interaction.response.send_message("⏭️ Geçildi.")
        else:
            await interaction.response.send_message("❌ Şu an bir şey çalmıyor.", ephemeral=True)

    @app_commands.command(name="duraklat", description="Müziği duraklatır (DJ)")
    async def duraklat(self, interaction: discord.Interaction):
        if not await self.dj_kontrol(interaction):
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Duraklatıldı.")
        else:
            await interaction.response.send_message("❌ Çalan bir şey yok.", ephemeral=True)

    @app_commands.command(name="devam", description="Müziğe devam eder (DJ)")
    async def devam(self, interaction: discord.Interaction):
        if not await self.dj_kontrol(interaction):
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Devam ediyor.")
        else:
            await interaction.response.send_message("❌ Duraklatılmış bir şey yok.", ephemeral=True)

    @app_commands.command(name="dur", description="Müziği durdurur ve kuyruğu temizler (DJ)")
    async def dur(self, interaction: discord.Interaction):
        if not await self.dj_kontrol(interaction):
            return
        st = self.state(interaction.guild.id)
        st.queue.clear()
        st.loop = False
        st.current = None
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
        await interaction.response.send_message("⏹️ Durduruldu, kuyruk temizlendi.")

    @app_commands.command(name="kuyruk", description="Şarkı kuyruğunu gösterir")
    async def kuyruk(self, interaction: discord.Interaction):
        st = self.state(interaction.guild.id)
        if not st.current and not st.queue:
            return await interaction.response.send_message("📭 Kuyruk boş.")
        satirlar = []
        if st.current:
            satirlar.append(f"🎶 **Şimdi:** {st.current['title']}")
        for i, t in enumerate(st.queue[:10], 1):
            satirlar.append(f"`{i}.` {t['title']} `[{sure(t['duration'])}]`")
        if len(st.queue) > 10:
            satirlar.append(f"... ve {len(st.queue) - 10} şarkı daha")
        await interaction.response.send_message("\n".join(satirlar))

    @app_commands.command(name="simdi", description="Şu an çalan şarkıyı gösterir")
    async def simdi(self, interaction: discord.Interaction):
        st = self.state(interaction.guild.id)
        if st.current:
            t = st.current
            await interaction.response.send_message(f"🎶 **{t['title']}** `[{sure(t['duration'])}]`\n{t['webpage_url']}")
        else:
            await interaction.response.send_message("❌ Şu an bir şey çalmıyor.", ephemeral=True)

    @app_commands.command(name="ses", description="Ses seviyesini ayarlar 1-100 (DJ)")
    @app_commands.describe(seviye="1 ile 100 arası")
    async def ses(self, interaction: discord.Interaction, seviye: app_commands.Range[int, 1, 100]):
        if not await self.dj_kontrol(interaction):
            return
        st = self.state(interaction.guild.id)
        st.volume = seviye / 100
        vc = interaction.guild.voice_client
        if vc and vc.source:
            vc.source.volume = st.volume
        await interaction.response.send_message(f"🔊 Ses: %{seviye}")

    @app_commands.command(name="dongu", description="Çalan şarkıyı döngüye alır/kapatır (DJ)")
    async def dongu(self, interaction: discord.Interaction):
        if not await self.dj_kontrol(interaction):
            return
        st = self.state(interaction.guild.id)
        st.loop = not st.loop
        await interaction.response.send_message("🔁 Döngü açık." if st.loop else "➡️ Döngü kapalı.")

    @app_commands.command(name="cik", description="Botu ses kanalından çıkarır (DJ)")
    async def cik(self, interaction: discord.Interaction):
        if not await self.dj_kontrol(interaction):
            return
        st = self.state(interaction.guild.id)
        st.queue.clear()
        st.loop = False
        st.current = None
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("👋 Çıktım.")
        else:
            await interaction.response.send_message("❌ Zaten seste değilim.", ephemeral=True)

    # Kanalda herkes çıkarsa bot da çıksın
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        vc = member.guild.voice_client
        if vc and vc.channel and len([m for m in vc.channel.members if not m.bot]) == 0:
            await asyncio.sleep(60)
            vc = member.guild.voice_client
            if vc and vc.channel and len([m for m in vc.channel.members if not m.bot]) == 0:
                st = self.state(member.guild.id)
                st.queue.clear()
                st.current = None
                await vc.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
