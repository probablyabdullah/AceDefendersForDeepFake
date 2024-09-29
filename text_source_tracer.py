from serpapi import GoogleSearch
from text_factagent_tools import ask_question
from config import serpapi_api_key


def summarize_text(text):
    prompt = f"""
    {text}
    -----
    Summarize the above text. Include only the keywords optimized for searching on a search engine. Include the keywords as comma separated text. 
    Include only the top 5 entities. Only follow the instructions, do not include any formatting.
    """
    print("prompt:", prompt)
    return ask_question(prompt)

def search_google(query):
    params = {
    "api_key": serpapi_api_key,
    "engine": "google",
    "q": query,
    "google_domain": "google.com",
    "gl": "us",
    "hl": "en",
    "tbm": "nws",
    "num": "10"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if "news_results" not in results:
        return None
    res=[]
    for i in results['news_results']:
        print(i['link'])    
        res.append(i['link'])
    return res
    
def revtextsearch(news_text):
    summary = summarize_text(news_text)
    print("Summary:", summary)

    search_results = search_google(summary)
    if search_results is None:
        return []
    print("Top 5 Google Search Results:")
    for i in search_results:
        print(i)
    return search_results
        
