import os
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

# ───────────────────────── ROL AYARLARI ─────────────────────────
# Liste yukarıdan aşağıya hiyerarşi sırasıdır (en üstteki en yetkili).
ROLES = [
    {"name": "ALLAHIN ASLANI", "color": 0xF1C40F, "hoist": True, "perms": {"administrator": True}},
    {"name": "ALLAHIN OĞLU", "color": 0xE67E22, "hoist": True, "perms": {"administrator": True}},
    {"name": "!+!", "color": 0xFFFFFF, "hoist": True, "perms": {"administrator": True}},
    {
        "name": "ALLAHIN TORUNU", "color": 0xD4A017, "hoist": True,
        "perms": {
            "manage_channels": True, "manage_messages": True, "kick_members": True,
            "mute_members": True, "deafen_members": True, "move_members": True,
            "manage_nicknames": True, "view_audit_log": True,
        },
    },
    # Sadece sesten sese atıp çekebilen rol
    {"name": "AT-ÇEK", "color": 0xE74C3C, "hoist": False, "perms": {"move_members": True}},
    {"name": "DDK MASTER", "color": 0x9B59B6, "hoist": True, "perms": {"mute_members": True}},
    {"name": "ADK MASTER", "color": 0x8E44AD, "hoist": True, "perms": {"mute_members": True}},
    {"name": "MDK MASTER", "color": 0xA569BD, "hoist": True, "perms": {"mute_members": True}},
    # Müzik botunu yöneten DJ rolü
    {"name": "ŞARKI MASTER", "color": 0x1ABC9C, "hoist": True, "perms": {"priority_speaker": True, "stream": True}},
    {"name": "DOST", "color": 0x2ECC71, "hoist": True, "perms": {"stream": True, "attach_files": True, "external_emojis": True}},
    {"name": "prenses", "color": 0xFF69B4, "hoist": True, "perms": {"stream": True, "change_nickname": True}},
    {"name": "Regl Olanlar", "color": 0xFF3B7F, "hoist": False, "perms": {}},
    {"name": "yeni rol", "color": 0x95A5A6, "hoist": False, "perms": {}},
    {"name": "Kayıtsız", "color": 0x7F8C8D, "hoist": False, "perms": {}},
]

YETKILI_ROLLER = ["ALLAHIN ASLANI", "ALLAHIN OĞLU", "!+!", "ALLAHIN TORUNU"]
ATCEK_ROL = "AT-ÇEK"
KAYITSIZ_ROL = "Kayıtsız"
KAYITLI_ROL = "yeni rol"
HOSGELDIN_KANAL = "👋┃hoş-geldin"
RESET_SONRASI_KANAL = "komut-kullanım"
RESET_MESAJI = "Fronzy Abi Keyzin Anasını Sik"

# ───────────────────────── KANAL AYARLARI (sosyal / eğlenceli) ─────────────────────────
KATEGORILER = [
    {
        "name": "👋 HOŞ GELDİN", "kayitsiz_gorur": True,
        "text": [
            {"name": HOSGELDIN_KANAL, "readonly": True},
            {"name": "📝┃kayıt", "readonly": True},
        ],
    },
    {
        "name": "📌 ÖNEMLİ",
        "text": [
            {"name": "📢┃duyuru", "readonly": True},
            {"name": "📜┃kurallar", "readonly": True},
            {"name": "🎁┃çekiliş-etkinlik", "readonly": True},
        ],
    },
    {
        "name": "💬 SOSYAL",
        "text": [
            {"name": "💬┃sohbet"},
            {"name": "🤫┃itiraf"},
            {"name": "🤳┃selfie-paylaşım"},
            {"name": "🐸┃meme-diyarı"},
            {"name": "❓┃günün-sorusu"},
            {"name": "🎲┃eğlence-komut"},
        ],
    },
    {
        "name": "🎮 OYUN & FIVEM",
        "text": [
            {"name": "🏙️┃fivem-sohbet"},
            {"name": "🔫┃killpov"},
            {"name": "🎬┃clip-paylaşım"},
            {"name": "🤝┃oyun-arkadaşı-ara"},
            {"name": "🌐┃tahmin-kanalı"},
        ],
    },
    {
        "name": "🎶 MÜZİK",
        "text": [
            {"name": "🎶┃müzik-komut"},
            {"name": "💿┃şarkı-önerileri"},
        ],
        "voice": [
            {"name": "🎵 Müzik Odası 1"},
            {"name": "🎵 Müzik Odası 2"},
            {"name": "🎤 Karaoke"},
        ],
    },
    {
        "name": "🔊 SES ODALARI",
        "voice": [
            {"name": "🔒 Boss office", "gizli": True},
            {"name": "⚽ MAÇ ODASI"},
            {"name": "🔊 -Sohbet 1"},
            {"name": "🔊 -Sohbet 2"},
            {"name": "🔊 -Sohbet 3"},
            {"name": "🎮 Oyun Odası 1", "limit": 5},
            {"name": "🎮 Oyun Odası 2", "limit": 5},
            {"name": "🍿 Film Gecesi"},
            {"name": "🔐 -özel oda-1", "limit": 2},
            {"name": "🔐 -özel oda-2", "limit": 5},
            {"name": "🔐 -özel oda-3", "limit": 2},
            {"name": "😴 AFK", "afk": True},
        ],
    },
]


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("music")
        await self.load_extension("eglence")
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("Komutlar yüklendi.")

    async def on_ready(self):
        print(f"Bot aktif: {self.user}")


bot = Bot()


# ───────────────────────── YARDIMCILAR ─────────────────────────
def rol_bul(guild: discord.Guild, name: str) -> Optional[discord.Role]:
    return discord.utils.get(guild.roles, name=name)


def atcek_yetkisi_var_mi(member: discord.Member) -> bool:
    return member.guild_permissions.administrator or any(r.name == ATCEK_ROL for r in member.roles)


def hedef_korunuyor_mu(guild: discord.Guild, executor: discord.Member, target: discord.Member) -> bool:
    """Hedefin rolü senden yüksek/eşitse işlem yapılamaz (sunucu sahibi hariç)."""
    if guild.owner_id == executor.id:
        return False
    return target.top_role >= executor.top_role


async def roller_kur(guild: discord.Guild):
    bot_pos = guild.me.top_role.position
    olusanlar = []

    for d in ROLES:
        role = rol_bul(guild, d["name"])
        perms = discord.Permissions(**d["perms"])
        colour = discord.Colour(d["color"])
        if role is None:
            role = await guild.create_role(
                name=d["name"], colour=colour, hoist=d["hoist"],
                permissions=perms, mentionable=False, reason="Otomatik kurulum",
            )
        else:
            await role.edit(colour=colour, hoist=d["hoist"], permissions=perms)
        olusanlar.append(role)

    # Botun rolünün hemen altından başlayıp aşağı doğru diz
    positions = {role: max(1, bot_pos - 1 - i) for i, role in enumerate(olusanlar)}
    try:
        await guild.edit_role_positions(positions=positions)
    except discord.HTTPException as e:
        print("Rol sıralaması ayarlanamadı (botun rolünü en üste çek):", e)


async def kanallar_kur(guild: discord.Guild):
    everyone = guild.default_role
    kayitsiz = rol_bul(guild, KAYITSIZ_ROL)
    yetkililer = [r for r in (rol_bul(guild, n) for n in YETKILI_ROLLER) if r]

    for kat in KATEGORILER:
        # Kayıtsızlar sadece "Hoş geldin" kategorisini görür
        kat_ow = {}
        if kayitsiz:
            if kat.get("kayitsiz_gorur"):
                kat_ow[kayitsiz] = discord.PermissionOverwrite(view_channel=True, read_message_history=True)
            else:
                kat_ow[kayitsiz] = discord.PermissionOverwrite(view_channel=False)
        if kat.get("kayitsiz_gorur"):
            kat_ow[everyone] = discord.PermissionOverwrite(send_messages=False)

        category = discord.utils.get(guild.categories, name=kat["name"])
        if category is None:
            category = await guild.create_category(kat["name"], overwrites=kat_ow)
        else:
            await category.edit(overwrites=kat_ow)

        for ch in kat.get("text", []):
            if any(c.name == ch["name"].lower() for c in category.text_channels):
                continue
            ow = dict(kat_ow)
            if ch.get("readonly"):
                ow[everyone] = discord.PermissionOverwrite(send_messages=False)
            await guild.create_text_channel(ch["name"], category=category, overwrites=ow)

        for ch in kat.get("voice", []):
            voice = discord.utils.get(category.voice_channels, name=ch["name"])
            if voice is None:
                ow = dict(kat_ow)
                if ch.get("gizli"):
                    ow[everyone] = discord.PermissionOverwrite(view_channel=False)
                    for r in yetkililer:
                        ow[r] = discord.PermissionOverwrite(view_channel=True, connect=True)
                voice = await guild.create_voice_channel(
                    ch["name"], category=category,
                    user_limit=ch.get("limit", 0), overwrites=ow,
                )
            if ch.get("afk"):
                try:
                    await guild.edit(afk_channel=voice)
                except discord.HTTPException:
                    pass


# ───────────────────────── OLAYLAR ─────────────────────────
@bot.event
async def on_member_join(member: discord.Member):
    role = rol_bul(member.guild, KAYITSIZ_ROL)
    if role:
        await member.add_roles(role, reason="Yeni üye")
    kanal = discord.utils.find(
        lambda c: c.name == HOSGELDIN_KANAL.lower(), member.guild.text_channels
    )
    if kanal:
        await kanal.send(f"🎉 Hoş geldin {member.mention}! Kayıt olmak için yetkililere ulaş, sonra sunucu senin 😎")


# ───────────────────────── KOMUTLAR ─────────────────────────
@bot.tree.command(name="kurulum", description="Tüm rolleri ve kanalları otomatik kurar")
@app_commands.default_permissions(administrator=True)
async def kurulum(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        await roller_kur(interaction.guild)
        await kanallar_kur(interaction.guild)
    except Exception as e:
        return await interaction.followup.send(f"❌ Hata: {e}", ephemeral=True)
    await interaction.followup.send(
        "✅ Kurulum tamam! Roller ve kanallar hazır.\n"
        "Not: Botun rolünü sunucu ayarlarından **en üste** çekersen rol sıralaması tam oturur.",
        ephemeral=True,
    )


@bot.tree.command(name="kayit", description="Kayıtsız üyeyi kayıt eder")
@app_commands.default_permissions(manage_roles=True)
@app_commands.describe(kisi="Kayıt edilecek kişi")
async def kayit(interaction: discord.Interaction, kisi: discord.Member):
    kayitsiz = rol_bul(interaction.guild, KAYITSIZ_ROL)
    kayitli = rol_bul(interaction.guild, KAYITLI_ROL)
    if kayitsiz and kayitsiz in kisi.roles:
        await kisi.remove_roles(kayitsiz)
    if kayitli:
        await kisi.add_roles(kayitli)
    await interaction.response.send_message(f"✅ {kisi.mention} kayıt edildi.")


@bot.tree.command(name="cek", description="Seste olan birini senin odana çeker")
@app_commands.describe(kisi="Çekilecek kişi")
async def cek(interaction: discord.Interaction, kisi: discord.Member):
    uye = interaction.user
    if not atcek_yetkisi_var_mi(uye):
        return await interaction.response.send_message(f"❌ Bu komut için **{ATCEK_ROL}** rolü lazım.", ephemeral=True)
    if not kisi.voice or not kisi.voice.channel:
        return await interaction.response.send_message("❌ Hedef kişi şu an seste değil.", ephemeral=True)
    if not uye.voice or not uye.voice.channel:
        return await interaction.response.send_message("❌ Önce bir ses kanalına girmen lazım.", ephemeral=True)
    if kisi.id != uye.id and hedef_korunuyor_mu(interaction.guild, uye, kisi):
        return await interaction.response.send_message("❌ Rolü senden yüksek/eşit birine dokunamazsın.", ephemeral=True)

    await kisi.move_to(uye.voice.channel, reason=f"{uye} çekti")
    await interaction.response.send_message(f"🧲 {kisi.mention} → **{uye.voice.channel.name}** odasına çekildi.")


@bot.tree.command(name="at", description="Seste olan birini başka bir ses kanalına atar")
@app_commands.describe(kisi="Atılacak kişi", kanal="Gidecek ses kanalı (boşsa AFK, AFK yoksa sesten atar)")
async def at(interaction: discord.Interaction, kisi: discord.Member, kanal: Optional[discord.VoiceChannel] = None):
    uye = interaction.user
    if not atcek_yetkisi_var_mi(uye):
        return await interaction.response.send_message(f"❌ Bu komut için **{ATCEK_ROL}** rolü lazım.", ephemeral=True)
    if not kisi.voice or not kisi.voice.channel:
        return await interaction.response.send_message("❌ Hedef kişi şu an seste değil.", ephemeral=True)
    if kisi.id != uye.id and hedef_korunuyor_mu(interaction.guild, uye, kisi):
        return await interaction.response.send_message("❌ Rolü senden yüksek/eşit birine dokunamazsın.", ephemeral=True)

    hedef_kanal = kanal or interaction.guild.afk_channel
    await kisi.move_to(hedef_kanal, reason=f"{uye} attı")  # None = sesten atar
    if hedef_kanal:
        await interaction.response.send_message(f"🚀 {kisi.mention} → **{hedef_kanal.name}** kanalına atıldı.")
    else:
        await interaction.response.send_message(f"🚀 {kisi.mention} sesten atıldı.")


@bot.tree.command(name="reset", description="TÜM kanalları ve rolleri siler, sunucuyu sıfırlar (GERİ ALINAMAZ)")
@app_commands.default_permissions(administrator=True)
async def reset(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)

    # Kanalları sil
    for ch in list(guild.channels):
        try:
            await ch.delete(reason="/reset")
        except discord.HTTPException:
            pass

    # Rolleri sil (@everyone, botun kendi rolü ve entegrasyon rolleri hariç)
    for role in list(guild.roles):
        if role.is_default() or role.managed or role >= guild.me.top_role:
            continue
        try:
            await role.delete(reason="/reset")
        except discord.HTTPException:
            pass

    # Tek kanalı aç
    yeni_kanal = await guild.create_text_channel(RESET_SONRASI_KANAL)
    await yeni_kanal.send(RESET_MESAJI)

    await interaction.followup.send("✅ Sunucu sıfırlandı.", ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN)
