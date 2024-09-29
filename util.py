from pytube. innertube import _default_clients
_default_clients[ "ANDROID"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients[ "ANDROID_EMBED"][ "context"][ "client"]["clientVersion"] = "19.08.35"
_default_clients[ "IOS_EMBED"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"][ "context"]["client"]["clientVersion"] = "6.41"
_default_clients[ "ANDROID_MUSIC"] = _default_clients[ "ANDROID_CREATOR" ]
import requests
import uuid
from PIL import Image
from io import BytesIO
from pytube import YouTube

def download_image(url):
    img_data = requests.get(url).content
    file_name = f"temp/{uuid.uuid4().hex}.jpg"

    with open(file_name, "wb") as handler:
        handler.write(img_data)

    return file_name, Image.open(BytesIO(img_data)) 

def download_youtube_video(url):
    yt = YouTube(url)
    file_name = f"{uuid.uuid4().hex}.mp4"
    print("before")
    print(url)
    # yt.streams.filter(file_extension='mp4', progressive=True)[0].download(filename=file_name, output_path="temp/")
    streams = yt.streams.filter(file_extension="mp4", progressive=True)
    print(streams)
    streams[0].download(filename=file_name, output_path="temp/")
    print("after")
    return f"temp/{file_name}"

if __name__ == "__main__":
    print(download_youtube_video("https://youtu.be/2hPkD9lvVe8?si=o58jdGcQgVtD5NVF"))

