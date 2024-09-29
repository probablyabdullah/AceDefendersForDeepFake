import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os

class Article:
    def __init__(self, url):
        self.url = url
        self.parse_article()

    def parse_article(self):
        # Send a GET request to the URL
        response = requests.get(self.url)
        
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract article heading
        heading = soup.find('h1').text.strip() if soup.find('h1') else 'Heading not found'
        
        # Article URL is the input URL
        article_url = self.url
        
        # Extract publish date (this might vary depending on the website structure)
        publish_date = None
        date_meta = soup.find('meta', property='article:published_time')
        if date_meta:
            publish_date = datetime.fromisoformat(date_meta['content'].split('T')[0])
        else:
            # Try to find a date in a common format (adjust as needed)
            date_element = soup.find('time')
            if date_element and date_element.has_attr('datetime'):
                publish_date = datetime.fromisoformat(date_element['datetime'].split('T')[0])
        
        # Extract all images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_src = urljoin(self.url, src)
                if not os.path.splitext(urlparse(full_src).path)[1].lower() == '.gif':
                    images.append(full_src)
        
        # Extract all videos
        videos = []
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                full_src = urljoin(self.url, src)
                videos.append(full_src)
        
        # Also check for iframe embedded videos (e.g., YouTube)
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            # if src and ('youtube.com' in src or 'vimeo.com' in src):
            if src and ('youtu' in src):
                videos.append(src)
        
        # Extract article text
        article_text = ""
        # Look for common article container elements
        article_containers = soup.find_all(['article', 'div'], class_=['article-body', 'entry-content', 'post-content'])
        if article_containers:
            for container in article_containers:
                paragraphs = container.find_all('p')
                article_text += ' '.join([p.text for p in paragraphs])
        else:
            # If no specific article container is found, try to get all paragraphs
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.text for p in paragraphs])
        
        # Clean up the text
        article_text = ' '.join(article_text.split())
        
        # return {
        #     'heading': heading,
        #     'url': article_url,
        #     'publish_date': publish_date,
        #     'images': images,
        #     'videos': videos,
        #     'text': article_text
        # }
        self.title = heading
        self.publish_date = publish_date
        self.images = images
        self.videos = videos
        self.text = article_text

if __name__ == "__main__":
    # # Example usage
    article_url = 'https://www.thisisanfield.com/2024/07/2-former-liverpool-players-are-making-identical-transfer-to-cesc-fabregas-club/'
    # article_data = parse_article(article_url)
    article = Article(article_url)

    print(f"Heading: {article.title}")
    print(f"URL: {article.url}")
    print(f"Publish Date: {article.publish_date}")
    print(f"Images: {article.images}")
    print(f"Videos: {article.videos}")
    print(f"Article Text: {article.text}") 
