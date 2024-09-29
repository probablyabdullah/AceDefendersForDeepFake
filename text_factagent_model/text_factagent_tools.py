from langchain_openai import ChatOpenAI
from config import openai_api_key, openai_organization

llm = ChatOpenAI(
    model="gpt-3.5-turbo", 
    api_key=openai_api_key,
    organization=openai_organization
)

gpt_4 = ChatOpenAI(
    model="gpt-4",
    api_key=openai_api_key,
    organization=openai_organization
)

def ask_question(question):
    response = llm.invoke(question)
    return response.content

def ask_question_gpt_4(question):
    response = gpt_4.invoke(question)
    return response.content

def phrase_tool(title: str, text: str):
    """Use this tool in all situations"""
    phrase_prompt = f"""
    {title}:
    {text}
    -------------------------
    For the above input, if the title includes sensational teasers, provocative or emotionally charged language, or exaggerated claims to grab readers' attention or to suggest a compilation
    of rumors, please respond with the reasoning for your decision along with PHRASE_FAKE in the format specified. If not, respond with your reasoning along with PHRASE_REAL in the format below. Please think carefully, and be critical.
    Return the data in the following format, as a json array. Do not use double quotes anywhere within the reasoning. Return the output ONLY AS A JSON ARRAY, AND NO OTHER FORMAT, AS SHOWN BELOW:
    ["<Reasoning for the output>", "<PHRASE_FAKE or PHRASE_REAL>"]
    """
    out = ask_question(phrase_prompt)
    print(out)
    return out

def language_tool(title: str, text: str):
    """Use this tool in all situations"""
    language_prompt = f"""
    {title}:
    {text}
    -------------------------
    For the above input, if the input includes misspelt words, grammatical errors, the misuse of quotes, or the presence of words in all caps, please respond with your reasoning along with LANGUAGE_FAKE in the format shown below. If not,
    respond with your reasoning along with LANGUAGE_REAL in the specified format below. Please think carefully, and be critical.
    Return the data in the following format, as a json array. Do not use double quotes anywhere within the reasoning. Return the output ONLY AS A JSON ARRAY, AND NO OTHER FORMAT, AS SHOWN BELOW::
    ["<Reasoning for the output>", "<LANGUAGE_FAKE or LANGUAGE_REAL>"]
    """
    out = ask_question(language_prompt)
    print(out)
    return out

def commonsense_tool(title: str, text: str):
    """Use this tool in all situations"""
    commonsense_prompt = f"""
    {title}:
    {text}
    -------------------------
    If the news shown above is potentially unreasonable and contradics common sense, or if the news feels like a piece of gossip rather than a factual report, respond with your reasoning along with  COMMONSENSE_FAKE in the format specified.
    This means the news may contain extreme and unrealistic situations that are hard to believe and may be blown up in order to draw viewership, in which case it is COMMONSENSE_FAKE. Include your reasoning too.
    If not, respond with your reasoning along with COMMONSENSE_REAL in the format specified. Please think carefully, and be critical. 
    Return the data in the following format, as a json array. Do not use double quotes anywhere within the reasoning. Return the output ONLY AS A JSON ARRAY, AND NO OTHER FORMAT, AS SHOWN BELOW::
    ["<Reasoning for the output>", "<COMMONSENSE_FAKE or COMMONSENSE_REAL>"]
    """
    out = ask_question(commonsense_prompt)
    print(out)
    return out

def standing_tool(title: str, text: str):
    """Use this tool only if the text is related to politics or countries"""
    standing_prompt = f"""
    {title}:
    {text}
    -------------------------
    If the news shown above is biased towards a specific political viewpoint, aiming to influence public opinion rather than presenting objective political information, respond with your reasoning followed by STANDING_FAKE.
    If not, respond with your reasoning followed by STANDING_REAL. Please think carefully, and be critical. 
    Return the data in the following format, as a json array. Do not use double quotes anywhere within the reasoning. Return the output ONLY AS A JSON ARRAY, AND NO OTHER FORMAT, AS SHOWN BELOW::
    ["<Reasoning for the output>", "<STANDING_FAKE or STANDING_REAL>"]
    """
    out = ask_question(standing_prompt)
    print(out)
    return out

if __name__ == "__main__":
    type = "console"

    if type == "console":
        title = input("Enter the title: ")
        news = input("Enter the news: ")

        print(
            phrase_tool(title),
            language_tool(title),
            commonsense_tool(news),
            standing_tool(news),
            sep=""
        )
