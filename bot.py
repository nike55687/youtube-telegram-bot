import os
import time
import subprocess
from telegram import Bot

# گرفتن اطلاعات از محیط (بعداً در GitHub Secrets می‌گذاریم)
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(token=TOKEN)

# تنظیمات
MAX_DURATION = 30 * 60  # 30 دقیقه به ثانیه
DOWNLOAD_PATH = "downloads"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)


def get_video_duration(url):
    """گرفتن مدت زمان ویدیو با yt-dlp"""
    cmd = [
        "yt-dlp",
        "--get-duration",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = result.stdout.strip()

    if not duration:
        return None

    parts = duration.split(":")
    if len(parts) == 2:
        m, s = map(int, parts)
        return m * 60 + s
    elif len(parts) == 3:
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s

    return None


def download_video(url):
    """دانلود ویدیو"""
    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",
        "-o", f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",
        url
    ]
    subprocess.run(cmd)


def send_to_telegram(file_path, title):
    """ارسال به تلگرام"""
    with open(file_path, "rb") as video:
        bot.send_video(
            chat_id=CHAT_ID,
            video=video,
            caption=title
        )


def main():
    # فعلاً تستی یک ویدیو می‌گیریم (بعداً خودکار می‌شود)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    duration = get_video_duration(test_url)

    if duration and duration > MAX_DURATION:
        print("Video too long, skipped")
        return

    download_video(test_url)

    # پیدا کردن فایل دانلود شده
    files = os.listdir(DOWNLOAD_PATH)
    if not files:
        return

    latest_file = max(
        [os.path.join(DOWNLOAD_PATH, f) for f in files],
        key=os.path.getctime
    )

    send_to_telegram(latest_file, "Test Video")


if __name__ == "__main__":
    main()
