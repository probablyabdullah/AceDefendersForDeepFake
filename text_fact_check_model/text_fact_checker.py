import time
import pprint
import google.generativeai as genai
import requests
from collections import Counter
from config import google_api_key, fact_check_api_key

genai.configure(api_key=google_api_key)
few_shot_examples = [
    {
        "query": "Final election 2016 numbers: Trump won the popular vote.",
        "claim": "President Donald Trump won the 2020 election",
        "similar": False
    },
    {
        "query": "Final election 2016 numbers: Trump won the popular vote.",
        "claim": "Final election 2016 numbers: Trump won the popular vote.",
        "similar": True
    },
    {
        "query": "Vaccines are safe.",
        "claim": "Vaccines can cause side effects.",
        "similar": False
    },
    {
        "query": "Vaccines are safe.",
        "claim": "Vaccines are generally safe for the public.",
        "similar": True
    }
]
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

def create_prompt(query, claim):
    prompt = f"""
    Based on the following examples:

    {few_shot_examples}

    Please determine if the following query and claim are similar.give only boolean value as output.

    Query: "{query}"
    Claim: "{claim}"

    Response:
    """
    return prompt.strip()


def is_claim_similar_to_query(query, claim):
    # Create the prompt with few-shot examples
    model = genai.GenerativeModel(model_name='models/gemini-1.0-pro')
   
    prompt = create_prompt(query,claim)
    
    response = model.generate_content([prompt], safety_settings=safety_settings)
    
    print(response.text)
    return "True" in response.text

def fact_check(query):
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={fact_check_api_key}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        claims = data.get('claims', [])
        
        if not claims:
            return 'No claim found'
        
        filtered_results = []
        for claim in claims:
            text = claim.get('text', 'No text found')
            
            if is_claim_similar_to_query(query, text):
                print(text)
                rating = claim.get('claimReview', [{}])[0].get('textualRating', 'No rating found')
                filtered_results.append(rating)
        
        if not filtered_results:
            return 'No claim found'
        
        # Calculate the most frequent rating
        rating_counts = Counter(filtered_results)
        most_common_rating = rating_counts.most_common(1)[0][0]
        
        return most_common_rating
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return 'No claim found'

if __name__ == "__main__":
    query = 'Superdelegates have never been a determining factor in who our nominee is since theyve been in place since 1984.'
    print(fact_check(query))
