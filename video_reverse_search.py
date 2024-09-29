from pytube import YouTube
from google_img_source_search import ReverseImageSearcher
import os
from Katna.video import Video
from Katna.writer import KeyFrameDiskWriter
import uuid
import shutil
from aging import diff_finder

def download_video(link, output_path="tests", filename="vid.mp4"):
    print("downloading...")
    yt = YouTube(link)
    yt.streams.filter(file_extension='mp4', progressive=True)[0].download(filename=filename, output_path=output_path)
    print("download complete!!")
    return os.path.join(output_path, filename)

def extract_keyframes(video_file_path, output_folder="selectedframes", no_of_frames=4):
    print("extracting keyframes")
    vd = Video()
    diskwriter = KeyFrameDiskWriter(location=output_folder)
    vd.extract_video_keyframes(
        no_of_frames=no_of_frames, file_path=video_file_path,
        writer=diskwriter
    )
    print(f"Keyframes extracted to {output_folder}")

def reverse_image_search_for_video(folder_path):
    print("Reverse image search begins....")
    rev_img_searcher = ReverseImageSearcher()
    results = []
    for image in os.listdir(folder_path):
        results.append(rev_img_searcher.search_by_file(os.path.join(folder_path, image)))
    rev=[]
    for result in results:
        if result:
            for i in range(len(result[:2])):
                res=[result[i].page_url,result[i].page_title,result[i].image_url]
                if res not in rev:
                    rev.append(res)
        else:
            print("reverse search : no results found")

    print(rev)
    print("rev search done")
    return rev

def video_reverse_search(video_path, article_url):
    path = f"temp/{uuid.uuid4().hex}"
    extract_keyframes(video_path, output_folder=path, no_of_frames=4)
    results = reverse_image_search_for_video(path)

    ages = []
    for result in results:
        date = diff_finder(article_url, result[0])
        if date > 0:
            ages.append(date)

    shutil.rmtree(path)

    return ages
