import os
import time
import random
import shutil
import requests
import subprocess
import yt_dlp
import whisper
import cloudinary
import cloudinary.uploader

# Buffer API Token
BUFFER_API_KEY = "FKSkzewtjeWRLoHrFtF0OT_iFJLR0VBnFfH9fRF7ZIB"
BUFFER_URL = "https://api.buffer.com"

# Cloudinary Configuration
cloudinary.config(
    cloud_name="xnjaxvto",
    api_key="636698659882116",
    api_secret="dk_rREtARWfV5f3QrJRq-h014Kw",
    secure=True
)

# Har channel ke saath uski service
BUFFER_CHANNELS = [
    {"id": "6aba3829ea19ca0bde10cfca", "service": "facebook"},
    {"id": "6aba37f7ea19ca0bde10ceb6", "service": "youtube"},
    {"id": "6aba37dcea19ca0bde10ce22", "service": "instagram"},
]
COOKIES_PATH = "cookies.txt"

# Video layout mode:
#   "blur"     -> poori video dikhegi (koi crop nahi), 1080x1920 vertical frame mein,
#                 upar/neeche blurred background. Facebook, YouTube Shorts, Instagram teeno accept karenge.
#   "original" -> bilkul original size (horizontal video Facebook/YouTube Shorts par reject hogi)
VIDEO_MODE = "blur"

# FFmpeg path: pehle system PATH mein dhundhega, nahi mila to neeche wala path try karega
FFMPEG_PATH = shutil.which("ffmpeg") or "C:\\ffmpeg\\bin\\ffmpeg.exe"
if not os.path.exists(FFMPEG_PATH):
    raise SystemExit(
        f"❌ FFmpeg nahi mila: {FFMPEG_PATH}\n"
        "Install karo: winget install Gyan.FFmpeg  (phir terminal naya kholo)"
    )
FFMPEG_DIR = os.path.dirname(FFMPEG_PATH)

# Whisper andar se "ffmpeg" naam se call karta hai, isliye folder ko PATH mein jod do
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
print(f"🎬 FFmpeg mila: {FFMPEG_PATH}")

print("🧠 Loading Whisper AI Model...")
whisper_model = whisper.load_model("base")

# Anime Topics ki list
ANIME_TOPICS = [
    "Gojo Satoru domain expansion JJK",
    "Sukuna vs Gojo epic fight JJK",
    "Toji Fushiguro badass moments JJK",
    "Yuji Itadori Black Flash JJK",
    "Naruto Uzumaki Rasenshuriken epic moments",
    "Sasuke Uchiha Chidori edit",
    "Kakashi Hatake Sharingan moments",
    "Madara Uchiha vs Shinobi Alliance",
    "Itachi Uchiha Tsukuyomi edit",
    "Tanjiro Kamado Hinokami Kagura Demon Slayer",
    "Inosuke Hashibira funny moments Demon Slayer",
    "Nezuko blood demon art edit",
    "Zenitsu Thunder Breathing God Speed",
    "Zoro Ashura mode One Piece",
    "Luffy Gear 5 laughing drums One Piece",
    "Sanji Diable Jambe edit One Piece",
    "Goku Ultra Instinct mastery DBZ",
    "Vegeta Final Flash epic moment",
    "Eren Yeager Founding Titan transformation AOT",
    "Levi Ackerman vs Beast Titan",
    "Ichigo Kurosaki Bankai hollow mask Bleach"
]


def upload_to_temp_host(file_path):
    print("🌐 Uploading video to Cloudinary...")
    try:
        response = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            folder="anime_shorts"
        )
        if "secure_url" in response:
            public_url = response["secure_url"]
            print(f"✅ Cloudinary Upload Successful: {public_url}")
            return public_url
    except Exception as e:
        print(f"⚠️ Cloudinary Upload error: {e}")
    return None


def download_video(search_keyword, temp_video):
    print(f"\n🔍 Searching & Downloading: '{search_keyword}'...")
    if os.path.exists(temp_video):
        os.remove(temp_video)

    # Step 1: Top 5 videos search karke random select karna
    search_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}
    }

    video_url = None
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            result = ydl.extract_info(f"ytsearch5:{search_keyword} shorts", download=False)
            entries = result.get('entries', [])
            if entries:
                chosen = random.choice(entries)
                video_url = chosen.get('url') or f"https://www.youtube.com/watch?v={chosen.get('id')}"
    except Exception as e:
        print(f"❌ Search Failed: {e}")
        return False

    if not video_url:
        print("❌ No video found.")
        return False

    print(f"🔗 Selected Random Video URL: {video_url}")

    # Step 2: FFmpeg location pass karke video aur audio dono ko properly merge karna
    ydl_opts = {
        'outtmpl': temp_video,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'ffmpeg_location': FFMPEG_DIR,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if not os.path.exists(temp_video):
            print("❌ Download ke baad file nahi bani (shayad merge fail hua).")
        elif os.path.getsize(temp_video) <= 500000:
            print("❌ File bahut choti hai, download adhura raha.")
        else:
            print("✅ Download Completed with Audio Merged!")
            return True
    except Exception as e:
        print(f"❌ Download Failed: {e}")

    return False


def generate_srt(video_path, srt_path):
    print("🎙️ Generating Subtitles...")
    result = whisper_model.transcribe(video_path)
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"]):
            start = time.strftime("%H:%M:%S,000", time.gmtime(segment["start"]))
            end = time.strftime("%H:%M:%S,000", time.gmtime(segment["end"]))
            f.write(f"{i+1}\n{start} --> {end}\n{segment['text'].strip()}\n\n")


CREATE_POST_MUTATION = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id status } }
    ... on MutationError { message }
  }
}
"""


def build_metadata(service, caption):
    if service == "instagram":
        return {"instagram": {"type": "reel", "shouldShareToFeed": True}}
    if service == "facebook":
        return {"facebook": {"type": "reel"}}
    if service == "youtube":
        return {"youtube": {
            "title": caption[:100],
            "categoryId": "24",
            "privacy": "public",
        }}
    return None


def push_to_buffer(local_file_path, caption):
    if not BUFFER_API_KEY:
        print("⚠️ Buffer skipped: BUFFER_API_KEY set nahi hai.")
        return

    public_url = upload_to_temp_host(local_file_path)
    if not public_url:
        print("⚠️ Buffer skipped: Cloudinary link failed.")
        return

    headers = {"Authorization": f"Bearer {BUFFER_API_KEY}", "Content-Type": "application/json"}

    for ch in BUFFER_CHANNELS:
        post_input = {
            "channelId": ch["id"],
            "schedulingType": "automatic",
            "mode": "addToQueue",
            "text": caption,
            "assets": [{"video": {"url": public_url}}],
        }
        meta = build_metadata(ch["service"], caption)
        if meta:
            post_input["metadata"] = meta

        try:
            print(f"🚀 Sending to Buffer ({ch['service']}) Channel ID: {ch['id']}...")
            res = requests.post(
                BUFFER_URL,
                json={"query": CREATE_POST_MUTATION, "variables": {"input": post_input}},
                headers=headers,
                timeout=60,
            )
            print(f"📥 Buffer Response Status: {res.status_code}")
            data = res.json()
            print(f"📥 Buffer Response Body: {data}")

            if data.get("errors"):
                print(f"❌ GraphQL error: {data['errors']}")
            else:
                result = (data.get("data") or {}).get("createPost") or {}
                if "post" in result:
                    print(f"✅ Queued on {ch['service']}: post id {result['post']['id']}")
                elif "message" in result:
                    print(f"❌ Buffer refused ({ch['service']}): {result['message']}")
        except Exception as e:
            print(f"❌ Buffer API Error: {e}")


def build_ffmpeg_command(temp_v, temp_s, out_v, has_srt):
    escaped_srt = temp_s.replace(":", "\\:").replace("'", "\\'")
    sub_style = (
        f"subtitles='{escaped_srt}':force_style='FontSize=20,Bold=1,PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2'"
    )
    base = [FFMPEG_PATH, "-y", "-i", temp_v, "-t", "60"]
    encode = ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
              "-c:a", "aac", "-b:a", "128k", out_v]

    if VIDEO_MODE == "blur":
        # Poori video (bina crop) 1080x1920 frame ke beech mein, peeche blurred copy
        fc = (
            "[0:v]fps=30,split=2[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bgb];"
            "[fg]scale=1080:1920:force_original_aspect_ratio=decrease:force_divisible_by=2[fgs];"
            "[bgb][fgs]overlay=(W-w)/2:(H-h)/2"
        )
        if has_srt:
            fc += "," + sub_style
        return base + ["-filter_complex", fc] + encode

    # "original": sirf even dimensions, ratio same
    vf = "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2"
    if has_srt:
        vf += "," + sub_style
    return base + ["-vf", vf] + encode


def process(keyword, output_name):
    temp_v = f"temp_{output_name}.mp4"
    temp_s = f"temp_{output_name}.srt"
    out_v = f"{output_name}.mp4"

    if not download_video(keyword, temp_v):
        return

    has_srt = False
    try:
        generate_srt(temp_v, temp_s)
        has_srt = os.path.exists(temp_s)
    except Exception as e:
        print(f"⚠️ Subtitles skip (error): {e}")

    print(f"🎞️ Rendering Video (Max 60s, mode: {VIDEO_MODE})...")
    cmd = build_ffmpeg_command(temp_v, temp_s, out_v, has_srt)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("❌ FFmpeg error:\n", result.stderr[-1500:])
        return

    if os.path.exists(out_v) and os.path.getsize(out_v) > 1000000:
        caption = f"🔥 {keyword.title()} #anime #shorts #viral #reels"
        push_to_buffer(out_v, caption)
    else:
        print("❌ Output video nahi bani ya bahut choti hai.")

    for f in [temp_v, temp_s, out_v]:
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    selected_topic = random.choice(ANIME_TOPICS)
    process(selected_topic, "anime_short")