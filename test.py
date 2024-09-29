import pandas as pd 
# import numpy as np
from main import text_pipeline, image_pipeline, video_pipeline
import re
from ensemble import llm_call

df = pd.read_excel("/home/capemox/Downloads/dataset_end_to_end.xlsx", sheet_name="Sheet1")
out_df = pd.DataFrame()

for i in range(len(df)):
    row = dict()
    results = dict()
    url = df.news_url[i]
    if not url.startswith("http"):
        url = "http://" + url
    try:
        text = re.sub("\s+", " ", df.text[i]).strip()
    except:
        continue
    results["text"] = text_pipeline(df.title[i], text, url)
    # results.append(text_result)
    if not pd.isna(df.top_image_url[i]):
        try:
            results["image"] = image_pipeline([df.top_image_url[i]], url)[0]
        except:
            pass
    if not pd.isna(df.video_url[i]):
        try:
            print("VIDEO PIPELINE\n\n\n\n\n\n\n\n")
            results["video"] = video_pipeline([df.video_url[i]], url)[0]
        except Exception as e:
            print(e)
    
    actual_class = df["class"][i]
    # print(results["text"], '\n\n\n')
    # print(results["image"], '\n\n\n')
    # print(results["video"], '\n\n\n')
    # break
    p = eval(results["text"]["phrase_tool"])
    l = eval(results["text"]["language_tool"])
    c = eval(results["text"]["commonsense_tool"])
    s = eval(results["text"]["standing_tool"])

    row["url"] = df.news_url[i]
    row["news_title"] = df.title[i]
    row["news_text"] = text

    if not pd.isna(df.top_image_url[i]):
        row["image_url"] = df.top_image_url[i]
    else:
        row["image_url"] = ""

    if not pd.isna(df.video_url[i]):
        row["video_url"] = df.top_image_url[i]
    else:
        row["video_url"] = ""

    row["phrase_tool"] = p[1]
    row["language_tool"] = l[1]
    row["commonsense_tool"] = c[1]
    row["standing_tool"] = s[1]
    row["phrase_tool_reasoning"] = p[0]
    row["language_tool_reasoning"] = l[0]
    row["commonsense_tool_reasoning"] = c[0]
    row["standing_tool_reasoning"] = s[0]
    row["aging"] = results["text"]["reverse_search_ages"]
    row["fact_check"] = results["text"]["fact_check"]

    if "image" in results and results["image"] != []:
        # p = eval(results["text"]["phrase_tool"])
        # l = eval(results["text"]["language_tool"])
        # c = eval(results["text"]["commonsense_tool"])
        # s = eval(results["text"]["standing_tool"])
        row["image_prediction"] = results["image"]["prediction"]
        row["image_description"] = results["image"]["description"]
        p = eval(results["image"]["text_processing"]["phrase_tool"])
        l = eval(results["image"]["text_processing"]["language_tool"])
        c = eval(results["image"]["text_processing"]["commonsense_tool"])
        s = eval(results["image"]["text_processing"]["standing_tool"])
        row["image_phrase_tool"] = p[1]
        row["image_language_tool"] = l[1]
        row["image_commonsense_tool"] = c[1]
        row["image_standing_tool"] = s[1]
        row["image_phrase_tool_reasoning"] = p[0]
        row["image_language_tool_reasoning"] = l[0]
        row["image_commonsense_tool_reasoning"] = c[0]
        row["image_standing_tool_reasoning"] = s[0]
        row["image_image_aging"] = results["image"]["ages"]
        row["image_image_fact_check"] = results["image"]["text_processing"]["fact_check"]
    else:
        results["image"] = dict()
        results["image"]["text_processing"] = dict()
        results["image"]["prediction"] = "null"
        results["image"]["text_processing"]["commonsense_tool"] = "null"
        results["image"]["text_processing"]["standing_tool"] = "null"
        results["image"]["text_processing"]["fact_check"] = "null"
        row["image_prediction"] = "null"
        row["image_description"] = "null"
        row["image_phrase_tool"] = "null"
        row["image_language_tool"] = "null"
        row["image_commonsense_tool"] = "null"
        row["image_standing_tool"] = "null"
        row["image_phrase_tool_reasoning"] = "null"
        row["image_language_tool_reasoning"] = "null"
        row["image_commonsense_tool_reasoning"] = "null"
        row["image_standing_tool_reasoning"] = "null"
        row["image_aging"] = "null"
        row["image_fact_check"] = "null"

    if "video" in results and results["video"] != []:
        row["video_prediction"] = results["video"]["predictions"]
        row["video_description"] = results["video"]["description"]
        p = eval(results["video"]["text_processing"]["phrase_tool"])
        l = eval(results["video"]["text_processing"]["language_tool"])
        c = eval(results["video"]["text_processing"]["commonsense_tool"])
        s = eval(results["video"]["text_processing"]["standing_tool"])
        row["video_phrase_tool"] = p[1]
        row["video_language_tool"] = l[1]
        row["video_commonsense_tool"] = c[1]
        row["video_standing_tool"] = s[1]
        row["video_phrase_tool_reasoning"] = p[0]
        row["video_language_tool_reasoning"] = l[0]
        row["image_commonsense_tool_reasoning"] = c[0]
        row["video_standing_tool_reasoning"] = s[0]
        row["video_image_aging"] = results["video"]["ages"]
        # row["video_phrase_tool"] = results["video"]["text_processing"]["phrase_tool"]
        # row["video_language_tool"] = results["video"]["text_processing"]["language_tool"]
        # row["video_commonsense_tool"] = results["video"]["text_processing"]["commonsense_tool"]
        # row["video_standing_tool"] = results["video"]["text_processing"]["standing_tool"]
        row["video_aging"] = results["video"]["ages"]
        row["video_fact_check"] = results["video"]["text_processing"]["fact_check"]
    else:
        results["video"] = dict()
        results["video"]["text_processing"] = dict()
        results["video"]["predictions"] = "null"
        results["video"]["text_processing"]["commonsense_tool"] = "null"
        results["video"]["text_processing"]["standing_tool"] = "null"
        results["video"]["text_processing"]["fact_check"] = "null"
        row["video_prediction"] = "null"
        row["video_description"] = "null"
        row["video_phrase_tool"] = "null"
        row["video_language_tool"] = "null"
        row["video_commonsense_tool"] = "null"
        row["video_standing_tool"] = "null"
        row["video_phrase_tool_reasoning"] = "null"
        row["video_language_tool_reasoning"] = "null"
        row["image_commonsense_tool_reasoning"] = "null"
        row["video_standing_tool_reasoning"] = "null"
        row["video_aging"] = "null"
        row["video_fact_check"] = "null"

    row["actual_class"] = actual_class
    row["predicted_class"] = llm_call(results)
    out_df = out_df._append(row, ignore_index=True, sort=False)
    # out_df[len(out_df)] = row
    out_df.to_csv("output_final.csv")

