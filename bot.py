from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp, os, asyncio, re

# 🔹 بيانات البوت
API_ID = 36461220
API_HASH = "4606e5a2c60e92befc9de30c9a8851bd"
BOT_TOKEN = "8506660351:AAElbJAA7-3BuaJwufbdDrCyz6O5VSa6z18"

GROUP_LINK = "https://t.me/H2OT3"
BUTTON_NAME = "Николас"

app = Client("musicbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
semaphore = asyncio.Semaphore(5)

# 🔹 رابط الصورة من الإنترنت
IMAGE_URL = "https://p2.piqsels.com/preview/400/854/479/silhouette-wallpaper-music-wallpapers-music-background.jpg"

# 🔹 /start مضمون مع الصورة + كليشة + زر
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_photo(
        photo=IMAGE_URL,
        caption="🎧 اهلا بك في ميوزك گروع\n\nاكتب yt أو يوت + اسم الأغنية",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(BUTTON_NAME, url=GROUP_LINK)]]
        )
    )

# 🔹 البحث على يوتيوب
def search(query):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    return info['webpage_url'], info['title']

# 🔹 تحميل الأغاني
async def download_audio(url, title):
    os.makedirs("cache", exist_ok=True)
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    file_name = f"cache/{safe_title}.m4a"

    if os.path.exists(file_name):
        return file_name

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "outtmpl": file_name,
    }

    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await loop.run_in_executor(None, lambda: ydl.download([url]))

    return file_name

# 🔹 تشغيل الأغاني
@app.on_message(filters.text)
async def play(client, message):
    text = message.text.strip()
    match = re.match(r"^(yt|يوت)\s*(.+)", text, re.IGNORECASE)
    if not match:
        return

    query = match.group(2)
    msg = await message.reply("⏳ جار التحميل...")

    try:
        url, title = search(query)
        async with semaphore:
            file_path = await download_audio(url, title)

        await msg.delete()
        await message.reply_audio(
            audio=file_path,
            title=title,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(BUTTON_NAME, url=GROUP_LINK)]]
            )
        )

    except Exception as e:
        await msg.edit(f"❌ خطأ: {e}")

# 🔹 تشغيل البوت
app.run()
