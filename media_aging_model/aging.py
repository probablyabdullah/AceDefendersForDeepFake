import requests
from datetime import datetime
from htmldate.core import find_date

def get_article_date(url):
    html=requests.get(url).content.decode('utf-8')
    date = find_date(html)  
    print(date)
    return date

def diff_finder(url1,url2):
    date1 = get_article_date(url1)
    date2 = get_article_date(url2)
    if not date1 or not date2:
        return -1
    date1 = datetime.strptime(date1, f"%Y-%m-%d")
    date2 = datetime.strptime(date2, f"%Y-%m-%d")

    # difference = date1 - date2 
    difference = date2 - date1
    days_difference = difference.days
    return days_difference


    
