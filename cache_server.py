from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pinecone_utils import update_auditor_score
import uvicorn
import requests
from typing import Dict, Any, Optional
import json
import traceback
from pinecone_utils import query_index, add_data, update_auditor_score, retrieve_data, fetch_article_text

app = FastAPI()

class URLInput(BaseModel):
    url: str
    image: bool = True
    video: bool = True

class TextAnalysis(BaseModel):
    phrase_tool: str = Field(..., description="fake or real")
    language_tool: str = Field(..., description="fake or real")
    commonsense_tool: str = Field(..., description="fake or real")
    standing_tool: str = Field(..., description="fake or real")
    fact_check_tool: str = Field(..., description="TRUE or FALSE or Mostly-true or Half-true or Barely-true or Pants-fire")

class MediaAnalysis(BaseModel):
    deepfake_tool: float = Field(..., ge=0, le=1)
    phrase_tool: str = Field(..., description="fake or real")
    language_tool: str = Field(..., description="fake or real")
    commonsense_tool: str = Field(..., description="fake or real")
    standing_tool: str = Field(..., description="fake or real")

class FactCheckResult(BaseModel):
    url: str
    text: TextAnalysis
    image: Optional[MediaAnalysis] = None
    video: Optional[MediaAnalysis] = None
    final_blockchain_score: Optional[int] = None
    final_ai_score: str = Field(..., description="fake or real")

@app.post("/fact-check", response_model=FactCheckResult)
async def fact_check(url_input: URLInput):
    print("entered")
    print(url_input)
    try:
        results = query_index(url_input.url)
        print("index queried")
        if results:
            print("results:", results)
            if results["matches"]:
                match = results['matches'][0]
                similarity_score = match['score']  
                threshold = 0.85  

                if similarity_score >= threshold:
                    metadata = match['metadata']
                    data = retrieve_data(match["id"]) # must make the vector db contain the data we want!
                    response = json.loads(data["metadata"])
                    response["final_blockchain_score"] = data["auditor_score"]
                    print(response)
                    return response

                else:
                    ai_dict = requests.post("http://0.0.0.0:8000/fact-check", json=dict(url_input)).json()
                    json_dict = json.dumps(ai_dict)
                    print("response", ai_dict, type(ai_dict))
                    metadata = {"url": url_input.url, "metadata": json_dict, "auditor_score": "N/A"} # change here too depending
                    item_id = add_data(url_input.url, metadata)


                    await update_auditor_score(item_id)
                    return ai_dict


            else:
                ai_dict = requests.post("http://0.0.0.0:8000/fact-check", json=dict(url_input)).json()
                json_dict = json.dumps(ai_dict)
                print("response", ai_dict, type(ai_dict))

                metadata = {"url": url_input.url, "metadata": json_dict, "auditor_score": "N/A"} # change here too depending
                item_id = add_data(url_input.url, metadata)

                await update_auditor_score(item_id)
                return ai_dict
        else:
            print("error in results")
            raise HTTPException(status_code=500, detail="Error querying the vector database")
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        raise HTTPException(status_code=500, detail="some other error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
