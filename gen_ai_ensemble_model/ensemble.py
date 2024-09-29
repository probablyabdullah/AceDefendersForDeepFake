from text_factagent_tools import ask_question_gpt_4

tools_description="""

###Tools description:

#### Text analysis Tools:

  Text Analytics output are based on tittle and the article text.
- Phrase_tool: Analyzes the language and phrasing and look for sensational teasers, provocative language, or exaggerated claims to detect signs of fake news.
- Language_tool: Evaluates the overall language quality and coherence to identify inconsistencies in article.
- Commonsense_tool: Applies common sense reasoning to the article title and text to check for logical inconsistencies.
- Standing_tool: standing tool analyzes political statements and determines whether it is politically biased.
- Fact_check_tool: Check if the claim made in title are already verified by reliable fact cheking sources and gives output as True, \
                     Mostly-True, Half-True, Barely-True,False,Pants-Fire(claims not only false but also reidiculous), No Claim Found.

####Image analysis Tools:

  Image analytics outputs are based on the textual description
- Image_commonsense_tool: Applies common sense reasoning to the image description to check for logical inconsistencies.
- Image_standing_tool: standing tool analyzes political statements in image description and determines whether it is politically biased.
- Image_fact_check_tool: Check if the claims found in image description are already verified by reliable fact cheking sources

#### Video analysis Tools:

  Video analytics outputs are based on the textual description of vedio except deepfake tool
- video_deepfake_tool: Detects whether the video associated with the article have been manipulated or are deepfakes.score more closer to 1 indicates the media is a deepfake or manipulated.
- video_commonsense_tool: Applies common sense reasoning to the video description to check for logical inconsistencies
- video_standing_tool: standing tool analyzes political statements in video description and determines whether it is politically biased.
- video_fact_check_tool:  Check if the claims found in video description are already verified by reliable fact cheking sources"""

import openai
def generate_prompt(fact_check_result):
    prompt = f"""
You are an intelligent Fake News Detector, your job is to classify the article as FAKE or REAL using the outputs text,vedio and image analytics tools on article.


-------------------------------------------------------------------

{tools_description}

--------------------------------------------------------------------

### Below are the outputs of the individual tools :

#### Text analysis Tools:
    - Phrase_tool: {fact_check_result["text"]["phrase_tool"]}
    - Language_tool: {fact_check_result["text"]["language_tool"]}
    - Commonsense_tool: {fact_check_result["text"]["commonsense_tool"]}
    - Standing_tool: {fact_check_result["text"]["standing_tool"]}
    - Fact_check_tool: {fact_check_result["text"]["fact_check"]}


#### Image analysis Tools:
    - Image_deepfake_tool: {fact_check_result["image"]["prediction"]}
    - Image_commonsense_tool: {fact_check_result["image"]["text_processing"]["commonsense_tool"]}
    - Image_standing_tool: {fact_check_result["image"]["text_processing"]["standing_tool"]}
    - Image_fact_check_tool: {fact_check_result["image"]["text_processing"]["fact_check"]}


#### Video analysis Tools:
    -video_deepfake_tool: {fact_check_result["video"]["predictions"]}
    -video_commonsense_tool: {fact_check_result["video"]["text_processing"]["commonsense_tool"]}
    -video_standing_tool: {fact_check_result["video"]["text_processing"]["standing_tool"]}
    -video_fact_check_tool: {fact_check_result["video"]["text_processing"]["fact_check"]}



### INSTRUCTIONS:
1. Utilize provided tool outputs effectively to determine if the article is REAL or FAKE.
2. Ignore any null values from individual tools while making your decision.
3. Return only the word 'REAL' or 'FAKE' as output.

RETURN ONLY THE WORD 'REAL' or 'FAKE' as output.
"""

    return prompt

def llm_call(data):

    prompt = generate_prompt(data)
    print(prompt)
    return ask_question_gpt_4(prompt)
