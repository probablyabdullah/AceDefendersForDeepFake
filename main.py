import concurrent.futures
from text_factagent_tools import *
from text_source_tracer import *
from text_fact_checker import *
from aging import diff_finder
from util import download_image, download_youtube_video
from image_deepfake_detection import predict
from image_reverse_search import reverse_image_search
from video_deepfake_detector import video_deepfake_detector
from video_reverse_search import video_reverse_search
from media_description_tool import process_video_and_generate_content
import os
from article_parser import Article
import re

def pipeline(url, image: bool, video: bool):
    results = dict()
    article = Article(url)
    text = re.sub("\s+", " ", article.text).strip()
    results["text"] = text_pipeline(article.title, text, url)
    print(article.images)
    if image == True and article.images != []:
        try:
            results["images"] = image_pipeline(article.images[:5], url)[0]
        except:
            pass
    if video == True and article.videos != []:
        try:
            results["videos"] = image_pipeline(article.videos[:1], url)[0]
        except:
            pass
    
    print("Text:----------------", results["text"], "\n\n\n")
    if "images" in results:
        print("Images:----------------", results["images"], "\n\n\n")
    if "videos" in results:
        print("Videos:----------------", results["videos"], "\n\n\n")

    # return 0.69
    # have to change code in cache to accomodate this
    return results



def text_pipeline(title, text, article_url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as exe:
        p = exe.submit(phrase_tool, title, text)
        l = exe.submit(language_tool, title, text)
        c = exe.submit(commonsense_tool, title, text)
        s = exe.submit(standing_tool, title, text)
        urls = exe.submit(revtextsearch, text)
        t = exe.submit(fact_check, title)
    
    ages = []
    # if urls.result() is not []:
    for url in urls.result():
        try:
            ages.append(diff_finder(url, article_url))
        except:
            continue


    return {
        "phrase_tool": p.result(),
        "language_tool": l.result(),
        "commonsense_tool": c.result(),
        "standing_tool": s.result(),
        "reverse_search_ages": ages,
        "fact_check": t.result()
    }

def image_pipeline(urls, article_url):
    article_urls = [article_url for _ in urls]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as exe:
        result = exe.map(process_image, urls, article_urls)

    result = list(result)

    for i in range(len(result)):
        if result[i] is not None:
            result[i]["text_processing"] = text_pipeline(result[i]["description"], result[i]["description"], article_url)

    result = [i for i in result if i is not None]
    return result

def process_image(url, article_url):
    try:
        path, img_data = download_image(url)
    except Exception as e:
        print(e)
        return None
    
    predictions, _, _ = predict(img_data, "real")
    if predictions is None:
        print("predictions NONEEEE")
        return None
    try:
        description = process_video_and_generate_content(path, "image")
        print(description)
    except Exception as e:
        print(e)
        return None

    try:
        ages = reverse_image_search(path, article_url)
    except Exception as e:
        print(e)
        return None

    os.remove(path)
    return {
        "prediction": predictions["fake"],
        "description": description,
        "ages": ages
    }

def video_pipeline(urls, article_url):
    # print("article_url", article_url)
    article_urls = [article_url for _ in urls]
    print("processing video...")
    print(urls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as exe:
        result = exe.map(process_video, urls, article_urls)
    
    result = list(result)
    # print(result)

    for i in range(len(result)):
        if result is not None:
            result[i]["text_processing"] = text_pipeline(result[i]["description"], result[i]["description"], article_url)

    result = [i for i in result if i is not None]
    return result

def process_video(url, article_url):
    print("article_url", article_url)
    
    try:
        path = download_youtube_video(url)
    except Exception as e:
        print(e)
        return None

    try:
        predictions = video_deepfake_detector(path)
        description = process_video_and_generate_content(path, "video")
        print(description)
        ages = video_reverse_search(path, article_url)
    except Exception as e:
        print(e)
        return None

    os.remove(path)
    return {
        "predictions": predictions["fake"],
        "description": description,
        "ages": ages
    }

if __name__ == "__main__": 
    url = input("Enter a url: ")
    article = Article(url)

    # text_result = text_pipeline(article.title, article.text, url)
    image_result = image_pipeline(article.images[:4], url)
    # video_result = video_pipeline(article.videos, url)

    # print(f"Text result:\n{text_result}\n\n\n")
    print(f"Image result:\n{image_result}\n\n\n")
    print(article.images[:4])
    # print(f"Video result:\n{video_result}\n\n\n")
