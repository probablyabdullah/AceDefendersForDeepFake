import pinecone
from transformers import BertTokenizer, BertModel
import numpy as np
import requests
import bs4 as BeautifulSoup
import uuid
import asyncio
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from config import pinecone_api_key

pc = Pinecone(api_key=pinecone_api_key)

# Define the index name
index_name = 'text-embedding-index'

# Create an index if it doesn't already exist
try:
    if index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=768,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1'
            ) 
        )
except:
    pass

# Connect to the index
index = pc.Index(index_name)
#fetch text
import pandas as pd
from newspaper import Article
import requests
from urllib.parse import urlparse, urlunparse
# Function to ensure the URL has a scheme
def ensure_scheme(url):
    if not isinstance(url, str):
        return None
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        if parsed_url.netloc:
            return urlunparse(('https', parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
        elif parsed_url.path:
            return 'https://' + parsed_url.path
    return url
# Function to check if the URL is working
def is_url_working(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error checking URL:  {e}")
        return False
def fetch_article_text(url):
    fixed_url = ensure_scheme(url)
    if is_url_working(fixed_url):
       try:
        article = Article(fixed_url)
        article.download()
        article.parse()
        # article.nlp()
        text = article.text
        return text
       except  Exception as e:
        print("no text retrieved:", e)
        return None
    else:
        return None
    
# Function to generate text embeddings using BERT
def get_embedding(text):
    text=text[:200]
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    inputs = tokenizer(text, return_tensors='pt')
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
    return embedding

# Placeholder function to simulate fetching the auditor score from the blockchain
async def fetch_auditor_score_from_blockchain(item_id):
    await asyncio.sleep(10)  # Simulate network delay
    # Simulate a blockchain response
    return 85  # Replace with actual blockchain call and logic

# Function to update the auditor score asynchronously
async def update_auditor_score(item_id):
    # Fetch the auditor score from the blockchain
    auditor_score = await fetch_auditor_score_from_blockchain(item_id)
    # Retrieve the current item metadata
    item = index.fetch(ids=[item_id])
    print("itemmmmm", item)
    if item and 'vectors' in item:
        print("updating...")
        vector_data = item['vectors'][item_id]
        metadata = vector_data['metadata']
        # Update the auditor score
        metadata['auditor_score'] = auditor_score
        # Upsert the updated item back into the index
        index.upsert(vectors=[(item_id, vector_data['values'], metadata)])
        print("updated!")

# Function to insert new data into the Pinecone index
def insert_data(headline, metadata):
    embedding = get_embedding(headline)
    item_id = str(uuid.uuid4())
    metadata['auditor_score'] = "NA"
    index.upsert(vectors=[(item_id, embedding, metadata)])
    return item_id

# Function to query the Pinecone index
def query_index(url):
    text = fetch_article_text(url)
    if text:
        embedding = get_embedding(text)
        try:
            results = index.query(vector=embedding.tolist(), top_k=1)
            return results
        except Exception as e:
            print(f"Error querying Pinecone index: {e}")
            return None
    return None

# Function to add new data and run model to update Pinecone
def add_data(url, metadata):
    text = fetch_article_text(url)
    if text:
        item_id = str(uuid.uuid4())
        embedding = get_embedding(text)
        metadata['full_text'] = text[:1000]  # Store first 1000 characters of full text
        metadata['auditor_score'] = "NA"
        index.upsert(vectors=[(item_id, embedding, metadata)])
        return item_id
    return None

# Function to retrieve updated data
def retrieve_data(item_id):
    item = index.fetch(ids=[item_id])
    if item and 'vectors' in item:
        return item['vectors'][item_id]['metadata']
    return None
