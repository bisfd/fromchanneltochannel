import asyncio
import os
import yt_dlp
import sqlite3
from aiogram import Bot

# Настройки
TOKEN = "7545025311:AAFCLcyRPmVDAn5ROLg6Qxlreaf3IspeYbw"
CHAT_ID = "@ttwicsurvideo"  # или ID канала
YOUTUBE_CHANNEL = "https://www.youtube.com/@BISKASYT"
DB_FILE = "videos.db"

bot = Bot(token=TOKEN)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS videos (video_id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

def is_new(video_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM videos WHERE video_id=?", (video_id,))
    exists = cur.fetchone()
    if not exists:
        cur.execute("INSERT INTO videos (video_id) VALUES (?)", (video_id,))
        conn.commit()
    conn.close()
    return not exists

async def download_and_post(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_name = ydl.prepare_filename(info)
        title = info.get('title')
        date = info.get('upload_date')  # формат YYYYMMDD
        date_formatted = f"{date[6:8]}.{date[4:6]}.{date[0:4]}"
        
    caption = f"🎥 {title}\nБИСКАС\nВыпущено: {date_formatted}\n#шортс #гонка_имён #Бискас"
    
    await bot.send_video(CHAT_ID, video=open(file_name, "rb"), caption=caption)
    os.remove(file_name)

async def main():
    init_db()
    while True:
        # Получаем список видео
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(YOUTUBE_CHANNEL, download=False)
            entries = info.get('entries', [])
            for video in entries:
                video_id = video.get('id')
                url = f"https://www.youtube.com/watch?v={video_id}"
                if is_new(video_id):
                    await download_and_post(url)
        await asyncio.sleep(600)  # проверка каждые 10 минут

if __name__ == "__main__":
    asyncio.run(main())
