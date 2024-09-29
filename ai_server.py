from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from typing import Dict, Any, Optional
from main import pipeline
from pprint import pprint
from ensemble import llm_call
import traceback

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
    final_ai_score: str = Field(..., description="fake or real")

@app.post("/fact-check", response_model=FactCheckResult)
async def fact_check(url_input: URLInput):
    try:
        
        fact_check_result = pipeline(url_input.url, image=url_input.image, video=url_input.video)
        
        print("check")
        ensemble_data = dict()
        p = eval(fact_check_result["text"]["phrase_tool"])
        l = eval(fact_check_result["text"]["language_tool"])
        c = eval(fact_check_result["text"]["commonsense_tool"])
        s = eval(fact_check_result["text"]["standing_tool"])
        result = FactCheckResult(
            url=url_input.url,
            text=TextAnalysis(
                phrase_tool=p[1],
                language_tool=l[1],
                commonsense_tool=c[1],
                standing_tool=s[1],
                fact_check_tool=fact_check_result["text"]["fact_check"]
            ),
            final_ai_score=""
        )
        ensemble_data["text"] = fact_check_result["text"]
        
        if "images" in fact_check_result:
            p = eval(fact_check_result["images"]["text_processing"]["phrase_tool"])
            l = eval(fact_check_result["images"]["text_processing"]["language_tool"])
            c = eval(fact_check_result["images"]["text_processing"]["standing_tool"])
            s = eval(fact_check_result["images"]["text_processing"]["commonsense_tool"])
            media_analysis = MediaAnalysis(
                deepfake_tool=fact_check_result["images"]["prediction"],
                phrase_tool=p[1],
                language_tool=l[1],
                commonsense_tool=c[1],
                standing_tool=s[1],
            )
            ensemble_data["image"] = fact_check_result["images"]
            result.image = media_analysis
        else:
            ensemble_data["image"] = dict()
            ensemble_data["image"]["text_processing"] = dict()
            ensemble_data["image"]["prediction"] = "null"
            ensemble_data["image"]["text_processing"]["commonsense_tool"] = "null"
            ensemble_data["image"]["text_processing"]["standing_tool"] = "null"
            ensemble_data["image"]["text_processing"]["fact_check"] = "null"

        
        if "videos" in fact_check_result:
            p = eval(fact_check_result["videos"]["text_processing"]["phrase_tool"])
            l = eval(fact_check_result["videos"]["text_processing"]["language_tool"])
            c = eval(fact_check_result["videos"]["text_processing"]["standing_tool"])
            s = eval(fact_check_result["videos"]["text_processing"]["commonsense_tool"])
            media_analysis = MediaAnalysis(
                deepfake_tool=fact_check_result["videos"]["prediction"],
                phrase_tool=p[1],
                language_tool=l[1],
                commonsense_tool=c[1],
                standing_tool=s[1],
            )
            ensemble_data["video"] = fact_check_result["videos"]
            result.video = media_analysis
        else:
            ensemble_data["video"] = dict()
            ensemble_data["video"]["text_processing"] = dict()
            ensemble_data["video"]["predictions"] = "null"
            ensemble_data["video"]["text_processing"]["commonsense_tool"] = "null"
            ensemble_data["video"]["text_processing"]["standing_tool"] = "null"
            ensemble_data["video"]["text_processing"]["fact_check"] = "null"
        
        # pprint(result)
        llm_result = llm_call(ensemble_data)
        print(llm_result)
        result.final_ai_score = llm_result
        print("\n\n\n\n\n", result)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="some other error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
