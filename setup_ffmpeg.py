import os
import urllib.request
import zipfile
import shutil

url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
zip_path = "ffmpeg.zip"
extract_path = "C:\\ffmpeg"

print("📥 Downloading FFmpeg for Windows...")
try:
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except:
            pass

    urllib.request.urlretrieve(url, zip_path)
    print("✅ Download Complete!")

    print("📂 Extracting files to C:\\ffmpeg...")
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path, ignore_errors=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("C:\\temp_ffmpeg")

    extracted_folders = os.listdir("C:\\temp_ffmpeg")
    for folder in extracted_folders:
        old_dir = os.path.join("C:\\temp_ffmpeg", folder)
        if os.path.isdir(old_dir):
            os.rename(old_dir, extract_path)
            break

    # Cleanup
    shutil.rmtree("C:\\temp_ffmpeg", ignore_errors=True)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    print("🚀 FFmpeg successfully installed at C:\\ffmpeg!")

except Exception as e:
    print(f"❌ Error: {e}")