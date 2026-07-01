import subprocess
import os

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

SENT_FILE = "sent_videos.txt"
CHANNELS_FILE = "channels.txt"


def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(f.read().splitlines())


def save_sent(video_id):
    with open(SENT_FILE, "a") as f:
        f.write(video_id + "\n")


def get_latest_videos(channel_url):
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s|%(duration)s|%(title)s|%(url)s",
        channel_url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    return lines


def download_video(url):
    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",
        "-o", f"{DOWNLOAD_PATH}/%(id)s.%(ext)s",
        url
    ]
    subprocess.run(cmd)


def main():
    sent = load_sent()

    with open(CHANNELS_FILE, "r") as f:
        channels = f.read().splitlines()

    for channel in channels:
        videos = get_latest_videos(channel)

        for v in videos:
            try:
                vid_id, duration, title, url = v.split("|")

                # جلوگیری از تکراری
                if vid_id in sent:
                    continue

                # فیلتر ۳۰ دقیقه
                if duration.isdigit() and int(duration) > 1800:
                    continue

                download_video(url)

                file_path = None
                for f in os.listdir(DOWNLOAD_PATH):
                    if vid_id in f:
                        file_path = os.path.join(DOWNLOAD_PATH, f)

                if file_path:
                    send_to_telegram(file_path, title)

                save_sent(vid_id)

            except:
                continue


if __name__ == "__main__":
    main()
